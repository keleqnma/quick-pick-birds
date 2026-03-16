"""
鸟类物种数据库 - 中国鸟类名录
参考：郑光美《中国鸟类分类与分布名录》
"""
import sqlite3
import os
from typing import List, Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "bird_species.db")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_species_db():
    """初始化物种数据库"""
    conn = get_connection()
    c = conn.cursor()

    # 鸟类物种表
    c.execute("""
        CREATE TABLE IF NOT EXISTS bird_species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_cn TEXT,
            order_en TEXT,
            family_cn TEXT,
            family_en TEXT,
            genus_cn TEXT,
            genus_en TEXT,
            species_cn TEXT NOT NULL,
            species_en TEXT,
            scientific_name TEXT NOT NULL,
            conservation_level TEXT,
            china_endemic BOOLEAN DEFAULT 0,
            common BOOLEAN DEFAULT 1,
            description TEXT,
            distribution TEXT,
            habitat TEXT,
            voice TEXT,
            similar_species TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 保护级别表
    c.execute("""
        CREATE TABLE IF NOT EXISTS conservation_levels (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            short_name TEXT,
            description TEXT
        )
    """)

    # 索引
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_species_name ON bird_species(species_cn)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_species_scientific ON bird_species(scientific_name)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_species_family ON bird_species(family_cn)
    """)

    # 初始化保护级别
    conservation_data = [
        (1, "国家重点保护野生动物 - 一级", "国家一级", "濒危物种，禁止捕猎"),
        (2, "国家重点保护野生动物 - 二级", "国家二级", "濒危物种，限制捕猎"),
        (3, "三有保护动物", "三有", "有益的、有重要经济价值、有科学研究价值"),
        (4, "IUCN 极危", "CR", "Critically Endangered"),
        (5, "IUCN 濒危", "EN", "Endangered"),
        (6, "IUCN 易危", "VU", "Vulnerable"),
        (7, "IUCN 近危", "NT", "Near Threatened"),
        (8, "IUCN 无危", "LC", "Least Concern"),
    ]
    c.executemany(
        "INSERT OR REPLACE INTO conservation_levels VALUES (?, ?, ?, ?)",
        conservation_data
    )

    conn.commit()
    conn.close()


def search_species(keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
    """搜索鸟类物种（支持中文名、学名、英文名模糊搜索）"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM bird_species
        WHERE species_cn LIKE ? OR scientific_name LIKE ? OR species_en LIKE ?
        LIMIT ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))

    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_species_by_id(species_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取物种详情"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM bird_species WHERE id = ?", (species_id,))
    row = c.fetchone()

    conn.close()
    if row:
        return dict(row)
    return None


def list_species(
    family: str = None,
    order: str = None,
    common_only: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """获取物种列表（支持筛选）"""
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT * FROM bird_species WHERE 1=1"
    params = []

    if family:
        query += " AND family_cn = ?"
        params.append(family)
    if order:
        query += " AND order_cn = ?"
        params.append(order)
    if common_only:
        query += " AND common = 1"
        params.append(True)

    query += " ORDER BY species_cn LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_families() -> List[Dict[str, Any]]:
    """获取所有科列表"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT family_cn, family_en, order_cn, order_en
        FROM bird_species
        WHERE family_cn IS NOT NULL
        ORDER BY order_cn, family_cn
    """)

    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_orders() -> List[Dict[str, Any]]:
    """获取所有目列表"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT DISTINCT order_cn, order_en
        FROM bird_species
        WHERE order_cn IS NOT NULL
        ORDER BY order_cn
    """)

    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_species_count() -> Dict[str, int]:
    """获取物种统计"""
    conn = get_connection()
    c = conn.cursor()

    # 总数
    c.execute("SELECT COUNT(*) FROM bird_species")
    total = c.fetchone()[0]

    # 常见种
    c.execute("SELECT COUNT(*) FROM bird_species WHERE common = 1")
    common = c.fetchone()[0]

    # 特有种
    c.execute("SELECT COUNT(*) FROM bird_species WHERE china_endemic = 1")
    endemic = c.fetchone()[0]

    conn.close()

    return {
        "total": total or 0,
        "common": common or 0,
        "endemic": endemic or 0
    }


def add_species(species_data: Dict[str, Any]) -> int:
    """添加新物种"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO bird_species (
            order_cn, order_en, family_cn, family_en,
            genus_cn, genus_en, species_cn, species_en,
            scientific_name, conservation_level,
            china_endemic, common, description,
            distribution, habitat, voice, similar_species
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        species_data.get("order_cn"),
        species_data.get("order_en"),
        species_data.get("family_cn"),
        species_data.get("family_en"),
        species_data.get("genus_cn"),
        species_data.get("genus_en"),
        species_data.get("species_cn"),
        species_data.get("species_en"),
        species_data.get("scientific_name"),
        species_data.get("conservation_level"),
        species_data.get("china_endemic", False),
        species_data.get("common", True),
        species_data.get("description"),
        species_data.get("distribution"),
        species_data.get("habitat"),
        species_data.get("voice"),
        species_data.get("similar_species")
    ))

    species_id = c.lastrowid
    conn.commit()
    conn.close()
    return species_id


def batch_add_species(species_list: List[Dict[str, Any]]) -> int:
    """批量添加物种"""
    conn = get_connection()
    c = conn.cursor()

    count = 0
    for species in species_list:
        try:
            c.execute("""
                INSERT INTO bird_species (
                    order_cn, order_en, family_cn, family_en,
                    genus_cn, genus_en, species_cn, species_en,
                    scientific_name, conservation_level,
                    china_endemic, common
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                species.get("order_cn"),
                species.get("order_en"),
                species.get("family_cn"),
                species.get("family_en"),
                species.get("genus_cn"),
                species.get("genus_en"),
                species.get("species_cn"),
                species.get("species_en"),
                species.get("scientific_name"),
                species.get("conservation_level"),
                species.get("china_endemic", False),
                species.get("common", True)
            ))
            count += 1
        except sqlite3.IntegrityError:
            # 跳过重复的物种
            continue

    conn.commit()
    conn.close()
    return count


# 初始化数据库
init_species_db()
