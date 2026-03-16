"""
观鸟地图 API - 根据照片的位置和时间信息绘制观鸟地图
"""
import os
import json
import folium
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from collections import defaultdict

router = APIRouter()


class PhotoLocation(BaseModel):
    """照片位置信息"""
    file_path: str
    file_name: str
    gps_lat: float
    gps_lon: float
    gps_alt: Optional[float] = None
    capture_time: Optional[datetime] = None
    bird_species: Optional[str] = None
    bird_count: int = 1


class MapPoint(BaseModel):
    """地图标点"""
    lat: float
    lon: float
    title: str
    popup_html: str
    icon_color: str = "blue"


class DailyMapResponse(BaseModel):
    """当日观鸟地图响应"""
    map_date: date
    total_photos: int
    total_locations: int
    bird_species_count: int
    points: List[MapPoint]
    map_html: Optional[str] = None
    species_summary: Dict[str, int]


class BirdObservation(BaseModel):
    """观鸟记录"""
    species_cn: str
    species_en: str
    count: int
    locations: List[Dict[str, Any]]
    first_seen: datetime
    last_seen: datetime


def generate_map_html(points: List[MapPoint], center: tuple = None) -> str:
    """
    生成地图 HTML
    使用 folium 库创建交互式地图
    """
    # 默认中心点（如果没有数据，显示中国中心）
    if center is None:
        center = [35.8617, 104.1954]

    # 创建地图
    m = folium.Map(location=center, zoom_start=10, tiles='OpenStreetMap')

    # 添加标记点
    for point in points:
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{point.title}</h4>
            {point.popup_html}
        </div>
        """

        folium.Marker(
            location=[point.lat, point.lon],
            popup=folium.Popup(popup_html, max_width=400),
            icon=folium.Icon(color=point.icon_color, icon='bird', prefix='fa')
        ).add_to(m)

    # 如果有多个点，自动调整视图
    if len(points) > 1:
        lats = [p.lat for p in points]
        lons = [p.lon for p in points]
        # 简单拟合边界
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    return m._repr_html_()


def get_species_color(species: str) -> str:
    """根据鸟种返回标记颜色"""
    colors = {
        "麻雀": "orange",
        "鸽子": "gray",
        "乌鸦": "black",
        "喜鹊": "blue",
        "燕子": "red",
        "翠鸟": "cyan",
        "鹭鸟": "lightblue",
        "鹰": "brown",
        "隼": "darkred",
        "鹦鹉": "green",
        "啄木鸟": "lime",
        "蜂鸟": "pink",
        "火烈鸟": "magenta",
        "鹈鹕": "purple",
        "猫头鹰": "darkpurple",
    }
    return colors.get(species, "blue")


@router.get("/daily")
async def get_daily_map(
    map_date: Optional[str] = Query(None, description="日期，格式 YYYY-MM-DD，默认为今天"),
    photo_locations: Optional[str] = Query(None, description="照片位置信息 JSON")
) -> DailyMapResponse:
    """
    获取当日的观鸟地图

    photo_locations: JSON 字符串，包含照片位置列表
    格式：[{"file_path": "...", "gps_lat": 0.0, "gps_lon": 0.0, "capture_time": "...", "bird_species": "..."}]
    """
    # 解析日期
    if map_date:
        try:
            target_date = datetime.strptime(map_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    else:
        target_date = date.today()

    # 解析照片位置
    locations = []
    if photo_locations:
        try:
            locations = json.loads(photo_locations)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="照片位置 JSON 格式错误")

    # 过滤当天的照片
    daily_photos = []
    for loc in locations:
        if loc.get('capture_time'):
            try:
                capture_date = datetime.fromisoformat(loc['capture_time']).date()
                if capture_date == target_date:
                    daily_photos.append(loc)
            except (ValueError, TypeError):
                # 如果时间解析失败，使用默认格式
                try:
                    capture_date = datetime.strptime(loc['capture_time'], '%Y-%m-%d %H:%M:%S').date()
                    if capture_date == target_date:
                        daily_photos.append(loc)
                except (ValueError, TypeError):
                    pass
        else:
            # 没有时间信息的照片，如果有 GPS 也加入
            if loc.get('gps_lat') is not None and loc.get('gps_lon') is not None:
                daily_photos.append(loc)

    # 按位置分组（相近的 GPS 坐标合并）
    location_groups = defaultdict(list)
    for photo in daily_photos:
        # 简化 GPS 坐标到小数点后 4 位（约 11 米精度）
        lat_key = round(photo.get('gps_lat', 0), 4)
        lon_key = round(photo.get('gps_lon', 0), 4)
        location_groups[(lat_key, lon_key)].append(photo)

    # 创建地图标点
    points = []
    species_count = defaultdict(int)

    for (lat, lon), photos in location_groups.items():
        if lat is None or lon is None:
            continue

        # 统计鸟种
        species_list = [p.get('bird_species') for p in photos if p.get('bird_species')]
        main_species = max(set(species_list), key=species_list.count) if species_list else "未知鸟种"

        for species in species_list:
            if species:
                species_count[species] += 1

        # 格式化时间信息
        time_info = ""
        for p in photos[:5]:  # 只显示前 5 张
            if p.get('capture_time'):
                time_info += f"<div>{p['capture_time']}</div>"

        # 创建标点
        point = MapPoint(
            lat=lat,
            lon=lon,
            title=f"{main_species} x{len(photos)}",
            popup_html=f"""
                <div><strong>照片数量:</strong> {len(photos)}</div>
                <div><strong>鸟种:</strong> {', '.join(set(species_list)) if species_list else '未知'}</div>
                <div><strong>拍摄时间:</strong></div>
                {time_info}
            """,
            icon_color=get_species_color(main_species)
        )
        points.append(point)

    # 计算中心点
    if points:
        center_lat = sum(p.lat for p in points) / len(points)
        center_lon = sum(p.lon for p in points) / len(points)
        center = (center_lat, center_lon)
    else:
        center = None

    # 生成地图 HTML
    map_html = None
    if points:
        map_html = generate_map_html(points, center)

    return DailyMapResponse(
        map_date=target_date,
        total_photos=len(daily_photos),
        total_locations=len(points),
        bird_species_count=len(species_count),
        points=points,
        map_html=map_html,
        species_summary=dict(species_count)
    )


@router.get("/generate")
async def generate_birding_map(
    photo_data: str = Query(..., description="照片数据 JSON")
) -> JSONResponse:
    """
    生成完整的观鸟地图

    photo_data: JSON 字符串
    格式：包含照片路径、GPS 坐标、拍摄时间、识别的鸟种等信息
    """
    try:
        data = json.loads(photo_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="照片数据 JSON 格式错误")

    # 提取位置信息
    locations = []
    for item in data.get('photos', []):
        if item.get('gps_lat') and item.get('gps_lon'):
            locations.append({
                'file_path': item.get('file_path', ''),
                'file_name': item.get('file_name', ''),
                'gps_lat': item['gps_lat'],
                'gps_lon': item['gps_lon'],
                'gps_alt': item.get('gps_alt'),
                'capture_time': item.get('capture_time'),
                'bird_species': item.get('bird_species'),
                'bird_count': item.get('bird_count', 1)
            })

    # 生成地图
    if not locations:
        return JSONResponse({
            "message": "没有可用的位置信息",
            "map_html": None,
            "locations": []
        })

    # 创建 folium 地图
    lats = [loc['gps_lat'] for loc in locations]
    lons = [loc['gps_lon'] for loc in locations]
    center = [sum(lats)/len(lats), sum(lons)/len(lons)]

    m = folium.Map(location=center, zoom_start=12, tiles='OpenStreetMap')

    # 按鸟种分组
    species_groups = defaultdict(list)
    for loc in locations:
        species = loc.get('bird_species', '未知')
        species_groups[species].append(loc)

    # 为每种鸟添加图层
    for species, locs in species_groups.items():
        color = get_species_color(species)

        for loc in locs:
            popup_html = f"""
            <div>
                <h4>{species}</h4>
                <p>文件：{loc['file_name']}</p>
                <p>坐标：{loc['gps_lat']:.4f}, {loc['gps_lon']:.4f}</p>
                <p>时间：{loc.get('capture_time', '未知')}</p>
                <p>海拔：{loc.get('gps_alt', 'N/A')}m</p>
            </div>
            """

            folium.Marker(
                location=[loc['gps_lat'], loc['gps_lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon='map-marker')
            ).add_to(m)

    # 添加图例
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-family: Arial, sans-serif;">
        <h4 style="margin: 0 0 10px 0;">鸟种图例</h4>
    '''
    for species in species_groups.keys():
        color = get_species_color(species)
        legend_html += f'<div><span style="color:{color};">●</span> {species}</div>'
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))

    return JSONResponse({
        "map_html": m._repr_html_(),
        "total_locations": len(locations),
        "species_count": len(species_groups),
        "species_summary": {k: len(v) for k, v in species_groups.items()}
    })


@router.get("/heatmap")
async def get_birding_heatmap(
    session_id: Optional[int] = Query(None, description="会话 ID，为空则使用所有照片")
):
    """
    生成观鸟热点图

    - **session_id**: 可选，指定会话 ID 则只生成该会话的热力图
    """
    from app.db import database

    # 从数据库获取位置数据
    if session_id:
        photos = database.get_photos_by_session(session_id)
    else:
        photos = database.get_all_photos(limit=10000)

    locations = []
    for photo in photos:
        if photo.get('gps_lat') and photo.get('gps_lng'):
            locations.append([photo['gps_lat'], photo['gps_lng']])

    if not locations:
        return {"message": "没有可用的位置信息"}

    # 创建带热力图的地图
    center = [sum(l[0] for l in locations)/len(locations),
              sum(l[1] for l in locations)/len(locations)]

    m = folium.Map(location=center, zoom_start=12, tiles='CartoDB positron')

    # 添加热力图
    from folium.plugins import HeatMap
    heat_map = HeatMap(locations, radius=15, blur=10, max_zoom=1)
    heat_map.add_to(m)

    return JSONResponse({
        "map_html": m._repr_html_(),
        "hotspot_count": len(locations)
    })
