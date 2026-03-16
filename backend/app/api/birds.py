"""
鸟类识别 API - 识别照片中的鸟类，支持连拍识别和品种识别
"""
import os
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib

from app.db import database

router = APIRouter()

# 模拟鸟类数据库 - 实际项目中会使用真实的 AI 模型
BIRD_SPECIES = {
    "sparrow": "麻雀",
    "pigeon": "鸽子",
    "crow": "乌鸦",
    "magpie": "喜鹊",
    "swallow": "燕子",
    "kingfisher": "翠鸟",
    "heron": "鹭鸟",
    "eagle": "鹰",
    "hawk": "隼",
    "parrot": "鹦鹉",
    "woodpecker": "啄木鸟",
    "hummingbird": "蜂鸟",
    "flamingo": "火烈鸟",
    "pelican": "鹈鹕",
    "owl": "猫头鹰",
}


class BirdDetection(BaseModel):
    """单次鸟类检测结果"""
    species_cn: str  # 中文名
    species_en: str  # 英文名
    confidence: float  # 置信度
    bounding_box: Optional[Dict[str, int]] = None  # 检测框


class BurstGroup(BaseModel):
    """连拍组"""
    group_id: str
    photo_count: int
    time_span_seconds: float
    primary_photo_path: str
    detections: List[BirdDetection]
    suggested_best: int  # 建议最佳照片索引


class BirdIdentifyRequest(BaseModel):
    """识别请求"""
    photo_paths: List[str]
    session_id: Optional[int] = None  # 可选的会话 ID，用于关联数据库记录
    save_to_db: bool = True  # 是否保存到数据库


class BirdIdentifyResponse(BaseModel):
    """识别响应"""
    total_photos: int
    photos_with_birds: int
    detections: List[BirdDetection]
    burst_groups: List[BurstGroup]
    identify_time: datetime
    session_id: Optional[int] = None  # 数据库会话 ID（如果传入了 session_id）


class BirdSpeciesResponse(BaseModel):
    """鸟类品种响应"""
    species_cn: str
    species_en: str
    photo_count: int
    first_seen: datetime
    last_seen: datetime
    locations: List[Dict[str, Any]]


