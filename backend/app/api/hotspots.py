"""
热点地图 API - 观鸟热点和地点订阅功能
参照 eBird Hotspots 功能
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import folium
from folium.plugins import HeatMap, MarkerCluster
import math

from app.db import database

router = APIRouter()


# ==================== 数据模型 ====================

class HotspotCreate(BaseModel):
    """创建热点"""
    name: str
    description: Optional[str] = None
    gps_lat: float
    gps_lng: float
    radius_meters: Optional[float] = 500
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = "中国"
    habitat_type: Optional[str] = None
    access_level: Optional[str] = "public"
    created_by: Optional[str] = None


class HotspotUpdate(BaseModel):
    """更新热点"""
    name: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    habitat_type: Optional[str] = None
    access_level: Optional[str] = None


class HotspotResponse(BaseModel):
    """热点响应"""
    id: int
    name: str
    description: Optional[str]
    gps_lat: float
    gps_lng: float
    radius_meters: Optional[float]
    city: Optional[str]
    province: Optional[str]
    country: str
    habitat_type: Optional[str]
    access_level: str
    created_by: Optional[str]
    visit_count: int
    total_species: int
    total_checklists: int
    created_at: str
    updated_at: str


class LocationSubscriptionCreate(BaseModel):
    """创建地点订阅"""
    user_name: str
    location_name: str
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    radius_km: Optional[float] = 5
    notification_enabled: Optional[bool] = True
    email_enabled: Optional[bool] = False
    wechat_enabled: Optional[bool] = False
    min_species_count: Optional[int] = 1


class LocationSubscriptionResponse(BaseModel):
    """地点订阅响应"""
    id: int
    user_name: str
    location_name: str
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    radius_km: float
    notification_enabled: bool
    email_enabled: bool
    wechat_enabled: bool
    min_species_count: int
    created_at: str
    last_notified_at: Optional[str]
    is_active: bool


# ==================== 热点 API ====================

@router.post("/hotspot", response_model=Dict[str, Any])
async def create_hotspot(hotspot: HotspotCreate):
    """
    创建新的观鸟热点

    - **name**: 热点名称
    - **gps_lat**: 纬度
    - **gps_lng**: 经度
    - **radius_meters**: 半径（米）
    - **habitat_type**: 栖息地类型（如：湿地、森林、公园等）
    """
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO hotspots (name, description, gps_lat, gps_lng, radius_meters,
                             city, province, country, habitat_type, access_level, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (hotspot.name, hotspot.description, hotspot.gps_lat, hotspot.gps_lng,
          hotspot.radius_meters, hotspot.city, hotspot.province, hotspot.country,
          hotspot.habitat_type, hotspot.access_level, hotspot.created_by))

    hotspot_id = c.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": hotspot_id,
        "message": "热点创建成功",
        "name": hotspot.name
    }


@router.get("/hotspot/{hotspot_id}", response_model=HotspotResponse)
async def get_hotspot(hotspot_id: int):
    """获取热点详情"""
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM hotspots WHERE id = ?", (hotspot_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="热点不存在")

    # 统计访问次数
    c.execute("SELECT COUNT(*) FROM hotspot_visits WHERE hotspot_id = ?", (hotspot_id,))
    visit_count = c.fetchone()[0] or 0

    # 统计物种数
    c.execute("""
        SELECT COUNT(DISTINCT ci.species_cn)
        FROM hotspot_visits hv
        LEFT JOIN checklists cl ON hv.checklist_id = cl.id
        LEFT JOIN checklist_items ci ON cl.id = ci.checklist_id
        WHERE hv.hotspot_id = ?
    """, (hotspot_id,))
    total_species = c.fetchone()[0] or 0

    # 统计清单数
    c.execute("SELECT COUNT(DISTINCT checklist_id) FROM hotspot_visits WHERE hotspot_id = ?", (hotspot_id,))
    total_checklists = c.fetchone()[0] or 0

    conn.close()

    return HotspotResponse(
        id=row[0], name=row[1], description=row[2],
        gps_lat=row[3], gps_lng=row[4], radius_meters=row[5],
        city=row[6], province=row[7], country=row[8],
        habitat_type=row[9], access_level=row[10], created_by=row[11],
        visit_count=visit_count, total_species=total_species,
        total_checklists=total_checklists,
        created_at=row[12], updated_at=row[13]
    )


@router.get("/hotspots")
async def list_hotspots(
    limit: int = Query(50, description="返回数量限制", le=200),
    offset: int = Query(0, description="偏移量"),
    province: Optional[str] = Query(None, description="省份筛选"),
    city: Optional[str] = Query(None, description="城市筛选"),
    habitat_type: Optional[str] = Query(None, description="栖息地类型筛选"),
    search: Optional[str] = Query(None, description="名称搜索")
):
    """获取热点列表（支持筛选和搜索）"""
    conn = database.get_connection()
    c = conn.cursor()

    query = "SELECT * FROM hotspots WHERE 1=1"
    params = []

    if province:
        query += " AND province = ?"
        params.append(province)
    if city:
        query += " AND city = ?"
        params.append(city)
    if habitat_type:
        query += " AND habitat_type = ?"
        params.append(habitat_type)
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY visit_count DESC, total_checklists DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    rows = c.fetchall()

    # 获取每个热点的统计
    result = []
    for row in rows:
        c.execute("SELECT COUNT(*) FROM hotspot_visits WHERE hotspot_id = ?", (row[0],))
        visit_count = c.fetchone()[0] or 0

        result.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "gps_lat": row[3],
            "gps_lng": row[4],
            "radius_meters": row[5],
            "city": row[6],
            "province": row[7],
            "country": row[8],
            "habitat_type": row[9],
            "access_level": row[10],
            "created_by": row[11],
            "visit_count": visit_count,
            "created_at": row[12],
            "updated_at": row[13]
        })

    conn.close()
    return {"hotspots": result, "total": len(result)}


@router.put("/hotspot/{hotspot_id}")
async def update_hotspot(hotspot_id: int, hotspot: HotspotUpdate):
    """更新热点信息"""
    conn = database.get_connection()
    c = conn.cursor()

    # 检查是否存在
    c.execute("SELECT id FROM hotspots WHERE id = ?", (hotspot_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="热点不存在")

    update_fields = []
    params = []

    if hotspot.name is not None:
        update_fields.append("name = ?")
        params.append(hotspot.name)
    if hotspot.description is not None:
        update_fields.append("description = ?")
        params.append(hotspot.description)
    if hotspot.city is not None:
        update_fields.append("city = ?")
        params.append(hotspot.city)
    if hotspot.province is not None:
        update_fields.append("province = ?")
        params.append(hotspot.province)
    if hotspot.habitat_type is not None:
        update_fields.append("habitat_type = ?")
        params.append(hotspot.habitat_type)
    if hotspot.access_level is not None:
        update_fields.append("access_level = ?")
        params.append(hotspot.access_level)

    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(hotspot_id)
        c.execute(f"UPDATE hotspots SET {', '.join(update_fields)} WHERE id = ?", params)
        conn.commit()

    conn.close()
    return {"message": "更新成功"}


@router.delete("/hotspot/{hotspot_id}")
async def delete_hotspot(hotspot_id: int):
    """删除热点"""
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM hotspots WHERE id = ?", (hotspot_id,))
    conn.commit()
    conn.close()

    return {"message": "删除成功"}


@router.post("/hotspot/{hotspot_id}/visit")
async def record_hotspot_visit(
    hotspot_id: int,
    checklist_id: Optional[int] = None,
    visit_date: Optional[str] = None,
    observer_name: Optional[str] = None,
    notes: Optional[str] = None
):
    """记录热点访问"""
    conn = database.get_connection()
    c = conn.cursor()

    # 检查热点是否存在
    c.execute("SELECT id FROM hotspots WHERE id = ?", (hotspot_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="热点不存在")

    if not visit_date:
        visit_date = datetime.now().strftime("%Y-%m-%d")

    # 统计物种数
    species_count = 0
    if checklist_id:
        c.execute("""
            SELECT COUNT(*) FROM checklist_items WHERE checklist_id = ?
        """, (checklist_id,))
        species_count = c.fetchone()[0] or 0

    c.execute("""
        INSERT INTO hotspot_visits (hotspot_id, checklist_id, visit_date,
                                   observer_name, species_count, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (hotspot_id, checklist_id, visit_date, observer_name, species_count, notes))

    conn.commit()
    conn.close()

    return {"message": "访问记录成功"}


