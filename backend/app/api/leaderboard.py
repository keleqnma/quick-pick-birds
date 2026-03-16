"""
排行榜和成就系统 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db import database

router = APIRouter()


# ==================== 成就定义 ====================

ACHIEVEMENTS = {
    "first_bird": {
        "name": "初次观鸟",
        "description": "记录第一次观鸟活动",
        "icon": "🐦",
        "category": "新手"
    },
    "species_10": {
        "name": "入门观鸟者",
        "description": "累计观测 10 种鸟类",
        "icon": "🏅",
        "category": "成就"
    },
    "species_50": {
        "name": "资深观鸟者",
        "description": "累计观测 50 种鸟类",
        "icon": "🌟",
        "category": "成就"
    },
    "species_100": {
        "name": "鸟类专家",
        "description": "累计观测 100 种鸟类",
        "icon": "👑",
        "category": "成就"
    },
    "photos_100": {
        "name": "勤奋拍摄",
        "description": "累计拍摄 100 张照片",
        "icon": "📷",
        "category": "拍摄"
    },
    "photos_1000": {
        "name": "摄影师",
        "description": "累计拍摄 1000 张照片",
        "icon": "📸",
        "category": "拍摄"
    },
    "days_10": {
        "name": "坚持观测",
        "description": "累计 10 天观鸟活动",
        "icon": "📅",
        "category": "坚持"
    },
    "days_50": {
        "name": "忠实观鸟者",
        "description": "累计 50 天观鸟活动",
        "icon": "🗓️",
        "category": "坚持"
    },
    "perfect_day": {
        "name": "完美的一天",
        "description": "单日观测到 10 种以上鸟类",
        "icon": "⭐",
        "category": "特殊"
    },
    "rare_bird": {
        "name": "稀有发现",
        "description": "观测到国家重点保护鸟类",
        "icon": "💎",
        "category": "特殊"
    },
    "year_report": {
        "name": "年度报告",
        "description": "完成一份完整的年度报告",
        "icon": "📊",
        "category": "报告"
    },
    "checklist_master": {
        "name": "清单大师",
        "description": "创建 20 份观测清单",
        "icon": "✅",
        "category": "清单"
    }
}


@router.get("/leaderboard/species")
async def get_species_leaderboard(
    limit: int = Query(10, description="返回前 N 名", le=50)
):
    """
    获取物种数量排行榜
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 按会话统计物种数量
    c.execute("""
        SELECT os.id, os.location_name, os.scan_date,
               COUNT(DISTINCT bd.species_cn) as species_count,
               COUNT(p.id) as photo_count
        FROM observation_sessions os
        LEFT JOIN photos p ON os.id = p.session_id
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE bd.species_cn IS NOT NULL AND bd.species_cn != ''
        GROUP BY os.id
        ORDER BY species_count DESC
        LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    result = []
    for idx, row in enumerate(rows, 1):
        result.append({
            "rank": idx,
            "session_id": row[0],
            "location": row[1] or "未知",
            "date": row[2],
            "species_count": row[3],
            "photo_count": row[4]
        })

    return {"leaderboard": result}


@router.get("/leaderboard/photos")
async def get_photos_leaderboard(
    limit: int = Query(10, description="返回前 N 名", le=50)
):
    """
    获取照片数量排行榜（按观测地点）
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 按地点统计
    c.execute("""
        SELECT os.location_name,
               COUNT(p.id) as photo_count,
               COUNT(DISTINCT bd.species_cn) as species_count,
               COUNT(DISTINCT DATE(p.capture_time)) as days
        FROM observation_sessions os
        LEFT JOIN photos p ON os.id = p.session_id
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE os.location_name IS NOT NULL AND os.location_name != ''
        GROUP BY os.location_name
        ORDER BY photo_count DESC
        LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    result = []
    for idx, row in enumerate(rows, 1):
        result.append({
            "rank": idx,
            "location": row[0] or "未知",
            "photo_count": row[1],
            "species_count": row[2],
            "observation_days": row[3]
        })

    return {"leaderboard": result}


@router.get("/leaderboard/locations")
async def get_locations_leaderboard(
    limit: int = Query(10, description="返回前 N 名", le=50)
):
    """
    获取热门观测地点排行榜
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 按 GPS 位置聚类
    c.execute("""
        SELECT ROUND(gps_lat, 2) as lat, ROUND(gps_lng, 2) as lng,
               COUNT(*) as visit_count,
               COUNT(DISTINCT DATE(capture_time)) as unique_days,
               COUNT(DISTINCT species_cn) as species_count
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE gps_lat IS NOT NULL AND gps_lng IS NOT NULL
        GROUP BY ROUND(gps_lat, 2), ROUND(gps_lng, 2)
        ORDER BY unique_days DESC
        LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    result = []
    for idx, row in enumerate(rows, 1):
        result.append({
            "rank": idx,
            "lat": row[0],
            "lng": row[1],
            "visit_count": row[2],
            "unique_days": row[3],
            "species_count": row[4]
        })

    return {"leaderboard": result}


@router.get("/achievements")
async def get_achievements():
    """
    获取所有可用的成就列表
    """
    return {"achievements": ACHIEVEMENTS}


@router.get("/achievements/check")
async def check_achievements():
    """
    检查当前已完成的成就
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 统计数据
    c.execute("SELECT COUNT(DISTINCT species_cn) FROM bird_detections WHERE species_cn IS NOT NULL")
    total_species = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM photos")
    total_photos = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(DISTINCT DATE(capture_time)) FROM photos")
    total_days = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM checklists")
    total_checklists = c.fetchone()[0] or 0

    # 单日最高物种数
    c.execute("""
        SELECT COUNT(DISTINCT bd.species_cn) as count
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        GROUP BY DATE(p.capture_time)
        ORDER BY count DESC
        LIMIT 1
    """)
    best_day_species = c.fetchone()[0] or 0

    # 检查是否有保护鸟类
    c.execute("""
        SELECT COUNT(*) FROM bird_detections
        WHERE species_cn IN (
            SELECT species_cn FROM bird_species
            WHERE conservation_level IS NOT NULL
        )
    """)
    protected_species_count = c.fetchone()[0] or 0

    conn.close()

    # 检查成就完成状态
    unlocked = []

    # 初次观鸟
    if total_days >= 1:
        unlocked.append("first_bird")

    # 物种成就
    if total_species >= 10:
        unlocked.append("species_10")
    if total_species >= 50:
        unlocked.append("species_50")
    if total_species >= 100:
        unlocked.append("species_100")

    # 照片成就
    if total_photos >= 100:
        unlocked.append("photos_100")
    if total_photos >= 1000:
        unlocked.append("photos_1000")

    # 坚持成就
    if total_days >= 10:
        unlocked.append("days_10")
    if total_days >= 50:
        unlocked.append("days_50")

    # 特殊成就
    if best_day_species >= 10:
        unlocked.append("perfect_day")
    if protected_species_count > 0:
        unlocked.append("rare_bird")

    # 清单成就
    if total_checklists >= 20:
        unlocked.append("checklist_master")

    # 构建完整成就列表
    all_achievements = []
    for key, achievement in ACHIEVEMENTS.items():
        all_achievements.append({
            "id": key,
            "name": achievement["name"],
            "description": achievement["description"],
            "icon": achievement["icon"],
            "category": achievement["category"],
            "unlocked": key in unlocked
        })

    # 按完成状态排序（未完成的在前）
    all_achievements.sort(key=lambda x: (x["unlocked"], x["category"]))

    progress = len(unlocked) / len(ACHIEVEMENTS) * 100

    return {
        "achievements": all_achievements,
        "unlocked_count": len(unlocked),
        "total_count": len(ACHIEVEMENTS),
        "progress": round(progress, 1)
    }


@router.get("/achievements/stats")
async def get_achievement_stats():
    """
    获取成就进度统计
    """
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(DISTINCT species_cn) FROM bird_detections WHERE species_cn IS NOT NULL")
    total_species = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM photos")
    total_photos = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(DISTINCT DATE(capture_time)) FROM photos")
    total_days = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM checklists")
    total_checklists = c.fetchone()[0] or 0

    c.execute("""
        SELECT COUNT(DISTINCT bd.species_cn) as count
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        GROUP BY DATE(p.capture_time)
        ORDER BY count DESC
        LIMIT 1
    """)
    best_day_species = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_species": total_species,
        "total_photos": total_photos,
        "total_observation_days": total_days,
        "total_checklists": total_checklists,
        "best_day_species_count": best_day_species,
        "next_milestones": [
            {"name": "物种数", "current": total_species, "next": 10 if total_species < 10 else (50 if total_species < 50 else (100 if total_species < 100 else None))},
            {"name": "照片数", "current": total_photos, "next": 100 if total_photos < 100 else (1000 if total_photos < 1000 else None)},
            {"name": "观测天数", "current": total_days, "next": 10 if total_days < 10 else (50 if total_days < 50 else None)},
            {"name": "观测清单", "current": total_checklists, "next": 20 if total_checklists < 20 else None}
        ]
    }
