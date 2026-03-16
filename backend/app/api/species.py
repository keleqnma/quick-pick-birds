"""
鸟类物种百科 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import sys
sys.path.append("..")
from app.db import species_db

router = APIRouter()


@router.get("/search")
async def search_species(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(50, description="返回数量限制")
):
    """
    搜索鸟类物种

    - **q**: 搜索关键词（支持中文名、学名、英文名）
    - **limit**: 返回结果数量限制
    """
    if not q or len(q) < 1:
        raise HTTPException(status_code=400, detail="搜索关键词至少 1 个字符")

    results = species_db.search_species(q, limit)
    return {"results": results, "total": len(results)}


@router.get("/species/{species_id}")
async def get_species(species_id: int):
    """获取物种详情"""
    species = species_db.get_species_by_id(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="物种不存在")
    return species


@router.get("/species")
async def list_species(
    family: Optional[str] = None,
    order: Optional[str] = None,
    common_only: bool = False,
    limit: int = 100,
    offset: int = 0
):
    """
    获取物种列表

    - **family**: 按科筛选
    - **order**: 按目筛选
    - **common_only**: 仅返回常见种
    """
    results = species_db.list_species(
        family=family,
        order=order,
        common_only=common_only,
        limit=limit,
        offset=offset
    )
    return {"results": results, "total": len(results)}


@router.get("/families")
async def list_families():
    """获取所有科列表"""
    families = species_db.list_families()
    return {"families": families}


@router.get("/orders")
async def list_orders():
    """获取所有目列表"""
    orders = species_db.list_orders()
    return {"orders": orders}


@router.get("/stats")
async def get_stats():
    """获取物种数据库统计"""
    stats = species_db.get_species_count()
    return stats


@router.get("/conservation-levels")
async def get_conservation_levels():
    """获取保护级别列表"""
    conn = species_db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM conservation_levels ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return {"levels": [dict(row) for row in rows]}


@router.post("/species")
async def add_species(species_data: Dict[str, Any]):
    """添加新物种"""
    required_fields = ["species_cn", "scientific_name"]
    for field in required_fields:
        if field not in species_data or not species_data[field]:
            raise HTTPException(status_code=400, detail=f"缺少必填字段：{field}")

    species_id = species_db.add_species(species_data)
    return {"success": True, "species_id": species_id}


@router.get("/species/{species_id}/similar")
async def get_similar_species(species_id: int):
    """获取相似物种"""
    species = species_db.get_species_by_id(species_id)
    if not species:
        raise HTTPException(status_code=404, detail="物种不存在")

    if not species.get("similar_species"):
        return {"similar_species": []}

    # 解析相似物种（假设存储的是物种 ID 列表，逗号分隔）
    similar_ids = [int(x.strip()) for x in str(species["similar_species"]).split(",") if x.strip()]
    similar_species = []

    for sid in similar_ids:
        s = species_db.get_species_by_id(sid)
        if s:
            similar_species.append(s)

    return {"similar_species": similar_species}
