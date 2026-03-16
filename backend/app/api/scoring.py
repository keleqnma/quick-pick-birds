"""
照片质量评分 API - 使用 LLM 评估照片质量
"""
import os
import base64
import httpx
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from app.db import database

router = APIRouter()

# 默认评分权重
DEFAULT_WEIGHTS = {
    "focus": 0.40,      # 对焦准确性（鸟眼清晰）
    "clarity": 0.35,    # 鸟体清晰度/锐度
    "composition": 0.25 # 构图/美学
}


class ScoringCriteria(BaseModel):
    """评分权重配置"""
    focus_weight: float = 0.40
    clarity_weight: float = 0.35
    composition_weight: float = 0.25

    def get_weights(self) -> Dict[str, float]:
        return {
            "focus": self.focus_weight,
            "clarity": self.clarity_weight,
            "composition": self.composition_weight
        }


class LLMConfig(BaseModel):
    """LLM API 配置"""
    base_url: str = "https://api.openai.com/v1"
    api_key: str
    model: str = "gpt-4o"
    timeout: int = 60
    system_prompt: Optional[str] = None


class ScoringRequest(BaseModel):
    """评分请求"""
    image_paths: List[str]
    criteria: Optional[ScoringCriteria] = None
    llm_config: Optional[LLMConfig] = None
    session_id: Optional[int] = None  # 可选的会话 ID，用于关联数据库记录
    save_to_db: bool = True  # 是否保存到数据库
    enable_validation: bool = True  # 是否启用幻觉校验
    max_retries: int = 2  # 最大重试次数


class PhotoScore(BaseModel):
    """单张照片评分结果"""
    image_path: str
    overall_score: float  # 0-100
    focus_score: float
    clarity_score: float
    composition_score: float
    explanation: str
    is_recommended: bool = False


class ScoringResponse(BaseModel):
    """批量评分响应"""
    scores: List[PhotoScore]
    total: int
    recommended_count: int


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


def build_scoring_prompt(criteria: ScoringCriteria) -> str:
    """构建评分 Prompt"""
    weights = criteria.get_weights()
    return f"""你是一位专业的生态摄影师和观鸟专家，拥有多年鸟类摄影评审经验。请评估这张照片的质量。

## 评分维度（每项 0-100 分）

1. **对焦准确性**（权重：{weights['focus']*100:.0f}%）
   - 鸟眼是否清晰锐利
   - 焦点是否准确落在眼部
   - 有无跑焦或对焦不实

2. **主体清晰度**（权重：{weights['clarity']*100:.0f}%）
   - 鸟体羽毛细节是否清晰
   - 有无运动模糊或手抖
   - 图像锐度和解析力

3. **构图美学**（权重：{weights['composition']*100:.0f}%）
   - 主体位置和视觉平衡
   - 背景简洁度和干扰程度
   - 画面整体美感和艺术性

## 输出要求

请严格按照以下 JSON 格式返回：
{{
    "focus_score": 85,
    "clarity_score": 78,
    "composition_score": 90,
    "overall_score": 84,
    "explanation": "鸟眼清晰对焦准确，主体羽毛细节丰富，背景略显杂乱但不影响主体..."
}}

如果没有鸟或照片质量极差，也请给出各项评分（可能很低）并说明原因。"""


async def call_scoring_api(image_base64: str, media_type: str, config: LLMConfig, criteria: ScoringCriteria) -> str:
    """调用 LLM API 进行评分"""
    prompt = build_scoring_prompt(criteria)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.api_key}"
    }

    # 构建请求体（OpenAI 格式）
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的生态摄影师和观鸟专家，擅长评估鸟类摄影作品的质量。"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1
    }

    # 处理 Anthropic API 格式
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
                                "media_type": media_type,
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


