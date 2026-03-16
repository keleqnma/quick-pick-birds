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

    # 观测清单表 - 记录每次观鸟活动的完整清单 (参照 eBird Checklist)
    c.execute("""
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_date TEXT NOT NULL,
            location_name TEXT NOT NULL,
            gps_lat REAL,
            gps_lng REAL,
            start_time TEXT,
            duration_minutes INTEGER,
            protocol TEXT DEFAULT 'incidental',
            effort_distance_km REAL,
            observer_name TEXT,
            weather TEXT,
            temperature REAL,
            wind TEXT,
            total_species INTEGER DEFAULT 0,
            total_individuals INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_checklists_date ON checklists(checklist_date)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_checklists_location ON checklists(location_name)
    """)

    # 清单项表 - 记录清单中的每个鸟种
    c.execute("""
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            species_cn TEXT NOT NULL,
            species_en TEXT,
            scientific_name TEXT,
            count INTEGER DEFAULT 1,
            sex TEXT,
            age TEXT,
            behavior TEXT,
            breeding_code TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_checklist_items_checklist ON checklist_items(checklist_id)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_checklist_items_species ON checklist_items(species_cn)
    """)

    # 观鸟热点表 - 记录热门观测地点 (参照 eBird Hotspots)
    c.execute("""
        CREATE TABLE IF NOT EXISTS hotspots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            gps_lat REAL NOT NULL,
            gps_lng REAL NOT NULL,
            radius_meters REAL DEFAULT 500,
            city TEXT,
            province TEXT,
            country TEXT DEFAULT '中国',
            habitat_type TEXT,
            access_level TEXT DEFAULT 'public',
            created_by TEXT,
            visit_count INTEGER DEFAULT 0,
            total_species INTEGER DEFAULT 0,
            total_checklists INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_hotspots_location ON hotspots(gps_lat, gps_lng)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_hotspots_name ON hotspots(name)
    """)

    # 热点访问记录表
    c.execute("""
        CREATE TABLE IF NOT EXISTS hotspot_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotspot_id INTEGER NOT NULL,
            checklist_id INTEGER,
            visit_date TEXT NOT NULL,
            observer_name TEXT,
            species_count INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotspot_id) REFERENCES hotspots(id) ON DELETE CASCADE,
            FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_hotspot_visits_hotspot ON hotspot_visits(hotspot_id)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_hotspot_visits_date ON hotspot_visits(visit_date)
    """)

    # 地点订阅表
    c.execute("""
        CREATE TABLE IF NOT EXISTS location_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            location_name TEXT NOT NULL,
            gps_lat REAL,
            gps_lng REAL,
            radius_km REAL DEFAULT 5,
            notification_enabled BOOLEAN DEFAULT 1,
            email_enabled BOOLEAN DEFAULT 0,
            wechat_enabled BOOLEAN DEFAULT 0,
            min_species_count INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_notified_at TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON location_subscriptions(user_name)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_location ON location_subscriptions(location_name)
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


# ==================== Checklist CRUD ====================

def create_checklist(checklist_date: str, location_name: str,
                     gps_lat: float = None, gps_lng: float = None,
                     start_time: str = None, duration_minutes: int = None,
                     protocol: str = "incidental", effort_distance_km: float = None,
                     observer_name: str = None, weather: str = None,
                     temperature: float = None, wind: str = None,
                     notes: str = None) -> int:
    """创建观测清单"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO checklists (checklist_date, location_name, gps_lat, gps_lng,
                                start_time, duration_minutes, protocol, effort_distance_km,
                                observer_name, weather, temperature, wind, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (checklist_date, location_name, gps_lat, gps_lng, start_time,
          duration_minutes, protocol, effort_distance_km, observer_name,
          weather, temperature, wind, notes))
    checklist_id = c.lastrowid
    conn.commit()
    conn.close()
    return checklist_id


def get_checklist(checklist_id: int) -> Optional[Dict[str, Any]]:
    """获取清单详情"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM checklists WHERE id = ?", (checklist_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_checklist_with_items(checklist_id: int) -> Optional[Dict[str, Any]]:
    """获取清单及其所有项"""
    conn = get_connection()
    c = conn.cursor()

    # 获取清单主记录
    c.execute("SELECT * FROM checklists WHERE id = ?", (checklist_id,))
    checklist = c.fetchone()
    if not checklist:
        conn.close()
        return None

    checklist_dict = dict(checklist)

    # 获取清单项
    c.execute("""
        SELECT * FROM checklist_items
        WHERE checklist_id = ?
        ORDER BY species_cn
    """, (checklist_id,))
    items = c.fetchall()
    checklist_dict["items"] = [dict(item) for item in items]

    # 统计
    total_species = len(items)
    total_individuals = sum(item["count"] for item in items)
    checklist_dict["total_species"] = total_species
    checklist_dict["total_individuals"] = total_individuals

    # 更新统计
    c.execute("""
        UPDATE checklists
        SET total_species = ?, total_individuals = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (total_species, total_individuals, checklist_id))
    conn.commit()
    conn.close()

    return checklist_dict


