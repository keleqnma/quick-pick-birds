"""
测试配置文件
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_image_path(tmp_path):
    """创建临时图片文件用于测试"""
    # 创建一个简单的测试文件
    test_file = tmp_path / "test_image.jpg"
    test_file.write_bytes(b"fake image data")
    return str(test_file)


@pytest.fixture
def sample_folder_path(tmp_path):
    """创建临时文件夹用于测试"""
    # 创建一些测试文件
    for i in range(3):
        (tmp_path / f"photo_{i}.jpg").write_bytes(b"fake image data")
    return str(tmp_path)