def parse_score_response(response_text: str) -> Dict[str, Any]:
    """解析 LLM 返回的评分 JSON"""
    try:
        # 尝试提取 JSON 部分
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1

        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            return {
                "focus_score": float(data.get("focus_score", 50)),
                "clarity_score": float(data.get("clarity_score", 50)),
                "composition_score": float(data.get("composition_score", 50)),
                "overall_score": float(data.get("overall_score", 50)),
                "explanation": data.get("explanation", "")
            }
        else:
            return {
                "focus_score": 50,
                "clarity_score": 50,
                "composition_score": 50,
                "overall_score": 50,
                "explanation": response_text
            }
    except (json.JSONDecodeError, ValueError):
        return {
            "focus_score": 50,
            "clarity_score": 50,
            "composition_score": 50,
            "overall_score": 50,
            "explanation": response_text
        }


def validate_score_response(score_data: Dict[str, Any]) -> tuple:
    """
    校验评分响应，防止 LLM 幻觉
    返回 (is_valid, error_message)
    """
    # 校验各项分数是否在 0-100 范围内
    for key in ["focus_score", "clarity_score", "composition_score", "overall_score"]:
        value = score_data.get(key)
        if value is None:
            return False, f"{key} 缺失"
        if not isinstance(value, (int, float)):
            return False, f"{key} 类型错误，应为数字"
        if value < 0 or value > 100:
            return False, f"{key} 超出范围 (0-100): {value}"

    # 校验总分是否合理（应该接近各分项的加权和）
    expected_overall = (
        score_data["focus_score"] * 0.4 +
        score_data["clarity_score"] * 0.35 +
        score_data["composition_score"] * 0.25
    )
    # 允许 15 分的误差（LLM 可能使用不同的权重计算）
    if abs(score_data["overall_score"] - expected_overall) > 15:
        return False, f"总分 {score_data['overall_score']} 与分项计算结果 {expected_overall:.1f} 差异过大"

    # 校验评语是否存在且合理
    explanation = score_data.get("explanation", "")
    if not explanation or len(explanation) < 10:
        return False, "评语过短或缺失"

    # 校验是否包含明显的幻觉内容
    hallucination_keywords = ["无法判断", "看不到图片", "图像加载失败", "没有鸟"]
    for keyword in hallucination_keywords:
        if keyword in explanation.lower():
            return False, f"LLM 可能产生幻觉：{keyword}"

    return True, ""


def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """计算加权总分"""
    return (
        scores.get("focus_score", 0) * weights.get("focus", 0.4) +
        scores.get("clarity_score", 0) * weights.get("clarity", 0.35) +
        scores.get("composition_score", 0) * weights.get("composition", 0.25)
    )


