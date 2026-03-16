"""
观测清单 API - 记录每次观鸟活动的完整鸟种列表
参照 eBird Checklist 功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
sys.path.append("..")
from app.db import database as db

router = APIRouter()


# ==================== Request/Response Models ====================

class ChecklistItem(BaseModel):
    """清单项 - 单个鸟种记录"""
    species_cn: str
    species_en: Optional[str] = None
    scientific_name: Optional[str] = None
    count: int = 1  # 观测到的数量
    sex: Optional[str] = None  # 性别 (雄/雌/未知)
    age: Optional[str] = None  # 年龄 (成鸟/亚成/幼鸟)
    behavior: Optional[str] = None  # 行为 (觅食/鸣叫/飞行等)
    breeding_code: Optional[str] = None  # 繁殖代码 (用于繁殖期观测)
    notes: Optional[str] = None  # 备注


class ChecklistCreate(BaseModel):
    """创建观测清单"""
    checklist_date: str  # 观测日期 ISO format
    location_name: str  # 地点名称
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    start_time: Optional[str] = None  # 开始时间
    duration_minutes: Optional[int] = None  # 观测时长 (分钟)
    protocol: str = "incidental"  # 观测类型：incidental (偶然), traveling (行进), stationary (定点)
    effort_distance_km: Optional[float] = None  # 行进距离 (km)
    observer_name: Optional[str] = None  # 观察者姓名
    weather: Optional[str] = None  # 天气状况
    temperature: Optional[float] = None  # 温度
    wind: Optional[str] = None  # 风力
    items: List[ChecklistItem] = []  # 鸟种列表
    notes: Optional[str] = None  # 总备注


class ChecklistUpdate(BaseModel):
    """更新观测清单"""
    location_name: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    protocol: Optional[str] = None
    effort_distance_km: Optional[float] = None
    observer_name: Optional[str] = None
    weather: Optional[str] = None
    temperature: Optional[float] = None
    wind: Optional[str] = None
    notes: Optional[str] = None


class ChecklistResponse(BaseModel):
    """观测清单响应"""
    id: int
    checklist_date: str
    location_name: str
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    start_time: Optional[str]
    duration_minutes: Optional[int]
    protocol: str
    effort_distance_km: Optional[float]
    observer_name: Optional[str]
    weather: Optional[str]
    temperature: Optional[float]
    wind: Optional[str]
    total_species: int
    total_individuals: int
    notes: Optional[str]
    created_at: str
    items: List[Dict[str, Any]]


# ==================== API Endpoints ====================

@router.post("/checklist", response_model=Dict[str, Any])
async def create_checklist(data: ChecklistCreate):
    """
    创建新的观测清单

    参照 eBird Checklist，记录一次完整的观鸟活动中的所有鸟种
    """
    try:
        # 创建清单主记录
        checklist_id = db.create_checklist(
            checklist_date=data.checklist_date,
            location_name=data.location_name,
            gps_lat=data.gps_lat,
            gps_lng=data.gps_lng,
            start_time=data.start_time,
            duration_minutes=data.duration_minutes,
            protocol=data.protocol,
            effort_distance_km=data.effort_distance_km,
            observer_name=data.observer_name,
            weather=data.weather,
            temperature=data.temperature,
            wind=data.wind,
            notes=data.notes
        )

        # 添加清单项
        if data.items:
            items_data = []
            for item in data.items:
                items_data.append({
                    "checklist_id": checklist_id,
                    "species_cn": item.species_cn,
                    "species_en": item.species_en,
                    "scientific_name": item.scientific_name,
                    "count": item.count,
                    "sex": item.sex,
                    "age": item.age,
                    "behavior": item.behavior,
                    "breeding_code": item.breeding_code,
                    "notes": item.notes
                })
            db.save_checklist_items_batch(items_data)

        # 获取完整清单
        checklist = db.get_checklist_with_items(checklist_id)

        return {
            "success": True,
            "checklist_id": checklist_id,
            "data": checklist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checklist/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(checklist_id: int):
    """获取观测清单详情"""
    checklist = db.get_checklist_with_items(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="清单不存在")
    return checklist


@router.get("/checklists")
async def list_checklists(
    year: Optional[int] = None,
    month: Optional[int] = None,
    location: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    获取观测清单列表

    - year: 按年份筛选
    - month: 按月份筛选
    - location: 按地点筛选 (模糊匹配)
    """
    checklists = db.list_checklists(
        year=year,
        month=month,
        location=location,
        limit=limit,
        offset=offset
    )
    return {"checklists": checklists, "total": len(checklists)}


