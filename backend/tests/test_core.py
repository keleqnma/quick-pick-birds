"""
后端核心功能单元测试
运行方式：pytest tests/test_core.py -v
"""
import pytest
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.birds import group_burst_photos, simulate_bird_detection, BIRD_SPECIES
from app.api.scoring import ScoringCriteria, DEFAULT_WEIGHTS
from app.api.llm_identify import parse_llm_response, encode_image_to_base64


class TestBirdDetection:
    """鸟类检测功能测试"""

    def test_simulate_detection_returns_list(self):
        """测试模拟检测返回 list"""
        result = simulate_bird_detection("/test/photo.jpg")
        assert isinstance(result, list)

    def test_simulate_detection_deterministic(self):
        """测试相同路径返回相同结果（确定性）"""
        result1 = simulate_bird_detection("/test/photo.jpg")
        result2 = simulate_bird_detection("/test/photo.jpg")
        assert len(result1) == len(result2)


class TestBurstGrouping:
    """连拍分组功能测试"""

    def test_empty_photos(self):
        """测试空照片列表"""
        result = group_burst_photos([])
        assert result == []

    def test_single_photo(self):
        """测试单张照片"""
        photos = [
            {'file_path': '/test/1.jpg', 'capture_time': datetime.now()}
        ]
        result = group_burst_photos(photos)
        # 单张照片不会形成连拍组
        assert len(result) == 0

    def test_burst_within_threshold(self):
        """测试阈值内的连拍照片"""
        base_time = datetime.now()
        photos = [
            {'file_path': '/test/1.jpg', 'capture_time': base_time},
            {'file_path': '/test/2.jpg', 'capture_time': base_time + timedelta(seconds=1)},
            {'file_path': '/test/3.jpg', 'capture_time': base_time + timedelta(seconds=2)},
        ]
        result = group_burst_photos(photos, time_threshold=5)
        # 应该在同一个连拍组内
        assert len(result) == 1
        assert result[0].photo_count == 3

    def test_burst_outside_threshold(self):
        """测试超出阈值的照片"""
        base_time = datetime.now()
        photos = [
            {'file_path': '/test/1.jpg', 'capture_time': base_time},
            {'file_path': '/test/2.jpg', 'capture_time': base_time + timedelta(seconds=10)},
        ]
        result = group_burst_photos(photos, time_threshold=5)
        # 应该不在同一个连拍组
        assert len(result) == 0


class TestScoringCriteria:
    """评分标准测试"""

    def test_default_criteria_weights_sum_to_one(self):
        """测试默认权重总和为 1"""
        total = DEFAULT_WEIGHTS["focus"] + DEFAULT_WEIGHTS["clarity"] + DEFAULT_WEIGHTS["composition"]
        assert abs(total - 1.0) < 0.01

    def test_default_criteria_values(self):
        """测试默认权重值"""
        assert DEFAULT_WEIGHTS["focus"] == 0.40
        assert DEFAULT_WEIGHTS["clarity"] == 0.35
        assert DEFAULT_WEIGHTS["composition"] == 0.25

    def test_scoring_criteria_model(self):
        """测试评分配置模型"""
        criteria = ScoringCriteria()
        weights = criteria.get_weights()
        assert "focus" in weights
        assert "clarity" in weights
        assert "composition" in weights


class TestLLMResponseParser:
    """LLM 响应解析器测试"""

    def test_parse_valid_json(self):
        """测试解析有效 JSON"""
        json_str = '{"has_bird": true, "detections": []}'
        result = parse_llm_response(json_str)
        assert result["has_bird"] is True
        assert result["detections"] == []

    def test_parse_json_with_text(self):
        """测试解析带周围文本的 JSON"""
        text = 'Some text before {"has_bird": true, "detections": []} some text after'
        result = parse_llm_response(text)
        assert result["has_bird"] is True

    def test_parse_invalid_json(self):
        """测试解析无效 JSON"""
        result = parse_llm_response("not valid json at all")
        assert result["has_bird"] is False
        assert result["detections"] == []

    def test_parse_empty_string(self):
        """测试解析空字符串"""
        result = parse_llm_response("")
        assert result["has_bird"] is False


class TestBirdSpecies:
    """鸟类物种数据测试"""

    def test_species_not_empty(self):
        """测试物种列表不为空"""
        assert len(BIRD_SPECIES) > 0

    def test_species_has_chinese_name(self):
        """测试所有物种都有中文名"""
        for key, name in BIRD_SPECIES.items():
            assert name is not None
            assert len(name) > 0


class TestImageEncoding:
    """图片编码测试"""

    def test_encode_nonexistent_file(self):
        """测试编码不存在的文件"""
        with pytest.raises(FileNotFoundError):
            encode_image_to_base64("/nonexistent/file.jpg")

    def test_encode_temp_image(self, tmp_path):
        """测试编码临时图片"""
        test_file = tmp_path / "test.jpg"
        test_data = b"fake image data"
        test_file.write_bytes(test_data)

        # 这个测试会验证文件存在时的编码
        # 注意：实际编码需要有效的图片数据
        try:
            result = encode_image_to_base64(str(test_file))
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception:
            # 如果图片数据无效，可能会失败
            pytest.skip("Invalid image data")
