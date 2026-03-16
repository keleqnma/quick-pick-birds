"""
观鸟小结生成 API - 生成 HTML 小结和日历数据
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3

from app.db import database

router = APIRouter()


class SummaryRequest(BaseModel):
    """小结生成请求"""
    session_id: int
    output_path: Optional[str] = None


class SummaryResponse(BaseModel):
    """小结生成响应"""
    session_id: int
    html_path: str
    stats: Dict[str, Any]


class CalendarResponse(BaseModel):
    """日历数据响应"""
    year: int
    month: int
    days: List[Dict[str, Any]]


def generate_html_template(summary_data: Dict[str, Any]) -> str:
    """生成 HTML 小结模板"""
    session = summary_data.get("session", {})
    stats = summary_data.get("stats", {})
    gps_points = summary_data.get("gps_points", [])
    detections = summary_data.get("detections", [])

    # 格式化日期
    scan_date = session.get("scan_date", "")
    if scan_date:
        try:
            dt = datetime.fromisoformat(scan_date)
            scan_date_str = dt.strftime("%Y年%m月%d日 %H:%M")
        except:
            scan_date_str = scan_date
    else:
        scan_date_str = "未知日期"

    # 物种列表
    species_list = stats.get("species_list", "")
    if species_list:
        species_items = [f"<span class='species-tag'>{s.strip()}</span>" for s in species_list.split(",") if s.strip()]
        species_html = "".join(species_items)
    else:
        species_html = "<span class='species-tag'>暂无记录</span>"

    # GPS 地图 HTML（使用 folium 或直接嵌入 Leaflet）
    if gps_points:
        map_html = generate_folium_map(gps_points, session.get("location_name", "观鸟地点"))
    else:
        map_html = '<div class="no-map">暂无 GPS 数据</div>'

    # 检测列表
    detection_cards = []
    for det in detections:
        card = f"""
        <div class="detection-card">
            <div class="detection-header">
                <h3>{det.get('species_cn', '未知')}</h3>
                <span class="species-en">{det.get('species_en', '')}</span>
            </div>
            <div class="detection-body">
                {f'<p class="description">{det.get("description", "")}</p>' if det.get('description') else ''}
                {f'<p class="behavior">🔍 行为：{det.get("behavior", "")}</p>' if det.get('behavior') else ''}
                <p class="meta">📷 {det.get('file_path', '')}</p>
            </div>
        </div>
        """
        detection_cards.append(card)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>观鸟小结 - {scan_date_str}</title>
    <link href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #2d5a27;
            --secondary-color: #4a7c43;
            --accent-color: #8bc34a;
            --bg-color: #f5f9f4;
            --card-bg: #ffffff;
            --text-color: #333333;
            --text-light: #666666;
            --border-radius: 12px;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f9f4 0%, #e8f5e9 100%);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: var(--border-radius);
            margin-bottom: 30px;
            box-shadow: var(--shadow);
        }}

        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        header .date {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        header .location {{
            font-size: 1.1rem;
            opacity: 0.85;
            margin-top: 8px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--card-bg);
            padding: 25px 20px;
            border-radius: var(--border-radius);
            text-align: center;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid transparent;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
            border-color: var(--accent-color);
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            line-height: 1;
        }}

        .stat-card .label {{
            font-size: 0.95rem;
            color: var(--text-light);
            margin-top: 8px;
        }}

        .section {{
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: var(--shadow);
        }}

        .section h2 {{
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section h2::before {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 24px;
            background: var(--accent-color);
            border-radius: 4px;
        }}

        .species-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .species-tag {{
            background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        #map {{
            height: 400px;
            border-radius: var(--border-radius);
            z-index: 1;
        }}

        .no-map {{
            text-align: center;
            padding: 40px;
            color: var(--text-light);
            font-style: italic;
        }}

        .detection-card {{
            background: var(--bg-color);
            border-radius: var(--border-radius);
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid var(--accent-color);
            transition: transform 0.2s ease;
        }}

        .detection-card:hover {{
            transform: translateX(5px);
        }}

        .detection-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 12px;
        }}

        .detection-header h3 {{
            color: var(--primary-color);
            font-size: 1.2rem;
        }}

        .species-en {{
            color: var(--text-light);
            font-style: italic;
            font-size: 0.95rem;
        }}

        .detection-body {{
            color: var(--text-color);
        }}

        .detection-body p {{
            margin-bottom: 8px;
        }}

        .description {{
            background: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.95rem;
        }}

        .behavior {{
            color: var(--primary-color);
            font-weight: 500;
        }}

        .meta {{
            font-size: 0.85rem;
            color: var(--text-light);
            margin-top: 10px;
        }}

        footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-light);
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8rem;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .stat-card .value {{
                font-size: 2rem;
            }}
        }}

        @media print {{
            body {{
                background: white;
            }}

            .section {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐦 观鸟小结</h1>
            <div class="date">📅 {scan_date_str}</div>
            {f'<div class="location">📍 {session.get("location_name", "未知地点")}</div>' if session.get('location_name') else ''}
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{stats.get('total_photos', 0)}</div>
                <div class="label">总照片数</div>
            </div>
            <div class="stat-card">
                <div class="value">{stats.get('recommended_count', 0)}</div>
                <div class="label">推荐照片</div>
            </div>
            <div class="stat-card">
                <div class="value">{stats.get('species_count', 0)}</div>
                <div class="label">物种数量</div>
            </div>
            <div class="stat-card">
                <div class="value">{stats.get('photos_with_gps', 0)}</div>
                <div class="label">带 GPS 照片</div>
            </div>
        </div>

        <div class="section">
            <h2>观测物种</h2>
            <div class="species-list">
                {species_html}
            </div>
        </div>

        <div class="section">
            <h2>观测地点</h2>
            <div id="map"></div>
        </div>

        <div class="section">
            <h2>观测记录</h2>
            {"".join(detection_cards) if detection_cards else '<p class="no-data">暂无观测记录</p>'}
        </div>

        <footer>
            <p>Quick Pick Birds · 智能观鸟助手</p>
            <p>生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // 初始化地图
        const mapContainer = document.getElementById('map');
        let hasGpsData = {str(gps_points is not None and len(gps_points) > 0).lower()};

        if (hasGpsData) {{
            const gpsPoints = {str(gps_points)};
            const centerLat = gpsPoints[0].gps_lat;
            const centerLng = gpsPoints[0].gps_lng;

            const map = L.map('map').setView([centerLat, centerLng], 13);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            // 添加标记点
            gpsPoints.forEach((point, index) => {{
                const marker = L.marker([point.gps_lat, point.gps_lng]).addTo(map);
                marker.bindPopup(`<b>观测点 ${index + 1}</b><br>照片数：${point.cnt}`);
            }});
        }} else {{
            mapContainer.innerHTML = '<div class="no-map">📍 暂无 GPS 数据，无法显示地图</div>';
        }}
    </script>
</body>
</html>"""

    return html