# ==================== 地点订阅 API ====================

@router.post("/subscription", response_model=Dict[str, Any])
async def create_subscription(subscription: LocationSubscriptionCreate):
    """
    创建地点订阅

    当指定地点附近有新观测记录时，系统会通知订阅用户
    """
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO location_subscriptions (user_name, location_name, gps_lat, gps_lng,
                                           radius_km, notification_enabled, email_enabled,
                                           wechat_enabled, min_species_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (subscription.user_name, subscription.location_name,
          subscription.gps_lat, subscription.gps_lng, subscription.radius_km,
          subscription.notification_enabled, subscription.email_enabled,
          subscription.wechat_enabled, subscription.min_species_count))

    subscription_id = c.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": subscription_id,
        "message": "订阅创建成功",
        "location_name": subscription.location_name
    }


@router.get("/subscriptions")
async def list_subscriptions(
    user_name: str = Query(..., description="用户名"),
    is_active: Optional[bool] = Query(None, description="筛选活跃状态")
):
    """获取用户的地点订阅列表"""
    conn = database.get_connection()
    c = conn.cursor()

    query = "SELECT * FROM location_subscriptions WHERE user_name = ?"
    params = [user_name]

    if is_active is not None:
        query += " AND is_active = ?"
        params.append(1 if is_active else 0)

    query += " ORDER BY created_at DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    subscriptions = []
    for row in rows:
        subscriptions.append({
            "id": row[0],
            "user_name": row[1],
            "location_name": row[2],
            "gps_lat": row[3],
            "gps_lng": row[4],
            "radius_km": row[5],
            "notification_enabled": row[6],
            "email_enabled": row[7],
            "wechat_enabled": row[8],
            "min_species_count": row[9],
            "created_at": row[10],
            "last_notified_at": row[11],
            "is_active": row[12]
        })

    return {"subscriptions": subscriptions, "total": len(subscriptions)}