@router.post("/batch-score")
async def batch_score(request: ScoringRequest) -> ScoringResponse:
    """
    批量评分照片质量

    使用 LLM API 评估每张照片的：
    - 对焦准确性（鸟眼清晰度）
    - 主体清晰度/锐度
    - 构图美观度

    并根据用户配置的权重计算总分
    """
    if not request.image_paths:
        raise HTTPException(status_code=400, detail="请提供照片路径列表")

    # 使用默认配置
    criteria = request.criteria or ScoringCriteria()
    weights = criteria.get_weights()

    # LLM 配置
    if not request.llm_config or not request.llm_config.api_key:
        # 尝试从环境变量获取
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="请配置 LLM API Key")
        llm_config = LLMConfig(
            api_key=api_key,
            base_url=request.llm_config.base_url if request.llm_config else "https://api.openai.com/v1",
            model=request.llm_config.model if request.llm_config else "gpt-4o",
            timeout=request.llm_config.timeout if request.llm_config else 60
        )
    else:
        llm_config = request.llm_config

    scores = []
    recommended_count = 0

    # 批量处理（限制数量避免超时）
    max_photos = 20
    image_paths = request.image_paths[:max_photos]

    for image_path in image_paths:
        if not os.path.exists(image_path):
            scores.append(PhotoScore(
                image_path=image_path,
                overall_score=0,
                focus_score=0,
                clarity_score=0,
                composition_score=0,
                explanation="文件不存在",
                is_recommended=False
            ))
            continue

        try:
            # 使用带重试和校验的评分函数
            photo_score = await score_photo_with_retry(
                image_path=image_path,
                llm_config=llm_config,
                criteria=criteria,
                weights=weights,
                enable_validation=request.enable_validation,
                max_retries=request.max_retries
            )
            scores.append(photo_score)

            if photo_score.is_recommended:
                recommended_count += 1

        except HTTPException:
            raise
        except Exception as e:
            scores.append(PhotoScore(
                image_path=image_path,
                overall_score=0,
                focus_score=0,
                clarity_score=0,
                composition_score=0,
                explanation=f"评分失败：{str(e)}",
                is_recommended=False
            ))

    # 保存到数据库
    if request.save_to_db and request.session_id:
        try:
            # 更新照片表中的评分信息
            for score in scores:
                conn = database.get_connection()
                c = conn.cursor()
                c.execute("""
                    UPDATE photos SET
                        quality_score = ?,
                        is_recommended = ?,
                        scoring_explanation = ?
                    WHERE file_path = ? AND session_id = ?
                """, (score.overall_score, score.is_recommended, score.explanation, score.image_path, request.session_id))
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"评分数据库保存失败：{str(e)}")

    # 按总分排序
    scores.sort(key=lambda x: x.overall_score, reverse=True)

    return ScoringResponse(
        scores=scores,
        total=len(scores),
        recommended_count=recommended_count
    )


async def score_photo_with_retry(
    image_path: str,
    llm_config: LLMConfig,
    criteria: ScoringCriteria,
    weights: Dict[str, float],
    enable_validation: bool = True,
    max_retries: int = 2
) -> PhotoScore:
    """
    对单张照片进行评分，带重试和校验机制
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            # 编码图片
            image_base64 = encode_image_to_base64(image_path)
            media_type = get_media_type(image_path)

            # 调用评分 API
            response_text = await call_scoring_api(image_base64, media_type, llm_config, criteria)

            # 解析评分
            score_data = parse_score_response(response_text)

            # 校验响应（防止 LLM 幻觉）
            if enable_validation:
                is_valid, error_msg = validate_score_response(score_data)
                if not is_valid:
                    if attempt < max_retries:
                        # 等待后重试
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    else:
                        # 校验失败但不再重试，使用计算后的分数
                        score_data["explanation"] += f" [校验警告：{error_msg}]"

            # 计算加权总分
            overall = calculate_weighted_score(score_data, weights)

            # 判定是否推荐（总分 >= 75）
            is_recommended = overall >= 75

            return PhotoScore(
                image_path=image_path,
                overall_score=round(overall, 1),
                focus_score=round(score_data["focus_score"], 1),
                clarity_score=round(score_data["clarity_score"], 1),
                composition_score=round(score_data["composition_score"], 1),
                explanation=score_data["explanation"],
                is_recommended=is_recommended
            )

        except HTTPException as e:
            last_error = e
            if e.status_code >= 500 and attempt < max_retries:
                # 服务器错误，重试
                await asyncio.sleep(2 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                await asyncio.sleep(1 * (attempt + 1))
                continue

    # 所有重试失败
    return PhotoScore(
        image_path=image_path,
        overall_score=0,
        focus_score=0,
        clarity_score=0,
        composition_score=0,
        explanation=f"评分失败：{str(last_error)}",
        is_recommended=False
    )


@router.get("/criteria/defaults")
async def get_default_criteria():
    """获取默认评分权重配置"""
    return {
        "focus_weight": DEFAULT_WEIGHTS["focus"],
        "clarity_weight": DEFAULT_WEIGHTS["clarity"],
        "composition_weight": DEFAULT_WEIGHTS["composition"]
    }
