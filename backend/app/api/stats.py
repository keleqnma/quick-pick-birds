"""
统计图表 API - 提供数据可视化所需的统计接口
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from app.db import database

router = APIRouter()


@router.get("/species-distribution")
async def get_species_distribution(
    year: Optional[int] = Query(None, description="年份，为空则统计所有年份"),
    session_id: Optional[int] = Query(None, description="会话 ID，优先于年份参数")
):
    """
    获取物种分布数据（用于饼图）

    返回每种鸟类的出现次数和比例
    """
    conn = database.get_connection()
    c = conn.cursor()

    if session_id:
        # 按会话统计
        c.execute("""
            SELECT bd.species_cn, bd.species_en, bd.scientific_name, COUNT(*) as count
            FROM bird_detections bd
            JOIN photos p ON bd.photo_id = p.id
            WHERE p.session_id = ?
            GROUP BY bd.species_cn, bd.species_en, bd.scientific_name
            ORDER BY count DESC
        """, (session_id,))
    elif year:
        # 按年份统计
        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"
        c.execute("""
            SELECT bd.species_cn, bd.species_en, bd.scientific_name, COUNT(*) as count
            FROM bird_detections bd
            JOIN photos p ON bd.photo_id = p.id
            WHERE p.capture_time >= ? AND p.capture_time < ?
            GROUP BY bd.species_cn, bd.species_en, bd.scientific_name
            ORDER BY count DESC
        """, (start_date, end_date))
    else:
        # 统计所有
        c.execute("""
            SELECT bd.species_cn, bd.species_en, bd.scientific_name, COUNT(*) as count
            FROM bird_detections bd
            GROUP BY bd.species_cn, bd.species_en, bd.scientific_name
            ORDER BY count DESC
        """)

    rows = c.fetchall()
    conn.close()

    total = sum(row[3] for row in rows)

    result = []
    for row in rows:
        result.append({
            "species_cn": row[0] or "未知",
            "species_en": row[1] or "",
            "scientific_name": row[2] or "",
            "count": row[3],
            "percentage": round(row[3] / total * 100, 2) if total > 0 else 0
        })

    return {
        "total_detections": total,
        "unique_species": len(result),
        "data": result
    }


@router.get("/monthly-trend")
async def get_monthly_trend(
    year: int = Query(..., description="年份")
):
    """
    获取月度观测趋势数据（用于柱状图/折线图）

    返回每个月的照片数、物种数、观测天数
    """
    conn = database.get_connection()
    c = conn.cursor()

    start_date = f"{year}-01-01"
    end_date = f"{year + 1}-01-01"

    # 按月统计
    c.execute("""
        SELECT
            strftime('%m', p.capture_time) as month,
            COUNT(DISTINCT p.id) as photo_count,
            COUNT(DISTINCT bd.species_cn) as species_count,
            COUNT(DISTINCT DATE(p.capture_time)) as observation_days
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE p.capture_time >= ? AND p.capture_time < ?
        GROUP BY strftime('%m', p.capture_time)
        ORDER BY month
    """, (start_date, end_date))

    rows = c.fetchall()
    conn.close()

    # 构建完整的月份数据（1-12 月）
    month_data = {str(i).zfill(2): {"month": str(i).zfill(2), "photo_count": 0, "species_count": 0, "observation_days": 0} for i in range(1, 13)}

    for row in rows:
        month = row[0]
        if month in month_data:
            month_data[month]["photo_count"] = row[1]
            month_data[month]["species_count"] = row[2]
            month_data[month]["observation_days"] = row[3]

    return {
        "year": year,
        "data": list(month_data.values())
    }


@router.get("/daily-activity")
async def get_daily_activity(
    year: Optional[int] = Query(None, description="年份"),
    month: Optional[int] = Query(None, description="月份")
):
    """
    获取每日活动热力图数据

    返回每天的观测数据，用于日历热力图
    """
    conn = database.get_connection()
    c = conn.cursor()

    if year and month:
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
    elif year:
        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"
    else:
        # 默认最近 30 天
        c.execute("""
            SELECT DATE(MAX(capture_time)) FROM photos
        """)
        max_date = c.fetchone()[0]
        if not max_date:
            conn.close()
            return {"data": []}

        # 计算 30 天前的日期
        from datetime import datetime, timedelta
        max_dt = datetime.fromisoformat(max_date)
        start_dt = max_dt - timedelta(days=30)
        start_date = start_dt.strftime("%Y-%m-%d")
        end_date = (max_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    c.execute("""
        SELECT
            DATE(capture_time) as date,
            COUNT(DISTINCT p.id) as photo_count,
            COUNT(DISTINCT bd.species_cn) as species_count
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE p.capture_time >= ? AND p.capture_time < ?
        GROUP BY DATE(capture_time)
        ORDER BY date
    """, (start_date, end_date))

    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "date": row[0],
            "photo_count": row[1],
            "species_count": row[2]
        })

    return {
        "start_date": start_date,
        "end_date": end_date,
        "data": result
    }


@router.get("/location-frequency")
async def get_location_frequency():
    """
    获取观测地点频率数据（用于条形图）

    按 GPS 位置聚类统计观测频次
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 按大致位置分组（经纬度保留 1 位小数）
    c.execute("""
        SELECT
            ROUND(gps_lat, 1) as lat_group,
            ROUND(gps_lng, 1) as lng_group,
            COUNT(*) as photo_count,
            COUNT(DISTINCT species_cn) as species_count,
            GROUP_CONCAT(DISTINCT species_cn) as species_list
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE p.gps_lat IS NOT NULL AND p.gps_lng IS NOT NULL
        GROUP BY lat_group, lng_group
        ORDER BY photo_count DESC
        LIMIT 20
    """)

    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "lat": row[0],
            "lng": row[1],
            "photo_count": row[2],
            "species_count": row[3],
            "species_list": row[4] or ""
        })

    return {
        "total_locations": len(result),
        "data": result
    }