@router.put("/subscription/{subscription_id}/toggle")
async def toggle_subscription(subscription_id: int):
    """切换订阅状态（启用/禁用）"""
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("SELECT is_active FROM location_subscriptions WHERE id = ?", (subscription_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="订阅不存在")

    new_status = 0 if row[0] else 1
    c.execute("UPDATE location_subscriptions SET is_active = ? WHERE id = ?", (new_status, subscription_id))
    conn.commit()
    conn.close()

    return {"message": "状态已更新", "is_active": bool(new_status)}


@router.delete("/subscription/{subscription_id}")
async def delete_subscription(subscription_id: int):
    """删除订阅"""
    conn = database.get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM location_subscriptions WHERE id = ?", (subscription_id,))
    conn.commit()
    conn.close()

    return {"message": "删除成功"}


# ==================== 热点地图 API ====================

@router.get("/hotspots/map")
async def get_hotspots_map(
    lat: Optional[float] = Query(None, description="当前纬度"),
    lng: Optional[float] = Query(None, description="当前经度"),
    zoom: Optional[int] = Query(10, description="缩放级别"),
    radius_km: Optional[float] = Query(100, description="搜索半径（公里）")
):
    """
    获取热点地图数据

    返回指定区域内的所有热点，支持以当前位置为中心搜索
    """
    conn = database.get_connection()
    c = conn.cursor()

    if lat is not None and lng is not None:
        # 计算搜索边界（简单的近似计算）
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * abs(math.cos(math.radians(lat))))

        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lng = lng - lng_delta
        max_lng = lng + lng_delta

        c.execute("""
            SELECT * FROM hotspots
            WHERE gps_lat BETWEEN ? AND ?
              AND gps_lng BETWEEN ? AND ?
            ORDER BY visit_count DESC
        """, (min_lat, max_lat, min_lng, max_lng))
    else:
        c.execute("SELECT * FROM hotspots ORDER BY visit_count DESC LIMIT 100")

    rows = c.fetchall()

    hotspots = []
    for row in rows:
        # 获取统计
        c.execute("SELECT COUNT(*) FROM hotspot_visits WHERE hotspot_id = ?", (row[0],))
        visit_count = c.fetchone()[0] or 0

        hotspots.append({
            "id": row[0],
            "name": row[1],
            "gps_lat": row[3],
            "gps_lng": row[4],
            "city": row[6],
            "province": row[7],
            "habitat_type": row[9],
            "visit_count": visit_count
        })

    conn.close()

    # 生成地图 HTML
    if lat is None or lng is None:
        center = [35.8617, 104.1954]  # 中国中心
    else:
        center = [lat, lng]

    m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')

    # 添加热点标记
    for hotspot in hotspots:
        popup_html = f"""
        <div style="min-width: 200px;">
            <h4 style="margin: 0 0 8px 0;">{hotspot['name']}</h4>
            <p><strong>城市:</strong> {hotspot.get('city') or 'N/A'}</p>
            <p><strong>省份:</strong> {hotspot.get('province') or 'N/A'}</p>
            <p><strong>栖息地:</strong> {hotspot.get('habitat_type') or 'N/A'}</p>
            <p><strong>访问次数:</strong> {hotspot['visit_count']}</p>
        </div>
        """

        folium.Marker(
            location=[hotspot['gps_lat'], hotspot['gps_lng']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='green', icon='bird', prefix='fa')
        ).add_to(m)

    # 如果有当前位置，添加标记
    if lat is not None and lng is not None:
        folium.Marker(
            location=[lat, lng],
            popup="当前位置",
            icon=folium.Icon(color='red', icon='star', prefix='fa')
        ).add_to(m)

    return JSONResponse({
        "hotspots": hotspots,
        "map_html": m._repr_html_(),
        "center": center
    })