def generate_folium_map(gps_points: List[Dict], location_name: str = "观鸟地点") -> str:
    """使用 folium 生成地图 HTML（可选）"""
    try:
        import folium

        if not gps_points:
            return '<div class="no-map">暂无 GPS 数据</div>'

        # 计算中心点
        center_lat = sum(p['gps_lat'] for p in gps_points) / len(gps_points)
        center_lng = sum(p['gps_lng'] for p in gps_points) / len(gps_points)

        # 创建地图
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # 添加标记
        for i, point in enumerate(gps_points):
            folium.Marker(
                location=[point['gps_lat'], point['gps_lng']],
                popup=f"观测点 {i+1}<br>照片数：{point['cnt']}",
                icon=folium.Icon(color='green', icon='bird', prefix='fa')
            ).add_to(m)

        return m._repr_html_()
    except ImportError:
        # folium 不可用时返回提示
        return '<div class="no-map">地图组件未加载</div>'


@router.post("/generate-summary")
async def generate_summary(request: SummaryRequest) -> SummaryResponse:
    """
    生成观鸟小结 HTML

    从数据库获取会话数据，生成精美的 HTML 小结页面
    """
    # 获取会话摘要
    summary_data = database.get_session_summary(request.session_id)

    if not summary_data:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 生成 HTML
    html_content = generate_html_template(summary_data)

    # 确定输出路径
    if request.output_path:
        output_path = request.output_path
    else:
        # 默认输出到 summaries 目录
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "summaries")
        os.makedirs(output_dir, exist_ok=True)
        session = summary_data.get("session", {})
        filename = f"summary_{request.session_id}_{session.get('scan_date', '')[:10]}.html"
        output_path = os.path.join(output_dir, filename)

    # 保存 HTML 文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return SummaryResponse(
        session_id=request.session_id,
        html_path=output_path,
        stats=summary_data.get("stats", {})
    )


@router.get("/calendar/{year}/{month}")
async def get_calendar_data(year: int, month: int) -> CalendarResponse:
    """
    获取指定月份的观鸟日历数据

    返回每天的：
    - 照片数量
    - 物种数量
    - 物种列表
    """
    days_data = database.get_calendar_data(year, month)

    # 转换为前端需要的格式
    days = []
    for day in days_data:
        date_str = day.get("date", "")
        days.append({
            "date": date_str,
            "day": int(date_str.split("-")[-1]) if date_str else 0,
            "photo_count": day.get("photo_count", 0),
            "species_count": day.get("species_count", 0),
            "species_list": day.get("species_list", "").split(",") if day.get("species_list") else []
        })

    # 按日期排序
    days.sort(key=lambda x: x["day"])

    return CalendarResponse(
        year=year,
        month=month,
        days=days
    )


@router.get("/summary/{session_id}")
async def get_session_summary(session_id: int) -> Dict[str, Any]:
    """获取会话摘要数据（JSON 格式）"""
    summary_data = database.get_session_summary(session_id)

    if not summary_data:
        raise HTTPException(status_code=404, detail="会话不存在")

    return summary_data


@router.get("/sessions")
async def list_sessions(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """获取观测会话列表"""
    sessions = database.list_sessions(limit, offset)
    total = len(database.list_sessions(1, 0))  # 简单获取总数
    return {
        "sessions": sessions,
        "total": total
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: int) -> Dict[str, Any]:
    """获取单个会话详情"""
    session = database.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    photos = database.get_photos_by_session(session_id)
    detections = database.get_detections_by_session(session_id)

    return {
        "session": session,
        "photos": photos,
        "detections": detections
    }


@router.get("/yearly-summary/{year}")
async def get_yearly_summary(year: int) -> Dict[str, Any]:
    """获取年度统计摘要"""
    return database.get_yearly_summary(year)


@router.get("/species/list")
async def get_species_list() -> List[Dict[str, Any]]:
    """获取所有检测过的鸟类列表"""
    return database.get_species_list()
