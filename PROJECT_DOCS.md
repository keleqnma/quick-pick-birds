# Quick Pick Birds 项目文档

## 项目概述

Quick Pick Birds 是一款智能观鸟助手应用，帮助观鸟爱好者管理、筛选和分析观鸟照片。

### 核心功能

1. **照片扫描** - 扫描文件夹中的 RAW/JPEG 照片，提取 EXIF 信息（GPS、拍摄参数等）
2. **鸟类识别** - 使用大模型 API 识别照片中的鸟类 species
3. **智能筛图** - 基于 LLM 评估照片质量（对焦、清晰度、构图），支持权重调整
4. **观鸟地图** - 在地图上显示观测点和物种分布
5. **观鸟日历** - 年/月/日视图展示观测记录
6. **小结生成** - 生成精美的 HTML 观鸟小结

---

## 技术架构

### 后端技术栈

| 组件 | 技术 |
|------|------|
| 框架 | FastAPI 0.109.0 + Uvicorn |
| 数据库 | SQLite3 |
| 图像处理 | Pillow, rawpy, exifread |
| HTTP 客户端 | httpx |
| 地图生成 | folium |
| LLM 集成 | OpenAI/Anthropic 等 API |

### 前端技术栈

| 组件 | 技术 |
|------|------|
| 框架 | React 19 + TypeScript |
| 路由 | React Router DOM v7 |
| 构建工具 | Vite |
| 桌面端 | Electron 41 |
| 地图 | Leaflet + react-leaflet |

---

## 项目结构

```
quick-pick-birds/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── scan.py          # 照片扫描 API
│   │   │   ├── birds.py         # 鸟类识别 API
│   │   │   ├── map_endpoint.py  # 地图生成 API
│   │   │   ├── llm_identify.py  # LLM 识别 API
│   │   │   ├── scoring.py       # 智能筛图 API (新增)
│   │   │   └── summary.py       # 小结生成 API (新增)
│   │   ├── db/
│   │   │   └── database.py      # SQLite 数据库 (新增)
│   │   └── main.py              # FastAPI 入口
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Scan.tsx
│   │   │   ├── Birds.tsx
│   │   │   ├── Map.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── PhotoScoring.tsx   # 智能筛图页面 (新增)
│   │   │   ├── Summary.tsx        # 观鸟小结页面 (新增)
│   │   │   └── Calendar.tsx       # 观鸟日历页面 (新增)
│   │   ├── api/
│   │   │   └── api.ts             # API 客户端
│   │   └── App.tsx                # 路由配置
│   └── electron/
│       ├── main.cjs
│       └── preload.cjs
│
└── bird_watching.db               # SQLite 数据库文件
```

---

## API 端点

### 照片扫描
- `POST /api/scan/scan` - 扫描文件夹中的照片
- `GET /api/scan/supported-formats` - 获取支持的图片格式

### 鸟类识别
- `POST /api/birds/identify` - 识别照片中的鸟类
- `GET /api/birds/species-list` - 获取物种列表

### 大模型识别
- `POST /api/llm/llm-identify` - 使用 LLM 识别单张照片
- `POST /api/llm/llm-identify-batch` - 批量识别

### 智能筛图 (新增)
- `POST /api/scoring/batch-score` - 批量评分照片质量
- `GET /api/scoring/criteria/defaults` - 获取默认评分权重

### 地图
- `POST /api/map/generate` - 生成观鸟地图
- `GET /api/map/daily` - 获取当日地图
- `GET /api/map/heatmap` - 获取观鸟热力图（新增）

### 数据导出 (新增)
- `GET /api/export/photos` - 导出照片数据为 Excel/CSV
- `GET /api/export/detections` - 导出鸟类检测数据为 Excel/CSV
- `GET /api/export/summary` - 导出会话汇总报告

### 统计图表 (新增)
- `GET /api/stats/overview` - 获取总体统计数据
- `GET /api/stats/species-distribution` - 获取物种分布数据（饼图）
- `GET /api/stats/monthly-trend` - 获取月度观测趋势（柱状图）
- `GET /api/stats/daily-activity` - 获取每日活动热力数据
- `GET /api/stats/location-frequency` - 获取观测地点频率（条形图）
- `GET /api/stats/top-species` - 获取热门物种排行榜
- `GET /api/stats/camera-stats` - 获取相机使用统计

### 观鸟小结 (新增)
- `POST /api/summary/generate-summary` - 生成 HTML 小结
- `GET /api/summary/calendar/{year}/{month}` - 获取日历数据
- `GET /api/summary/sessions` - 获取观测会话列表
- `GET /api/summary/summary/{sessionId}` - 获取会话详情
- `GET /api/summary/yearly-summary/{year}` - 获取年度摘要
- `GET /api/summary/species/list` - 获取物种列表

---

## 数据库设计

### observation_sessions (观测会话表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| folder_path | TEXT | 照片文件夹路径 |
| scan_date | TEXT | 扫描日期 |
| total_photos | INTEGER | 总照片数 |
| location_name | TEXT | 地点名称 |
| notes | TEXT | 备注 |

### photos (照片表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 会话 ID (外键) |
| file_path | TEXT | 文件路径 |
| capture_time | TEXT | 拍摄时间 |
| gps_lat/gps_lng | REAL | GPS 坐标 |
| camera_model | TEXT | 相机型号 |
| quality_score | REAL | 质量评分 |
| is_recommended | BOOLEAN | 是否推荐 |