@router.get("/hotspots/heatmap")
async def get_hotspots_heatmap(
    year: Optional[int] = Query(None, description="年份筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    获取热点热力图

    基于观测记录的密度生成热力图
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 从照片表获取 GPS 数据
    query = """
        SELECT gps_lat, gps_lng, COUNT(*) as count
        FROM photos
        WHERE gps_lat IS NOT NULL AND gps_lng IS NOT NULL
    """
    params = []

    if year:
        query += " AND strftime('%Y', capture_time) = ?"
        params.append(str(year))

    if start_date:
        query += " AND capture_time >= ?"
        params.append(start_date)

    if end_date:
        query += " AND capture_time <= ?"
        params.append(end_date)

    query += " GROUP BY gps_lat, gps_lng"

    c.execute(query, params)
    rows = c.fetchall()

    # 准备热力图数据
    heat_data = [[row[0], row[1], row[2]] for row in rows]

    conn.close()

    if not heat_data:
        return {"message": "暂无位置数据"}

    # 计算中心点
    center_lat = sum(row[0] for row in rows) / len(rows)
    center_lng = sum(row[1] for row in rows) / len(rows)

    # 创建地图
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # 添加热力图
    HeatMap(heat_data, radius=15, blur=10, max_zoom=10).add_to(m)

    # 添加标记聚类
    marker_cluster = MarkerCluster().add_to(m)

    for row in rows:
        if row[2] >= 5:  # 只显示观测次数>=5 的点
            folium.Marker(
                location=[row[0], row[1]],
                popup=f"观测次数：{row[2]}",
                icon=folium.Icon(color='green')
            ).add_to(marker_cluster)

    return JSONResponse({
        "map_html": m._repr_html_(),
        "data_points": len(heat_data),
        "center": [center_lat, center_lng]
    })


# ==================== 推荐热点 API ====================

@router.get("/hotspots/recommended")
async def get_recommended_hotspots(
    lat: float = Query(..., description="当前纬度"),
    lng: float = Query(..., description="当前经度"),
    limit: int = Query(10, description="返回数量限制")
):
    """
    获取推荐的热点

    基于距离和热门程度推荐附近的观鸟热点
    """
    conn = database.get_connection()
    c = conn.cursor()

    # 获取所有热点并计算距离
    c.execute("SELECT * FROM hotspots WHERE gps_lat IS NOT NULL AND gps_lng IS NOT NULL")
    rows = c.fetchall()

    def calculate_distance(lat1, lon1, lat2, lon2):
        """计算两点之间的距离（Haversine 公式）"""
        R = 6371  # 地球半径（公里）
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    # 计算距离并排序
    hotspots_with_distance = []
    for row in rows:
        distance = calculate_distance(lat, lng, row[3], row[4])
        if distance <= 50:  # 只考虑 50 公里内的热点
            c.execute("SELECT COUNT(*) FROM hotspot_visits WHERE hotspot_id = ?", (row[0],))
            visit_count = c.fetchone()[0] or 0
            hotspots_with_distance.append({
                "id": row[0],
                "name": row[1],
                "gps_lat": row[3],
                "gps_lng": row[4],
                "city": row[6],
                "province": row[7],
                "habitat_type": row[9],
                "distance_km": round(distance, 2),
                "visit_count": visit_count,
                "score": visit_count / (distance + 1)  # 评分：访问次数/距离
            })

    # 按评分排序
    hotspots_with_distance.sort(key=lambda x: x['score'], reverse=True)

    conn.close()

    return {
        "recommended": hotspots_with_distance[:limit],
        "search_center": {"lat": lat, "lng": lng}
    }
