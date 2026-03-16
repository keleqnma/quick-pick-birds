"""
SQLite 数据库 - 记录观鸟数据
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "bird_watching.db")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    c = conn.cursor()

    # 观测会话表 - 记录每次导入
    c.execute("""
        CREATE TABLE IF NOT EXISTS observation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT NOT NULL,
            scan_date TEXT NOT NULL,
            total_photos INTEGER DEFAULT 0,
            location_name TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 照片表 - 记录每张照片
    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT,
            capture_time TEXT,
            gps_lat REAL,
            gps_lng REAL,
            gps_alt REAL,
            camera_model TEXT,
            lens_model TEXT,
            focal_length TEXT,
            iso INTEGER,
            aperture TEXT,
            shutter_speed TEXT,
            quality_score REAL,
            is_recommended BOOLEAN DEFAULT 0,
            scoring_explanation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES observation_sessions(id) ON DELETE CASCADE
        )
    """)

    # 照片索引
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_photos_session ON photos(session_id)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_photos_capture_time ON photos(capture_time)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_photos_gps ON photos(gps_lat, gps_lng)
    """)

    # 鸟类检测表 - 记录鸟类识别
    c.execute("""
        CREATE TABLE IF NOT EXISTS bird_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id INTEGER NOT NULL,
            species_cn TEXT,
            species_en TEXT,
            scientific_name TEXT,
            confidence REAL,
            description TEXT,
            behavior TEXT,
            detection_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_detections_photo ON bird_detections(photo_id)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_detections_species ON bird_detections(species_cn)
    """)

    conn.commit()
    conn.close()


# ==================== Session CRUD ====================

def create_session(folder_path: str, total_photos: int = 0, location_name: str = None, notes: str = None) -> int:
    """创建观测会话"""
    conn = get_connection()
    c = conn.cursor()
    scan_date = datetime.now().isoformat()
    c.execute("""
        INSERT INTO observation_sessions (folder_path, scan_date, total_photos, location_name, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (folder_path, scan_date, total_photos, location_name, notes))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id: int) -> Optional[Dict[str, Any]]:
    """获取会话详情"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM observation_sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_sessions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """获取会话列表（按时间倒序）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM observation_sessions
        ORDER BY scan_date DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_session(session_id: int, location_name: str = None, notes: str = None):
    """更新会话信息"""
    conn = get_connection()
    c = conn.cursor()
    if location_name:
        c.execute("UPDATE observation_sessions SET location_name = ? WHERE id = ?", (location_name, session_id))
    if notes:
        c.execute("UPDATE observation_sessions SET notes = ? WHERE id = ?", (notes, session_id))
    conn.commit()
    conn.close()


def delete_session(session_id: int):
    """删除会话（级联删除照片和检测）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM observation_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


# ==================== Photo CRUD ====================

def save_photo(session_id: int, file_path: str, file_name: str = None, capture_time: str = None,
               gps_lat: float = None, gps_lng: float = None, gps_alt: float = None,
               camera_model: str = None, lens_model: str = None, focal_length: str = None,
               iso: int = None, aperture: str = None, shutter_speed: str = None,
               quality_score: float = None, is_recommended: bool = False, scoring_explanation: str = None) -> int:
    """保存照片记录"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO photos (session_id, file_path, file_name, capture_time, gps_lat, gps_lng, gps_alt,
                           camera_model, lens_model, focal_length, iso, aperture, shutter_speed,
                           quality_score, is_recommended, scoring_explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, file_path, file_name, capture_time, gps_lat, gps_lng, gps_alt,
          camera_model, lens_model, focal_length, iso, aperture, shutter_speed,
          quality_score, is_recommended, scoring_explanation))
    photo_id = c.lastrowid
    conn.commit()
    conn.close()
    return photo_id


