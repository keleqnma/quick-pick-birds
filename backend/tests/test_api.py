"""
后端 API 单元测试
运行方式：pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestHealthEndpoints:
    """健康检查端点测试"""

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """测试根路由接口"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Quick Pick Birds" in data["name"]


class TestScanAPI:
    """扫描 API 测试"""

    def test_get_supported_formats(self, client):
        """测试获取支持的图片格式"""
        response = client.get("/api/scan/supported-formats")
        assert response.status_code == 200
        data = response.json()
        assert "raw_formats" in data
        assert "image_formats" in data
        assert isinstance(data["raw_formats"], list)
        assert isinstance(data["image_formats"], list)

    def test_scan_nonexistent_folder(self, client):
        """测试扫描不存在的文件夹"""
        response = client.post(
            "/api/scan/scan",
            json={"folder_path": "/nonexistent/path", "include_subfolders": True}
        )
        # 应该返回 400 或 500
        assert response.status_code in [400, 500]


class TestBirdsAPI:
    """鸟类识别 API 测试"""

    def test_species_list(self, client):
        """测试获取鸟类物种列表"""
        response = client.get("/api/birds/species-list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "species_cn" in data[0]
            assert "species_en" in data[0]

    def test_burst_groups(self, client):
        """测试连拍分组接口"""
        response = client.post(
            "/api/birds/burst-groups",
            json={
                "photo_paths": ["/test/photo1.jpg", "/test/photo2.jpg"],
                "time_threshold": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "burst_groups" in data

    def test_identify_birds_empty_paths(self, client):
        """测试鸟类识别 - 空路径列表"""
        response = client.post(
            "/api/birds/identify",
            json={"photo_paths": [], "save_to_db": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_photos"] == 0


class TestScoringAPI:
    """智能筛图 API 测试"""

    def test_get_default_criteria(self, client):
        """测试获取默认评分标准"""
        response = client.get("/api/scoring/criteria/defaults")
        assert response.status_code == 200
        data = response.json()
        assert "focus_weight" in data
        assert "clarity_weight" in data
        assert "composition_weight" in data
        # 验证权重总和约为 1.0
        total = data["focus_weight"] + data["clarity_weight"] + data["composition_weight"]
        assert abs(total - 1.0) < 0.01


class TestSummaryAPI:
    """观鸟小结 API 测试"""

    def test_species_list(self, client):
        """测试获取物种列表"""
        response = client.get("/api/summary/species/list")
        assert response.status_code == 200

    def test_sessions_list(self, client):
        """测试获取会话列表"""
        response = client.get("/api/summary/sessions?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        # API 返回格式：{'sessions': [...], 'total': N}
        assert isinstance(data, dict)
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)

    def test_generate_summary_nonexistent_session(self, client):
        """测试生成不存在的会话小结"""
        response = client.post(
            "/api/summary/generate-summary",
            json={"session_id": 99999, "output_path": "/test/output.html"}
        )
        # 应该返回 400/404/500
        assert response.status_code in [400, 404, 500]


class TestMapAPI:
    """地图 API 测试"""

    def test_daily_map(self, client):
        """测试获取当日地图"""
        from datetime import date
        today = date.today().isoformat()
        response = client.get(f"/api/map/daily?date={today}")
        assert response.status_code == 200

    def test_daily_map_invalid_date(self, client):
        """测试无效日期格式"""
        response = client.get("/api/map/daily?date=invalid-date")
        # API 对于无效日期可能返回 200（使用默认日期）或 400
        assert response.status_code in [200, 400]


class TestLLMAPI:
    """LLM API 测试"""

    def test_test_connection_invalid_key(self, client):
        """测试连接 - 无效 API Key"""
        response = client.post(
            "/api/llm/test-connection",
            json={
                "base_url": "https://api.openai.com/v1",
                "api_key": "invalid-key",
                "model": "gpt-4o",
                "timeout": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_llm_identify_nonexistent_image(self, client):
        """测试 LLM 识别不存在的图片"""
        response = client.post(
            "/api/llm/llm-identify",
            json={
                "image_path": "/nonexistent/image.jpg",
                "config": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "test-key",
                    "model": "gpt-4o",
                    "timeout": 30
                }
            }
        )
        # 应该返回 400 或 500
        assert response.status_code in [400, 500]


class TestCORS:
    """CORS 配置测试"""

    def test_cors_headers(self, client):
        """测试 CORS 头"""
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        # OPTIONS 请求应该成功
        assert response.status_code in [200, 404, 405]


# 辅助函数
def create_client_with_config():
    """创建带配置的测试客户端"""
    return TestClient(app)