### bird_detections (鸟类检测表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| photo_id | INTEGER | 照片 ID (外键) |
| species_cn/en | TEXT | 中/英文种名 |
| confidence | REAL | 置信度 |
| description | TEXT | 描述 |
| behavior | TEXT | 行为 |

---

## 智能筛图功能

### 评分维度

| 维度 | 默认权重 | 说明 |
|------|----------|------|
| 对焦准确性 | 40% | 鸟眼是否清晰锐利 |
| 主体清晰度 | 35% | 鸟体羽毛细节、锐度 |
| 构图美学 | 25% | 主体位置、背景简洁度 |

### 评分流程

1. 用户选择照片文件夹
2. 调整各维度权重（滑块 0-100%）
3. 点击"开始评分"调用 LLM API
4. 返回每张照的：
   - 各维度分数（0-100）
   - 加权总分
   - 专家评语
   - 推荐标记（≥75 分）

### LLM Prompt 示例

```
你是一位专业的生态摄影师和观鸟专家...

评分维度（每项 0-100 分）：
1. 对焦准确性：鸟眼是否清晰锐利
2. 主体清晰度：鸟体羽毛细节是否清晰
3. 构图美学：主体位置、背景简洁度

返回 JSON：
{
  "focus_score": 85,
  "clarity_score": 78,
  "composition_score": 90,
  "overall_score": 84,
  "explanation": "鸟眼清晰对焦准确..."
}
```

---

## 使用说明

### 启动应用

1. **后端启动**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. **前端启动**
```bash
cd frontend
npm run dev
```

3. **Electron 桌面版**
```bash
cd frontend
npm run electron
```

### 配置 LLM API

1. 进入「设置」页面
2. 选择提供商（OpenAI/Anthropic/DeepSeek 等）
3. 填写 API Key 和模型名称
4. 测试连接

### 使用智能筛图

1. 进入「筛图」页面
2. 选择照片文件夹
3. 调整权重滑块
4. 点击「开始评分」
5. 查看评分结果和推荐照片

### 生成观鸟小结

1. 进入「小结」页面
2. 选择观测会话
3. 点击「生成 HTML 小结」
4. 点击「打开 HTML 文件」查看

### 查看观鸟日历

1. 进入「日历」页面
2. 切换年/月视图
3. 点击有记录的日期查看详情

### 导出 Excel 报表 (新增)

1. 进入「小结」页面
2. 选择观测会话
3. 点击「导出照片」、「导出检测」或「导出汇总」按钮
4. 自动下载 Excel 文件

### 查看统计图表 (新增)

1. 进入「统计」页面
2. 选择年份
3. 查看物种分布饼图、月度趋势柱状图、观测天数折线图
4. 查看热门物种排行榜

---

## 新增功能实现清单

### Phase 1: 智能筛图 ✅
- [x] `backend/app/api/scoring.py` - 评分 API
- [x] `frontend/src/pages/PhotoScoring.tsx` - 筛图 UI
- [x] `backend/app/main.py` - 注册路由
- [x] `frontend/src/App.tsx` - 添加路由
- [x] `frontend/src/api/api.ts` - 添加 scoringApi

### Phase 2: 数据库基础 ✅
- [x] `backend/app/db/database.py` - SQLite 模块
- [x] 初始化表结构（sessions, photos, detections）
- [x] CRUD 函数实现

### Phase 3: 观鸟小结 ✅
- [x] `backend/app/api/summary.py` - 小结 API
- [x] HTML 模板设计（精美自然风格）
- [x] Leaflet 地图集成
- [x] `frontend/src/pages/Summary.tsx` - 小结页面

### Phase 4: 观鸟日历 ✅
- [x] 日历 API 接口
- [x] `frontend/src/pages/Calendar.tsx` - 日历页面
- [x] 年/月/日视图切换
- [x] `frontend/src/index.css` - 日历样式

### Phase 5: 功能增强 ✅ (2026-03-16)
- [x] `backend/app/api/export.py` - 数据导出 API
- [x] `backend/app/api/stats.py` - 统计图表 API
- [x] `backend/app/main.py` - 注册 export 和 stats 路由
- [x] `frontend/src/pages/Statistics.tsx` - 统计页面
- [x] `frontend/src/pages/Map.tsx` - 添加热力图切换
- [x] `frontend/src/App.tsx` - 添加统计路由
- [x] `frontend/src/api/api.ts` - 添加 exportApi 和 statsApi
- [x] 安装依赖：`openpyxl` (Python), `recharts` (React)

---

## 下一步计划

1. **数据持久化集成**
   - 扫描后自动保存到数据库
   - 识别结果存储到 bird_detections 表

2. **性能优化**
   - 批量评分异步处理
   - 图片缩略图缓存

3. **功能增强**
   - 导出 CSV/Excel 报表
   - 物种统计图表
   - 地图热力图

---

## 依赖安装

### 后端依赖
```bash
pip install fastapi uvicorn httpx exifread rawpy pillow folium pydantic-settings
```

### 前端依赖
```bash
npm install
```

---

## 联系方式

项目作者：Quick Pick Birds Team
日期：2026-03-15
