"""
大模型鸟类识别 API - 使用配置的 LLM API 进行鸟类识别
"""
import os
import base64
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

router = APIRouter()


class LLMConfig(BaseModel):
    """LLM API 配置"""
    base_url: str = "https://api.openai.com/v1"
    api_key: str
    model: str = "gpt-4o"
    timeout: int = 60
    system_prompt: Optional[str] = None


class TestConnectionRequest(BaseModel):
    """测试连接请求"""
    base_url: str
    api_key: str
    model: str
    timeout: int = 30


class BirdDetection(BaseModel):
    """鸟类检测结果"""
    species_cn: str
    species_en: str
    confidence: float
    description: Optional[str] = None
    behavior: Optional[str] = None


class LLMIdentifyRequest(BaseModel):
    """LLM 识别请求"""
    image_path: str
    config: LLMConfig


class LLMIdentifyResponse(BaseModel):
    """LLM 识别响应"""
    has_bird: bool
    detections: List[BirdDetection]
    raw_response: str
    description: Optional[str] = None


def encode_image_to_base64(image_path: str) -> str:
    """将图片编码为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_media_type(image_path: str) -> str:
    """根据文件扩展名获取媒体类型"""
    ext = os.path.splitext(image_path)[1].lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
    }
    return media_types.get(ext, 'image/jpeg')


async def call_llm_api(image_base64: str, config: LLMConfig) -> str:
    """调用 LLM API 进行图像识别"""

    default_prompt = """你是一位专业的鸟类学家和观鸟专家。请仔细分析这张照片，识别其中的鸟类。

请按照以下格式返回 JSON：
{
    "has_bird": true/false,
    "detections": [
        {
            "species_cn": "中文名称",
            "species_en": "English Name",
            "scientific_name": "学名 (如有把握)",
            "confidence": 0.0-1.0,
            "description": "外观特征描述",
            "behavior": "行为观察 (如有)"
        }
    ],
    "notes": "其他观察说明"
}

如果照片中没有鸟或无法识别，返回 {"has_bird": false, "detections": []}"""

    prompt = config.system_prompt if config.system_prompt else default_prompt

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.api_key}"
    }

    # 构建请求体（OpenAI 兼容格式）
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{get_media_type(image_base64)};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1
    }

    # 处理不同 API 端点的格式差异
    if "anthropic" in config.base_url.lower():
        headers["x-api-key"] = config.api_key
        headers["anthropic-version"] = "2023-06-01"
        payload = {
            "model": config.model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": get_media_type(image_base64),
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }

    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()

            # 解析响应
            if "anthropic" in config.base_url.lower():
                content = result.get("content", [{}])[0].get("text", "")
            else:
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            return content

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="API 请求超时")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"API 请求失败：{str(e)}")


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """解析 LLM 返回的 JSON 响应"""
    try:
        # 尝试提取 JSON 部分
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            return {"has_bird": False, "detections": [], "raw_response": response_text}
    except json.JSONDecodeError:
        return {"has_bird": False, "detections": [], "raw_response": response_text}


@router.post("/llm-identify")
async def llm_identify_bird(request: LLMIdentifyRequest) -> LLMIdentifyResponse:
    """
    使用大模型 API 识别照片中的鸟类
    """
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=400, detail="图片文件不存在")

    # 编码图片
    try:
        image_base64 = encode_image_to_base64(request.image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片编码失败：{str(e)}")

    # 调用 LLM API
    try:
        llm_response = await call_llm_api(image_base64, request.config)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API 调用失败：{str(e)}")

    # 解析响应
    parsed = parse_llm_response(llm_response)

    has_bird = parsed.get("has_bird", False)
    detections_data = parsed.get("detections", [])

    detections = [
        BirdDetection(
            species_cn=d.get("species_cn", "未知"),
            species_en=d.get("species_en", "Unknown"),
            confidence=float(d.get("confidence", 0)),
            description=d.get("description"),
            behavior=d.get("behavior")
        )
        for d in detections_data
    ]

    return LLMIdentifyResponse(
        has_bird=has_bird,
        detections=detections,
        raw_response=llm_response,
        description=parsed.get("description")
    )


@router.post("/llm-identify-batch")
async def llm_identify_batch(request: Dict[str, Any]):
    """
    批量使用大模型识别鸟类
    """
    image_paths = request.get("image_paths", [])
    config = LLMConfig(**request.get("config", {}))

    results = []
    for path in image_paths[:10]:  # 限制每次最多 10 张
        try:
            req = LLMIdentifyRequest(image_path=path, config=config)
            result = await llm_identify_bird(req)
            results.append({
                "image_path": path,
                "has_bird": result.has_bird,
                "detections": [d.dict() for d in result.detections]
            })
        except Exception as e:
            results.append({
                "image_path": path,
                "error": str(e)
            })

    return {"results": results}


@router.post("/test-connection")
async def test_connection(request: TestConnectionRequest) -> Dict[str, str]:
    """
    测试 LLM API 连接是否正常
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {request.api_key}"
    }

    base_url = request.base_url.rstrip('/')
    details = []
    details.append(f"=== 开始测试 LLM 连接 ===")
    details.append(f"Base URL: {base_url}")
    details.append(f"Model: {request.model}")
    details.append(f"Timeout: {request.timeout}")

    # 尝试调用 models 端点（轻量级测试）
    async with httpx.AsyncClient(timeout=request.timeout) as client:
        try:
            # 先尝试 /models 端点（如果支持）
            models_url = f"{base_url}/models"
            details.append(f"发送 GET 请求到：{models_url}")

            response = await client.get(models_url, headers=headers)

            details.append(f"GET /models 响应状态码：{response.status_code}")
            details.append(f"GET /models 响应内容：{response.text[:500]}")

            if response.status_code == 200:
                details.append("连接成功")
                return {"status": "success", "message": "连接成功", "details": "\n".join(details)}

            # 如果 /models 不支持，尝试一个简单的 chat completions 请求
            if response.status_code in [404, 405]:
                chat_payload = {
                    "model": request.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                chat_url = f"{base_url}/chat/completions"
                details.append(f"发送 POST 请求到：{chat_url}")
                details.append(f"请求体：{json.dumps(chat_payload, ensure_ascii=False)}")

                chat_response = await client.post(
                    chat_url,
                    headers=headers,
                    json=chat_payload
                )
                details.append(f"POST /chat/completions 响应状态码：{chat_response.status_code}")
                details.append(f"POST /chat/completions 响应内容：{chat_response.text[:500]}")

                if chat_response.status_code == 200:
                    return {"status": "success", "message": "连接成功", "details": "\n".join(details)}
                else:
                    return {
                        "status": "error",
                        "message": f"连接失败：{chat_response.status_code}",
                        "details": "\n".join(details),
                        "response_body": chat_response.text[:500]
                    }

            return {
                "status": "error",
                "message": f"连接失败：{response.status_code}",
                "details": "\n".join(details)
            }

        except httpx.TimeoutException:
            details.append("请求超时")
            return {"status": "error", "message": "请求超时", "details": "\n".join(details)}
        except httpx.RequestError as e:
            details.append(f"请求失败：{str(e)}")
            return {"status": "error", "message": f"请求失败：{str(e)}", "details": "\n".join(details)}
        except Exception as e:
            details.append(f"未知错误：{str(e)}")
            return {"status": "error", "message": f"未知错误：{str(e)}", "details": "\n".join(details)}