def calculate_file_hash(file_path: str) -> str:
    """计算文件哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def simulate_bird_detection(file_path: str) -> List[BirdDetection]:
    """
    模拟鸟类检测 - 实际项目中会替换为真实的 AI 模型
    使用 YOLOv8 或 Faster R-CNN 等目标检测模型
    """
    # TODO: 集成真实的鸟类识别模型
    # 可以使用 transformers 库加载预训练的 ResNet 或 ViT 模型

    # 模拟返回 - 实际应该调用模型推理
    import random
    random.seed(len(file_path))  # 基于文件路径生成确定性结果

    has_bird = random.random() > 0.3  # 70% 概率有鸟
    if not has_bird:
        return []

    # 随机选择一种鸟
    species_en = random.choice(list(BIRD_SPECIES.keys()))
    confidence = 0.7 + random.random() * 0.28  # 0.7-0.98

    detection = BirdDetection(
        species_cn=BIRD_SPECIES[species_en],
        species_en=species_en,
        confidence=round(confidence, 3),
        bounding_box={
            "x": random.randint(100, 300),
            "y": random.randint(100, 400),
            "width": random.randint(50, 200),
            "height": random.randint(50, 200)
        }
    )

    return [detection]


def group_burst_photos(photos: List[Dict], time_threshold: int = 5) -> List[BurstGroup]:
    """
    将连拍照片分组
    连拍判定：同一时间附近（默认 5 秒内）连续拍摄的照片
    """
    if not photos:
        return []

    # 按拍摄时间排序
    sorted_photos = sorted(photos, key=lambda x: x.get('capture_time') or datetime.min)

    groups = []
    current_group = [sorted_photos[0]]

    for i in range(1, len(sorted_photos)):
        current_time = sorted_photos[i].get('capture_time')
        prev_time = sorted_photos[i-1].get('capture_time')

        if current_time and prev_time:
            time_diff = (current_time - prev_time).total_seconds()
            if time_diff <= time_threshold:
                current_group.append(sorted_photos[i])
            else:
                if len(current_group) > 1:
                    # 创建连拍组
                    group = create_burst_group(current_group)
                    groups.append(group)
                current_group = [sorted_photos[i]]
        else:
            current_group = [sorted_photos[i]]

    # 处理最后一组
    if len(current_group) > 1:
        group = create_burst_group(current_group)
        groups.append(group)

    return groups


def create_burst_group(photos: List[Dict]) -> BurstGroup:
    """创建连拍组"""
    group_id = hashlib.md5(
        str([p.get('file_path') for p in photos]).encode()
    ).hexdigest()[:8]

    times = [p.get('capture_time') for p in photos if p.get('capture_time')]
    time_span = (max(times) - min(times)).total_seconds() if times else 0

    # 找到建议的最佳照片（通常是第一张或中间张）
    suggested_best = len(photos) // 2

    return BurstGroup(
        group_id=group_id,
        photo_count=len(photos),
        time_span_seconds=time_span,
        primary_photo_path=photos[suggested_best].get('file_path', ''),
        detections=photos[0].get('detections', []),
        suggested_best=suggested_best
    )


@router.post("/identify")
async def identify_birds(request: BirdIdentifyRequest) -> BirdIdentifyResponse:
    """
    识别照片中的鸟类
    支持批量识别和连拍分组
    识别完成后自动保存到数据库
    """
    detections = []
    photos_with_birds = 0
    photo_data = []

    for file_path in request.photo_paths:
        if not os.path.exists(file_path):
            continue

        # 进行鸟类检测
        photo_detections = simulate_bird_detection(file_path)

        detection_info = {
            'file_path': file_path,
            'detections': photo_detections
        }
        photo_data.append(detection_info)

        if photo_detections:
            photos_with_birds += 1
            detections.extend(photo_detections)

    # 分组连拍照片
    burst_groups = group_burst_photos(photo_data)

    # 保存到数据库
    if request.save_to_db and request.session_id:
        try:
            # 为每个检测结果创建数据库记录
            detection_records = []
            for info in photo_data:
                if info['detections']:
                    # 查找对应的照片 ID
                    conn = database.get_connection()
                    c = conn.cursor()
                    c.execute("SELECT id FROM photos WHERE file_path = ?", (info['file_path'],))
                    row = c.fetchone()
                    conn.close()

                    if row:
                        photo_id = row[0]
                        for det in info['detections']:
                            detection_records.append({
                                'photo_id': photo_id,
                                'species_cn': det.species_cn,
                                'species_en': det.species_en,
                                'confidence': det.confidence,
                                'description': None,
                                'behavior': None
                            })

            if detection_records:
                database.save_detections_batch(detection_records)
        except Exception as e:
            print(f"数据库保存失败：{str(e)}")

    return BirdIdentifyResponse(
        total_photos=len(request.photo_paths),
        photos_with_birds=photos_with_birds,
        detections=detections,
        burst_groups=burst_groups,
        identify_time=datetime.now(),
        session_id=request.session_id
    )


@router.get("/species-list")
async def get_species_list():
    """获取所有支持的鸟类品种列表"""
    return [
        {"species_cn": name, "species_en": key}
        for key, name in BIRD_SPECIES.items()
    ]


@router.post("/detect-bird")
async def detect_bird_in_photo(file: UploadFile = File(...)):
    """
    上传单张照片进行鸟类检测
    """
    # 保存上传的文件
    temp_path = f"./temp/{file.filename}"
    os.makedirs("./temp", exist_ok=True)

    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 进行检测
    detections = simulate_bird_detection(temp_path)

    # 清理临时文件
    os.remove(temp_path)

    return {
        "filename": file.filename,
        "has_bird": len(detections) > 0,
        "detections": detections
    }


class BurstGroupRequest(BaseModel):
    """连拍分组请求"""
    photo_paths: List[str]
    time_threshold: int = 5


@router.post("/burst-groups")
async def get_burst_groups(request: BurstGroupRequest):
    """
    分析照片的连拍分组
    """
    # 模拟照片数据
    photo_data = []
    for path in request.photo_paths:
        photo_data.append({
            'file_path': path,
            'capture_time': datetime.now() - timedelta(seconds=len(photo_data) * 2)
        })

    groups = group_burst_photos(photo_data, request.time_threshold)
    return {"burst_groups": [g.dict() for g in groups]}
