"""
文件夹扫描 API - 扫描 RAW 照片
"""
import os
import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import exifread
from PIL import Image
import rawpy
import imageio

from app.db import database

router = APIRouter()

# 支持的 RAW 格式（扩展）
SUPPORTED_RAW_FORMATS = {
    '.cr2', '.cr3',      # Canon
    '.nef',              # Nikon
    '.arw',              # Sony
    '.raf',              # Fujifilm
    '.orf',              # Olympus
    '.pef',              # Pentax
    '.srw',              # Samsung
    '.dng',              # Adobe DNG
    '.rw2',              # Panasonic
    '.3fr',              # Hasselblad
    '.iiq',              # Phase One
    '.kdc',              # Kodak
    '.mrw',              # Minolta
    '.nrw',              # Nikon RAW2
    '.ptx',              # Pentax RAW
    '.r3d',              # RED
    '.raw',              # Generic RAW
    '.rwl',              # Leica RAW
    '.sr2',              # Sony RAW 2
    '.srf',              # Sony Raw Format
    '.x3f',              # Sigma RAW
}

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.heic'} | SUPPORTED_RAW_FORMATS


class PhotoInfo(BaseModel):
    """照片信息模型"""
    file_path: str
    file_name: str
    file_size: int
    capture_time: Optional[datetime] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    gps_alt: Optional[float] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[str] = None
    iso: Optional[int] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None
    is_raw: bool = False
    thumbnail_path: Optional[str] = None


class ScanRequest(BaseModel):
    """扫描请求"""
    folder_path: str
    include_subfolders: bool = True


class ScanResponse(BaseModel):
    """扫描响应"""
    total_photos: int
    raw_photos: int
    jpeg_photos: int
    photos_with_gps: int
    photos: List[PhotoInfo]
    scan_time: datetime
    error_files: List[str] = []
    session_id: Optional[int] = None  # 数据库会话 ID


def extract_gps_from_exif(exif_data: dict) -> tuple:
    """从 EXIF 数据中提取 GPS 信息"""
    try:
        if 'GPS GPSLatitude' in exif_data and 'GPS GPSLongitude' in exif_data:
            lat_ref = exif_data.get('GPS GPSLatRef', 'N').values
            lon_ref = exif_data.get('GPS GPSLonRef', 'E').values

            lat = exif_data['GPS GPSLatitude'].values
            lon = exif_data['GPS GPSLongitude'].values

            # 转换 GPS 坐标为十进制
            lat_decimal = lat[0][0]/lat[0][1] + lat[1][0]/(lat[1][1]*60) + lat[2][0]/(lat[2][1]*3600)
            lon_decimal = lon[0][0]/lon[0][1] + lon[1][0]/(lon[1][1]*60) + lon[2][0]/(lon[2][1]*3600)

            if lat_ref == 'S':
                lat_decimal = -lat_decimal
            if lon_ref == 'W':
                lon_decimal = -lon_decimal

            # 海拔
            alt = None
            if 'GPS GPSAltitude' in exif_data:
                alt_data = exif_data['GPS GPSAltitude'].values
                alt = alt_data[0][0] / alt_data[0][1]
                if 'GPS GPSAltitudeRef' in exif_data and exif_data['GPS GPSAltitudeRef'].values[0] == 1:
                    alt = -alt

            return lat_decimal, lon_decimal, alt
    except Exception as e:
        print(f"GPS 提取失败：{e}")

    return None, None, None