def save_photos_batch(photos_data: List[Dict[str, Any]]):
    """批量保存照片"""
    conn = get_connection()
    c = conn.cursor()
    c.executemany("""
        INSERT INTO photos (session_id, file_path, file_name, capture_time, gps_lat, gps_lng, gps_alt,
                           camera_model, lens_model, focal_length, iso, aperture, shutter_speed,
                           quality_score, is_recommended, scoring_explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(p.get('session_id'), p.get('file_path'), p.get('file_name'), p.get('capture_time'),
           p.get('gps_lat'), p.get('gps_lng'), p.get('gps_alt'), p.get('camera_model'),
           p.get('lens_model'), p.get('focal_length'), p.get('iso'), p.get('aperture'),
           p.get('shutter_speed'), p.get('quality_score'), p.get('is_recommended', False),
           p.get('scoring_explanation')) for p in photos_data])
    conn.commit()
    conn.close()


def get_photos_by_session(session_id: int, include_recommended_only: bool = False) -> List[Dict[str, Any]]:
    """获取会话中的所有照片"""
    conn = get_connection()
    c = conn.cursor()
    if include_recommended_only:
        c.execute("""
            SELECT * FROM photos WHERE session_id = ? AND is_recommended = 1
            ORDER BY quality_score DESC, capture_time ASC
        """, (session_id,))
    else:
        c.execute("""
            SELECT * FROM photos WHERE session_id = ?
            ORDER BY quality_score DESC, capture_time ASC
        """, (session_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_photo(photo_id: int) -> Optional[Dict[str, Any]]:
    """获取单张照片详情"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM photos WHERE id = ?", (photo_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_all_photos(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """获取所有照片（分页）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM photos
        ORDER BY capture_time DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== Bird Detection CRUD ====================

def save_detection(photo_id: int, species_cn: str = None, species_en: str = None,
                   scientific_name: str = None, confidence: float = None,
                   description: str = None, behavior: str = None) -> int:
    """保存鸟类检测记录"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO bird_detections (photo_id, species_cn, species_en, scientific_name, confidence, description, behavior)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (photo_id, species_cn, species_en, scientific_name, confidence, description, behavior))
    detection_id = c.lastrowid
    conn.commit()
    conn.close()
    return detection_id


def save_detections_batch(detections_data: List[Dict[str, Any]]):
    """批量保存鸟类检测"""
    conn = get_connection()
    c = conn.cursor()
    c.executemany("""
        INSERT INTO bird_detections (photo_id, species_cn, species_en, scientific_name, confidence, description, behavior)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [(d.get('photo_id'), d.get('species_cn'), d.get('species_en'), d.get('scientific_name'),
           d.get('confidence'), d.get('description'), d.get('behavior')) for d in detections_data])
    conn.commit()
    conn.close()


def get_detections_by_photo(photo_id: int) -> List[Dict[str, Any]]:
    """获取照片的所有鸟类检测"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM bird_detections WHERE photo_id = ?", (photo_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_species_list() -> List[Dict[str, Any]]:
    """获取所有检测过的鸟类列表（按出现次数排序）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT species_cn, species_en, scientific_name, COUNT(*) as count,
               GROUP_CONCAT(photo_id) as photo_ids
        FROM bird_detections
        WHERE species_cn IS NOT NULL AND species_cn != ''
        GROUP BY species_cn, species_en, scientific_name
        ORDER BY count DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_detections_by_session(session_id: int) -> List[Dict[str, Any]]:
    """获取会话的所有鸟类检测"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT bd.*, p.file_path, p.capture_time
        FROM bird_detections bd
        JOIN photos p ON bd.photo_id = p.id
        WHERE p.session_id = ?
    """, (session_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== Calendar & Statistics ====================

def get_calendar_data(year: int, month: int) -> List[Dict[str, Any]]:
    """获取指定月份的观鸟日历数据"""
    conn = get_connection()
    c = conn.cursor()
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"

    c.execute("""
        SELECT DATE(capture_time) as date,
               COUNT(DISTINCT p.id) as photo_count,
               COUNT(DISTINCT bd.species_cn) as species_count,
               GROUP_CONCAT(DISTINCT bd.species_cn) as species_list
        FROM photos p
        LEFT JOIN bird_detections bd ON p.id = bd.photo_id
        WHERE p.capture_time >= ? AND p.capture_time < ?
        GROUP BY DATE(capture_time)
    """, (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_yearly_summary(year: int) -> Dict[str, Any]:
    """获取年度统计摘要"""
    conn = get_connection()
    c = conn.cursor()

    start_date = f"{year}-01-01"
    end_date = f"{year+1}-01-01"

    # 总照片数
    c.execute("SELECT COUNT(*) FROM photos WHERE capture_time >= ? AND capture_time < ?", (start_date, end_date))
    total_photos = c.fetchone()[0]

    # 总物种数
    c.execute("""
        SELECT COUNT(DISTINCT species_cn) FROM bird_detections bd
        JOIN photos p ON bd.photo_id = p.id
        WHERE p.capture_time >= ? AND p.capture_time < ?
    """, (start_date, end_date))
    total_species = c.fetchone()[0]

    # 观测天数
    c.execute("SELECT COUNT(DISTINCT DATE(capture_time)) FROM photos WHERE capture_time >= ? AND capture_time < ?", (start_date, end_date))
    observation_days = c.fetchone()[0]

    # 推荐照片数
    c.execute("SELECT COUNT(*) FROM photos WHERE is_recommended = 1 AND capture_time >= ? AND capture_time < ?", (start_date, end_date))
    recommended_count = c.fetchone()[0]

    conn.close()

    return {
        "year": year,
        "total_photos": total_photos or 0,
        "total_species": total_species or 0,
        "observation_days": observation_days or 0,
        "recommended_photos": recommended_count or 0
    }


def get_session_summary(session_id: int) -> Dict[str, Any]:
    """获取会话摘要（用于生成 HTML 小结）"""
    conn = get_connection()
    c = conn.cursor()

    # 会话信息
    session = get_session(session_id)
    if not session:
        conn.close()
        return {}

    # 照片统计
    c.execute("SELECT COUNT(*) FROM photos WHERE session_id = ?", (session_id,))
    total_photos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM photos WHERE session_id = ? AND is_recommended = 1", (session_id,))
    recommended_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM photos WHERE session_id = ? AND gps_lat IS NOT NULL", (session_id,))
    photos_with_gps = c.fetchone()[0]

    # 物种统计
    c.execute("""
        SELECT COUNT(DISTINCT species_cn), GROUP_CONCAT(DISTINCT species_cn)
        FROM bird_detections bd
        JOIN photos p ON bd.photo_id = p.id
        WHERE p.session_id = ?
    """, (session_id,))
    row = c.fetchone()
    species_count = row[0]
    species_list = row[1]

    # GPS 坐标（用于地图）
    c.execute("""
        SELECT gps_lat, gps_lng, COUNT(*) as cnt
        FROM photos
        WHERE session_id = ? AND gps_lat IS NOT NULL
        GROUP BY gps_lat, gps_lng
    """, (session_id,))
    gps_points = c.fetchall()

    # 鸟类检测详情
    c.execute("""
        SELECT bd.species_cn, bd.species_en, bd.description, bd.behavior,
               p.file_path, p.capture_time
        FROM bird_detections bd
        JOIN photos p ON bd.photo_id = p.id
        WHERE p.session_id = ?
    """, (session_id,))
    detections = c.fetchall()

    conn.close()

    return {
        "session": session,
        "stats": {
            "total_photos": total_photos,
            "recommended_count": recommended_count,
            "photos_with_gps": photos_with_gps,
            "species_count": species_count,
            "species_list": species_list
        },
        "gps_points": [dict(row) for row in gps_points],
        "detections": [dict(row) for row in detections]
    }


# 初始化数据库
init_db()
