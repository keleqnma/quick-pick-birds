"""
Quick Pick Birds - 观鸟照片识别应用后端
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from typing import List, Optional

from app.api import scan, birds, map_endpoint, llm_identify, scoring, summary, export, stats


class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "Quick Pick Birds"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]
    UPLOAD_DIR: str = "./uploads"
    RAW_PHOTO_DIR: str = os.getenv("RAW_PHOTO_DIR", "")
    MODEL_PATH: str = "./models/bird_classifier.pth"

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="观鸟照片识别 API - 扫描 RAW 照片，识别鸟类，绘制观鸟地图",
    version="1.0.0"
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(scan.router, prefix="/api/scan", tags=["扫描"])
app.include_router(birds.router, prefix="/api/birds", tags=["鸟类识别"])
app.include_router(map_endpoint.router, prefix="/api/map", tags=["地图"])
app.include_router(llm_identify.router, prefix="/api/llm", tags=["大模型识别"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["智能筛图"])
app.include_router(summary.router, prefix="/api/summary", tags=["观鸟小结"])
app.include_router(export.router, prefix="/api/export", tags=["数据导出"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计图表"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "description": "观鸟照片识别 API - 扫描 RAW 照片，识别鸟类，绘制观鸟地图",
        "endpoints": [
            "/api/scan/scan - 扫描文件夹中的 RAW 照片",
            "/api/birds/list - 获取识别的鸟类列表",
            "/api/birds/identify - 识别照片中的鸟类",
            "/api/map/generate - 生成观鸟地图",
            "/api/map/daily - 获取当日的观鸟地图",
            "/api/scoring/batch-score - 批量评分照片质量",
            "/api/scoring/criteria/defaults - 获取默认评分权重",
            "/api/summary/generate-summary - 生成观鸟小结 HTML",
            "/api/summary/calendar/{year}/{month} - 获取日历数据",
            "/api/summary/sessions - 获取观测会话列表",
            "/api/summary/species/list - 获取物种列表",
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
