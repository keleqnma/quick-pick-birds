# 🐦 Quick Pick Birds - 智能观鸟照片识别应用

<div align="center">

![Quick Pick Birds Banner](https://img.shields.io/badge/Quick_Pick_Birds-观鸟助手-4CAF50?style=for-the-badge&logo=bird)

**一键扫描 · AI 识别 · 智能筛图 · 精美小结**

[![Platform](https://img.shields.io/badge/平台-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=flat-square)]()
[![License](https://img.shields.io/badge/许可证-MIT-green?style=flat-square)]()
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)]()
[![Node](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=node.js)]()
[![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat-square&logo=react)]()

</div>

---

## 📖 目录

- [功能亮点](#-功能亮点)
- [界面预览](#-界面预览)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [使用指南](#-使用指南)
- [API 文档](#-api-文档)
- [常见问题](#-常见问题)
- [开发计划](#-开发计划)

---

## ✨ 功能亮点

<details open>
<summary><b>点击展开功能详情</b></summary>

### 📁 智能文件夹扫描
- 支持 **RAW 格式**照片：CR2/CR3 (Canon)、NEF (Nikon)、ARW (Sony)、RAF (Fujifilm)
- 自动提取 **EXIF 信息**：拍摄时间、GPS 坐标、相机参数
- 批量处理，支持千张级照片快速扫描

### 🤖 AI 鸟类识别
- 集成大语言模型，精准识别鸟类品种
- 支持 **连拍分组分析**，自动筛选最佳照片
- 提供鸟类详细信息：学名、科属、保护级别

### ⭐ 智能筛图评分
- **三维度评分系统**：对焦清晰度 + 构图美感 + 物种特征
- 大模型专业点评，助你提升摄影技术
- 批量评分，快速淘汰废片

### 🗺️ 观鸟地图与热点
- 自动生成 **GPS 轨迹地图**，记录观鸟路线
- 支持 **热力图** 模式，发现高频观测点
- 创建和管理个人观鸟热点

### 📊 数据统计与小節
- 自动生成 **HTML 精美小结**
- 多维度统计：物种数量、观测天数、月度趋势
- 成就系统，记录你的观鸟里程碑

### 📋 eBird Checklist 支持
- 兼容 eBird 标准格式
- 支持创建和导出观测清单
- 一键分享到观鸟社区

</details>

---

## 🎨 界面预览

### 首页概览

```
┌─────────────────────────────────────────────────────────┐
│  🐦 Quick Pick Birds                                    │
│  观鸟照片识别工具 — 扫描 RAW 照片，识别鸟类              │
├─────────────────────────────────────────────────────────┤
│  [🏠 概览] [📁 扫描] [⭐ 筛图] [🐦 鸟类识别]            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   📁        │ │   🐦        │ │   ⭐        │   │
│  │  文件夹扫描  │ │  鸟类识别   │ │  智能筛图   │   │
│  │  支持 RAW 格式 │ │  AI 精准识别  │ │  三维度评分  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 功能模块图

| 模块 | 功能描述 | 快捷键 |
|------|----------|--------|
| 📁 **扫描** | 扫描文件夹，提取 EXIF 和 GPS | `Ctrl+O` |
| ⭐ **筛图** | AI 评分，筛选最佳照片 | - |
| 🐦 **物种** | 鸟类百科，查看物种详情 | - |
| 🗺️ **地图** | GPS 轨迹，热力图分布 | - |
| 📅 **日历** | 按日期浏览观测记录 | - |
| 📊 **小结** | 生成 HTML 精美报告 | - |
| 🏆 **成就** | 解锁观鸟里程碑 | - |
| 📋 **清单** | eBird Checklist 支持 | - |

---

## 🏗️ 技术架构

### 系统架构图

```
┌────────────────────────────────────────────────────────────┐
│                    Electron 桌面应用                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              React 19 + TypeScript                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ 扫描页  │ │ 筛图页  │ │ 地图页  │ │ 统计页  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ 物种页  │ │ 清单页  │ │ 成就页  │ │ 设置页  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │ HTTP API                       │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                    FastAPI 后端服务                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ EXIF 提取 │ │ AI 识别  │ │ 地图生成 │ │ 数据导出 │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 物种数据库│ │ 成就系统 │ │ 小结生成 │ │ eBird API │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└────────────────────────────────────────────────────────────┘
```

### 技术栈详情

| 层级 | 技术选型 |
|------|----------|
| **桌面应用** | Electron 41 + React 19 + TypeScript |
| **构建工具** | Vite 8 + electron-builder |
| **后端框架** | Python 3.11 + FastAPI + Uvicorn |
| **图像处理** | Pillow + rawpy + exifread |
| **地图引擎** | Folium + Leaflet |
| **数据可视化** | Recharts |
| **AI 集成** | Claude API / 自定义 LLM |

---

## 🚀 快速开始

### 环境要求

<div align="center">

| 组件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| Python | 3.11 | 3.12 |
| Node.js | 18 | 20+ |
| 内存 | 8GB | 16GB |
| 磁盘空间 | 2GB | 5GB+ |

</div>

### 第一步：克隆项目

```bash
git clone https://github.com/your-username/quick-pick-birds.git
cd quick-pick-birds
```

### 第二步：安装依赖

#### 🔧 后端依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 📦 前端依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 第三步：启动应用

#### 方式一：开发模式（推荐开发者）

**终端 1 - 启动后端服务：**
```bash
cd backend
# 确保虚拟环境已激活
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
看到以下输出表示成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**终端 2 - 启动桌面应用：**
```bash
cd frontend
npm run dev:electron
```

#### 方式二：Docker 一键启动

```bash
# 使用 docker-compose 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 方式三：使用启动脚本（Windows）

```bash
# 双击运行
start.bat
```

---

## 📖 使用指南

### 1️⃣ 扫描照片文件夹

1. 打开应用，点击「**📁 开始扫描**」或按 `Ctrl+O`
2. 选择包含 RAW 照片的文件夹
3. 等待扫描完成，查看照片列表和 EXIF 信息

```
扫描进度示例：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
正在扫描：IMG_0001.CR3 ... ✓
正在扫描：IMG_0002.CR3 ... ✓
正在扫描：IMG_0003.CR3 ... ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
扫描完成！发现 156 张照片，128 张包含 GPS 信息
```

### 2️⃣ AI 识别鸟类

1. 在扫描结果页面，点击「**识别鸟类**」
2. 系统自动分组连拍照片
3. 查看识别结果和推荐理由

**识别结果示例：**
```
📷 IMG_0001.CR3
├─ 物种：珠颈斑鸠 (Spilopelia chinensis)
├─ 保护级别：三有
└─ 推荐理由：对焦精准，羽毛细节清晰，姿态自然

📷 IMG_0005.CR3
├─ 物种：白头鹎 (Pycnonotus sinensis)
├─ 保护级别：常见
└─ 推荐理由：飞行姿态优美，背景虚化良好
```

### 3️⃣ 智能筛图评分

1. 进入「**⭐ 筛图**」页面
2. 选择评分标准（或使用默认标准）
3. 批量评分，查看排名

**评分维度：**
| 维度 | 权重 | 说明 |
|------|------|------|
| 🎯 对焦清晰度 | 40% | 主体是否锐利，焦点是否准确 |
| 🎨 构图美感 | 30% | 画面平衡，主体突出 |
| 🐦 物种特征 | 30% | 特征展现，姿态自然 |

### 4️⃣ 生成观鸟地图

1. 进入「**🗺️ 观鸟地图**」页面
2. 选择日期或查看热力图
3. 查看 GPS 轨迹和物种分布

### 5️⃣ 生成 HTML 小结

1. 进入「**📊 小结**」页面
2. 选择观测会话
3. 点击「生成 HTML 小结」
4. 导出分享或打印

---

## 📡 API 文档

### 端点列表

<details>
<summary><b>扫描 API</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/scan/scan` | 扫描文件夹中的照片 |
| `GET` | `/api/scan/supported-formats` | 获取支持的 RAW 格式列表 |
| `GET` | `/api/scan/photo-count` | 获取照片数量统计 |

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/scan/scan \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "C:/Photos/2024-01-01"}'
```

</details>

<details>
<summary><b>鸟类识别 API</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/birds/identify` | 批量识别照片中的鸟类 |
| `POST` | `/api/birds/detect-bird` | 上传单张照片检测 |
| `GET` | `/api/birds/species-list` | 获取支持的鸟类列表 |
| `GET` | `/api/birds/species/{id}` | 获取物种详情 |

**请求示例：**
```bash
curl -X POST http://localhost:8000/api/birds/identify \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "llm_provider": "claude"}'
```

</details>

<details>
<summary><b>筛图评分 API</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/scoring/criteria` | 获取默认评分标准 |
| `POST` | `/api/scoring/score` | 批量评分照片 |
| `POST` | `/api/scoring/score-single` | 单张照片评分 |

</details>

<details>
<summary><b>地图 API</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/map/daily` | 获取当日观鸟地图 |
| `GET` | `/api/map/generate` | 生成完整观鸟地图 |
| `GET` | `/api/map/heatmap` | 获取热力图数据 |

</details>

<details>
<summary><b>数据导出 API</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/export/photos` | 导出照片数据 Excel |
| `GET` | `/api/export/detections` | 导出鸟类检测结果 |
| `GET` | `/api/export/summary` | 导出观测汇总 |

</details>

---

## 🧩 支持的 RAW 格式

| 品牌 | 格式 | 说明 |
|------|------|------|
| 📷 Canon | `.cr2`, `.cr3` | 完全支持 |
| 📷 Nikon | `.nef` | 完全支持 |
| 📷 Sony | `.arw` | 完全支持 |
| 📷 Fujifilm | `.raf` | 完全支持 |
| 📷 Olympus | `.orf` | 完全支持 |
| 📷 Pentax | `.pef` | 完全支持 |
| 📷 Samsung | `.srw` | 完全支持 |
| 📷 Panasonic | `.rw2` | 完全支持 |
| 📷 Adobe | `.dng` | 完全支持 |

---

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 选择文件夹扫描 |
| `Ctrl+S` | 保存当前会话 |
| `Ctrl+R` | 刷新当前页面 |
| `Ctrl+Q` | 退出应用 |
| `F12` | 打开开发者工具 |
| `Ctrl++` | 放大界面 |
| `Ctrl+-` | 缩小界面 |
| `Ctrl+0` | 重置缩放级别 |

---

## ❓ 常见问题

<details>
<summary><b>❓ 扫描速度慢怎么办？</b></summary>

1. RAW 照片处理需要较大内存，建议至少 8GB RAM
2. 首次扫描大量照片可能需要较长时间，请耐心等待
3. 可以考虑分批扫描，每次处理 100-200 张照片
4. SSD 硬盘比机械硬盘有显著速度提升

</details>

<details>
<summary><b>❓ 鸟类识别不准确？</b></summary>

1. 确保照片清晰，主体突出
2. 检查是否正确配置了 LLM API
3. 某些相似物种可能需要人工确认
4. 可以在设置中调整识别阈值

</details>

<details>
<summary><b>❓ GPS 信息丢失？</b></summary>

1. 确认相机已开启 GPS 记录功能
2. 某些相机型号可能不记录 GPS 信息
3. 手机拍摄的 RAW 照片通常包含 GPS
4. 可以手动在后期添加位置信息

</details>

<details>
<summary><b>❓ 如何配置 LLM API？</b></summary>

1. 进入「设置」页面
2. 选择 LLM 提供商（推荐 Claude）
3. 输入 API Key 和模型名称
4. 点击「测试连接」验证配置

</details>

<details>
<summary><b>❓ 导出文件打不开？</b></summary>

1. 确认已安装 Microsoft Excel 或 WPS
2. 检查文件是否下载完整
3. 尝试重新导出
4. 检查文件名是否包含特殊字符

</details>

---

## 📋 开发计划

### v1.0 (当前版本)
- ✅ 基础扫描功能
- ✅ AI 鸟类识别
- ✅ 智能筛图评分
- ✅ 观鸟地图
- ✅ 数据导出

### v1.1 (计划中)
- [ ] 离线识别模型
- [ ] 更多统计图表
- [ ] 自定义评分标准
- [ ] 批量导出优化

### v2.0 (路线图)
- [ ] 移动端应用
- [ ] 云端同步
- [ ] 社区分享功能
- [ ] AI 辅助构图建议

---

## 🙏 致谢

感谢以下开源项目：

- [React](https://react.dev/) - 前端框架
- [Electron](https://www.electronjs.org/) - 桌面应用框架
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Pillow](https://python-pillow.org/) - 图像处理
- [rawpy](https://github.com/letmaik/rawpy) - RAW 文件处理
- [Folium](https://python-visualization.github.io/folium/) - 地图生成
- [Leaflet](https://leafletjs.com/) - 交互式地图
- [Recharts](https://recharts.org/) - 数据可视化

---

## 📄 License

```
MIT License

Copyright (c) 2024 Quick Pick Birds

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">

**🐦 Quick Pick Birds — 让每一次观鸟都值得纪念**

[开始使用](#-快速开始) · [报告问题](https://github.com/your-username/quick-pick-birds/issues) · [功能建议](https://github.com/your-username/quick-pick-birds/discussions)

</div>