def extract_photo_metadata(file_path: str) -> Optional[PhotoInfo]:
    """提取照片元数据"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        is_raw = file_ext in SUPPORTED_RAW_FORMATS

        photo_info = PhotoInfo(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_size=os.path.getsize(file_path),
            is_raw=is_raw
        )

        # 提取 EXIF 数据
        exif_data = None

        if is_raw:
            # RAW 文件使用 rawpy 处理
            try:
                with rawpy.imread(file_path) as raw:
                    # 获取嵌入的 EXIF
                    exif_raw = raw.raw_image
                    # 尝试从文件中读取 EXIF
                    with open(file_path, 'rb') as f:
                        exif_data = exifread.process_file(f, stop_tag='Image Width', details=False)
            except Exception as e:
                print(f"RAW 处理失败 {file_path}: {e}")
                # 尝试直接读取 EXIF
                with open(file_path, 'rb') as f:
                    exif_data = exifread.process_file(f, details=False)
        else:
            # JPEG/PNG 使用 Pillow 处理
            try:
                with Image.open(file_path) as img:
                    exif_data = exifread.process_file(open(file_path, 'rb'), details=False)
            except Exception:
                with open(file_path, 'rb') as f:
                    exif_data = exifread.process_file(f, details=False)

        if exif_data:
            # 拍摄时间
            if 'EXIF DateTimeOriginal' in exif_data:
                try:
                    time_str = str(exif_data['EXIF DateTimeOriginal'])
                    photo_info.capture_time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
                except Exception:
                    pass

            # GPS 信息
            lat, lon, alt = extract_gps_from_exif(exif_data)
            photo_info.gps_lat = lat
            photo_info.gps_lon = lon
            photo_info.gps_alt = alt

            # 相机信息
            if 'Image Model' in exif_data:
                photo_info.camera_model = str(exif_data['Image Model'])

            # 镜头信息
            if 'EXIF LensModel' in exif_data:
                photo_info.lens_model = str(exif_data['EXIF LensModel'])

            # 拍摄参数
            if 'EXIF FocalLength' in exif_data:
                photo_info.focal_length = str(exif_data['EXIF FocalLength'])

            if 'EXIF ISOSpeedRatings' in exif_data:
                try:
                    photo_info.iso = int(exif_data['EXIF ISOSpeedRatings'].values[0])
                except Exception:
                    pass

            if 'EXIF FNumber' in exif_data:
                photo_info.aperture = f"f/{exif_data['EXIF FNumber']}"

            if 'EXIF ExposureTime' in exif_data:
                photo_info.shutter_speed = str(exif_data['EXIF ExposureTime'])

        return photo_info

    except Exception as e:
        print(f"处理文件失败 {file_path}: {e}")
        return None


def scan_folder(folder_path: str, include_subfolders: bool = True) -> List[PhotoInfo]:
    """扫描文件夹中的照片"""
    photos = []

    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail=f"文件夹不存在：{folder_path}")

    # 遍历文件夹
    if include_subfolders:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in SUPPORTED_IMAGE_FORMATS:
                    file_path = os.path.join(root, file)
                    photo_info = extract_photo_metadata(file_path)
                    if photo_info:
                        photos.append(photo_info)
    else:
        for file in os.listdir(folder_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in SUPPORTED_IMAGE_FORMATS:
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    photo_info = extract_photo_metadata(file_path)
                    if photo_info:
                        photos.append(photo_info)

    return photos


@router.post("/scan")
async def scan_photos(request: ScanRequest) -> ScanResponse:
    """
    扫描文件夹中的 RAW 照片
    扫描完成后自动保存到数据库
    """
    error_files = []

    try:
        photos = scan_folder(request.folder_path, request.include_subfolders)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"扫描失败：{str(e)}")

    # 统计
    raw_count = sum(1 for p in photos if p.is_raw)
    jpeg_count = len(photos) - raw_count
    gps_count = sum(1 for p in photos if p.gps_lat is not None)

    # 保存到数据库
    session_id = None
    try:
        # 创建会话记录
        session_id = database.create_session(
            folder_path=request.folder_path,
            total_photos=len(photos),
            notes=f"扫描 {raw_count} 张 RAW, {jpeg_count} 张 JPEG"
        )

        # 批量保存照片记录
        photos_data = []
        for photo in photos:
            photos_data.append({
                'session_id': session_id,
                'file_path': photo.file_path,
                'file_name': photo.file_name,
                'capture_time': photo.capture_time.isoformat() if photo.capture_time else None,
                'gps_lat': photo.gps_lat,
                'gps_lng': photo.gps_lon,
                'gps_alt': photo.gps_alt,
                'camera_model': photo.camera_model,
                'lens_model': photo.lens_model,
                'focal_length': photo.focal_length,
                'iso': photo.iso,
                'aperture': photo.aperture,
                'shutter_speed': photo.shutter_speed,
                'quality_score': None,
                'is_recommended': False,
                'scoring_explanation': None
            })

        if photos_data:
            database.save_photos_batch(photos_data)
    except Exception as e:
        error_files.append(f"数据库保存失败：{str(e)}")

    return ScanResponse(
        total_photos=len(photos),
        raw_photos=raw_count,
        jpeg_photos=jpeg_count,
        photos_with_gps=gps_count,
        photos=photos,
        scan_time=datetime.now(),
        error_files=error_files,
        session_id=session_id
    )


@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的照片格式"""
    return {
        "raw_formats": list(SUPPORTED_RAW_FORMATS),
        "image_formats": list(SUPPORTED_IMAGE_FORMATS)
    }