def list_checklists(year: int = None, month: int = None,
                    location: str = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """获取清单列表（支持筛选）"""
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT * FROM checklists WHERE 1=1"
    params = []

    if year:
        query += " AND strftime('%Y', checklist_date) = ?"
        params.append(str(year))
    if month:
        query += " AND strftime('%Y-%m', checklist_date) = ?"
        params.append(f"{year}-{month:02d}")
    if location:
        query += " AND location_name LIKE ?"
        params.append(f"%{location}%")

    query += " ORDER BY checklist_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_checklist(checklist_id: int, **kwargs):
    """更新清单信息"""
    conn = get_connection()
    c = conn.cursor()

    allowed_fields = ["location_name", "gps_lat", "gps_lng", "start_time",
                      "duration_minutes", "protocol", "effort_distance_km",
                      "observer_name", "weather", "temperature", "wind", "notes"]

    for field in allowed_fields:
        if field in kwargs and kwargs[field] is not None:
            c.execute(f"UPDATE checklists SET {field} = ? WHERE id = ?",
                      (kwargs[field], checklist_id))

    c.execute("UPDATE checklists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
              (checklist_id,))
    conn.commit()
    conn.close()


def delete_checklist(checklist_id: int):
    """删除清单（级联删除清单项）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM checklists WHERE id = ?", (checklist_id,))
    conn.commit()
    conn.close()


def save_checklist_item(checklist_id: int, species_cn: str,
                        species_en: str = None, scientific_name: str = None,
                        count: int = 1, sex: str = None, age: str = None,
                        behavior: str = None, breeding_code: str = None,
                        notes: str = None) -> int:
    """保存清单项"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO checklist_items (checklist_id, species_cn, species_en, scientific_name,
                                     count, sex, age, behavior, breeding_code, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (checklist_id, species_cn, species_en, scientific_name,
          count, sex, age, behavior, breeding_code, notes))
    item_id = c.lastrowid

    # 更新清单统计
    _update_checklist_stats(conn, checklist_id)
    conn.commit()
    conn.close()
    return item_id


def save_checklist_items_batch(items_data: List[Dict[str, Any]]):
    """批量保存清单项"""
    conn = get_connection()
    c = conn.cursor()

    checklist_ids = set(item["checklist_id"] for item in items_data)

    c.executemany("""
        INSERT INTO checklist_items (checklist_id, species_cn, species_en, scientific_name,
                                     count, sex, age, behavior, breeding_code, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(item.get("checklist_id"), item.get("species_cn"), item.get("species_en"),
           item.get("scientific_name"), item.get("count", 1), item.get("sex"),
           item.get("age"), item.get("behavior"), item.get("breeding_code"),
           item.get("notes")) for item in items_data])

    # 更新所有相关清单的统计
    for checklist_id in checklist_ids:
        _update_checklist_stats(conn, checklist_id)

    conn.commit()
    conn.close()


def delete_checklist_item(item_id: int):
    """删除清单项"""
    conn = get_connection()
    c = conn.cursor()

    # 先获取 checklist_id
    c.execute("SELECT checklist_id FROM checklist_items WHERE id = ?", (item_id,))
    row = c.fetchone()
    if row:
        checklist_id = row[0]
        c.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        _update_checklist_stats(conn, checklist_id)

    conn.commit()
    conn.close()


def _update_checklist_stats(conn, checklist_id: int):
    """更新清单统计（内部函数）"""
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*), SUM(count)
        FROM checklist_items
        WHERE checklist_id = ?
    """, (checklist_id,))
    row = c.fetchone()
    total_species = row[0] or 0
    total_individuals = row[1] or 0

    c.execute("""
        UPDATE checklists
        SET total_species = ?, total_individuals = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (total_species, total_individuals, checklist_id))


def get_checklist_stats() -> Dict[str, Any]:
    """获取清单统计"""
    conn = get_connection()
    c = conn.cursor()

    # 总清单数
    c.execute("SELECT COUNT(*) FROM checklists")
    total_checklists = c.fetchone()[0]

    # 总观测物种数（去重）
    c.execute("SELECT COUNT(DISTINCT species_cn) FROM checklist_items")
    total_species = c.fetchone()[0]

    # 总观测个体数
    c.execute("""
        SELECT SUM(count) FROM checklist_items
    """)
    total_individuals = c.fetchone()[0] or 0

    # 最近清单
    c.execute("""
        SELECT id, checklist_date, location_name, total_species
        FROM checklists
        ORDER BY checklist_date DESC
        LIMIT 5
    """)
    recent_checklists = [dict(row) for row in c.fetchall()]

    conn.close()

    return {
        "total_checklists": total_checklists or 0,
        "total_species": total_species or 0,
        "total_individuals": total_individuals or 0,
        "recent_checklists": recent_checklists
    }


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