@router.get("/top-species")
async def get_top_species(
    limit: int = Query(10, description="返回前 N 个物种", le=50)
):
    """
    获取最频繁观测的物种（用于排行榜）
    """
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            bd.species_cn,
            bd.species_en,
            bd.scientific_name,
            COUNT(*) as count,
            COUNT(DISTINCT DATE(p.capture_time)) as observation_days,
            GROUP_CONCAT(DISTINCT DATE(p.capture_time)) as dates
        FROM bird_detections bd
        JOIN photos p ON bd.photo_id = p.id
        GROUP BY bd.species_cn, bd.species_en, bd.scientific_name
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        dates = row[5].split(",") if row[5] else []
        result.append({
            "species_cn": row[0] or "未知",
            "species_en": row[1] or "",
            "scientific_name": row[2] or "",
            "count": row[3],
            "observation_days": row[4],
            "first_seen": min(dates) if dates else None,
            "last_seen": max(dates) if dates else None
        })

    return result


@router.get("/camera-stats")
async def get_camera_stats(
    year: Optional[int] = Query(None, description="年份")
):
    """
    获取相机使用统计
    """
    conn = database.get_connection()
    c = conn.cursor()

    if year:
        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"
        c.execute("""
            SELECT
                camera_model,
                COUNT(*) as photo_count,
                COUNT(DISTINCT DATE(capture_time)) as observation_days
            FROM photos
            WHERE camera_model IS NOT NULL AND capture_time >= ? AND capture_time < ?
            GROUP BY camera_model
            ORDER BY photo_count DESC
            LIMIT 10
        """, (start_date, end_date))
    else:
        c.execute("""
            SELECT
                camera_model,
                COUNT(*) as photo_count,
                COUNT(DISTINCT DATE(capture_time)) as observation_days
            FROM photos
            WHERE camera_model IS NOT NULL
            GROUP BY camera_model
            ORDER BY photo_count DESC
            LIMIT 10
        """)

    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "camera_model": row[0] or "未知",
            "photo_count": row[1],
            "observation_days": row[2]
        })

    return {
        "data": result
    }


@router.get("/overview")
async def get_overview():
    """
    获取总体统计数据（用于仪表盘）
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 总照片数
    c.execute("SELECT COUNT(*) FROM photos")
    total_photos = c.fetchone()[0]

    # 总物种数
    c.execute("SELECT COUNT(DISTINCT species_cn) FROM bird_detections WHERE species_cn IS NOT NULL")
    total_species = c.fetchone()[0]

    # 总观测天数
    c.execute("SELECT COUNT(DISTINCT DATE(capture_time)) FROM photos")
    observation_days = c.fetchone()[0]

    # 推荐照片数
    c.execute("SELECT COUNT(*) FROM photos WHERE is_recommended = 1")
    recommended_count = c.fetchone()[0]

    # 最近观测日期
    c.execute("SELECT MAX(capture_time) FROM photos")
    last_observation = c.fetchone()[0]

    # 本月统计
    from datetime import datetime
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    c.execute("SELECT COUNT(*) FROM photos WHERE capture_time >= ?", (month_start,))
    month_photos = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(DISTINCT bd.species_cn)
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE p.capture_time >= ?
    """, (month_start,))
    month_species = c.fetchone()[0]

    conn.close()

    return {
        "total_photos": total_photos or 0,
        "total_species": total_species or 0,
        "observation_days": observation_days or 0,
        "recommended_photos": recommended_count or 0,
        "last_observation": last_observation,
        "month_stats": {
            "photos": month_photos or 0,
            "species": month_species or 0
        }
    }