@router.put("/checklist/{checklist_id}")
async def update_checklist(checklist_id: int, data: ChecklistUpdate):
    """更新观测清单"""
    checklist = db.get_checklist(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="清单不存在")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        db.update_checklist(checklist_id, **update_data)

    return {"success": True, "data": db.get_checklist_with_items(checklist_id)}


@router.delete("/checklist/{checklist_id}")
async def delete_checklist(checklist_id: int):
    """删除观测清单（级联删除清单项）"""
    checklist = db.get_checklist(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="清单不存在")

    db.delete_checklist(checklist_id)
    return {"success": True, "message": "清单已删除"}


@router.post("/checklist/{checklist_id}/items")
async def add_checklist_item(checklist_id: int, item: ChecklistItem):
    """向观测清单添加鸟种"""
    checklist = db.get_checklist(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="清单不存在")

    item_id = db.save_checklist_item(
        checklist_id=checklist_id,
        species_cn=item.species_cn,
        species_en=item.species_en,
        scientific_name=item.scientific_name,
        count=item.count,
        sex=item.sex,
        age=item.age,
        behavior=item.behavior,
        breeding_code=item.breeding_code,
        notes=item.notes
    )

    return {"success": True, "item_id": item_id}


@router.delete("/checklist/{checklist_id}/items/{item_id}")
async def delete_checklist_item(checklist_id: int, item_id: int):
    """从观测清单删除鸟种"""
    db.delete_checklist_item(item_id)
    return {"success": True, "message": "已删除"}


@router.get("/checklist/stats")
async def get_checklist_stats():
    """获取观测清单统计"""
    stats = db.get_checklist_stats()
    return stats


@router.get("/checklist/export/{checklist_id}")
async def export_checklist(checklist_id: int, format: str = "xlsx"):
    """导出观测清单为 Excel/CSV"""
    from fastapi.responses import Response
    import io

    checklist = db.get_checklist_with_items(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="清单不存在")

    if format == "xlsx":
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "观测清单"

        # 表头
        headers = ["序号", "中文名", "英文名", "学名", "数量", "性别", "年龄", "行为", "备注"]
        ws.append(headers)

        # 数据
        for idx, item in enumerate(checklist.get("items", []), 1):
            ws.append([
                idx,
                item.get("species_cn", ""),
                item.get("species_en", ""),
                item.get("scientific_name", ""),
                item.get("count", 1),
                item.get("sex", ""),
                item.get("age", ""),
                item.get("behavior", ""),
                item.get("notes", "")
            ])

        # 添加清单信息
        ws.append([])
        ws.append(["观测日期", checklist.get("checklist_date", "")])
        ws.append(["地点", checklist.get("location_name", "")])
        ws.append(["观察时长 (分钟)", checklist.get("duration_minutes", "")])
        ws.append(["物种数", checklist.get("total_species", 0)])
        ws.append(["个体总数", checklist.get("total_individuals", 0)])

        # 保存到内存
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=checklist_{checklist_id}.xlsx"}
        )

    elif format == "csv":
        import csv

        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # 表头
        writer.writerow(["序号", "中文名", "英文名", "学名", "数量", "性别", "年龄", "行为", "备注"])

        # 数据
        for idx, item in enumerate(checklist.get("items", []), 1):
            writer.writerow([
                idx,
                item.get("species_cn", ""),
                item.get("species_en", ""),
                item.get("scientific_name", ""),
                item.get("count", 1),
                item.get("sex", ""),
                item.get("age", ""),
                item.get("behavior", ""),
                item.get("notes", "")
            ])

        return Response(
            content=buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=checklist_{checklist_id}.csv"}
        )

    else:
        raise HTTPException(status_code=400, detail="不支持的格式，仅支持 xlsx 和 csv")
