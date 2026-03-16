# Quick Pick Birds - 观鸟照片识别应用

🐦 一个跨平台桌面应用，用于扫描 RAW 照片、识别鸟类品种、绘制观鸟地图。

## 功能特性

### 核心功能
- **📁 文件夹扫描** - 扫描本地文件夹中的 RAW 照片（CR2、CR3、NEF、ARW 等格式）
- **📷 EXIF 提取** - 自动提取拍摄时间、GPS 坐标、相机参数
- **🔍 鸟类识别** - AI 识别照片中的鸟类品种
- **📸 连拍分析** - 自动分组连拍照片，筛选最佳照片
- **🗺️ 观鸟地图** - 根据 GPS 和时间信息生成观鸟地图

### 桌面应用特性
- **原生文件夹选择** - 使用系统对话框选择照片文件夹
- **应用菜单** - 文件/编辑/视图/帮助菜单
- **快捷键支持** - Ctrl+O 打开文件夹，F12 开发者工具等
- **跨平台** - Windows/Mac/Linux 通用

## 技术栈

### 桌面应用
- **Electron** - 跨平台桌面应用框架
- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具

### 后端
- **Python 3.11+** - 编程语言
- **FastAPI** - Web 框架
- **Pillow/rawpy** - 图像处理
- **exifread** - EXIF 数据提取
- **folium** - 地图生成

## 快速开始

### 环境要求
- **Python 3.11+**
- **Node.js 18+**

### 第一步：安装依赖

#### 后端
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 前端
```bash
cd frontend
npm install
```

### 第二步：启动应用

#### 方式一：开发模式（推荐开发时使用）

**终端 1 - 启动后端：**
```bash
cd backend
# 确保虚拟环境已激活
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动 Electron 桌面应用：**
```bash
cd frontend
npm run dev:electron
```

#### 方式二：使用启动脚本（Windows）
```bash
# 双击运行
start.bat
```

### 第三步：使用应用

1. 在首页点击「开始扫描」或按 Ctrl+O 选择照片文件夹
2. 等待扫描完成，查看照片列表
3. 点击「识别鸟类」进行 AI 识别
4. 在地图页面查看观鸟路线

## 打包构建

### Windows
```bash
cd frontend
npm run build:electron
```

输出：`frontend/release/Quick Pick Birds-{version}.exe`

### Mac
```bash
cd frontend
npm run build:electron
```

输出：`frontend/release/Quick Pick Birds-{version}.dmg`

### Linux
```bash
cd frontend
npm run build:electron
```

输出：`frontend/release/Quick Pick Birds-{version}.AppImage`

## 项目结构

```
quick-pick-birds/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   └── api/
│   │       ├── scan.py       # 扫描 API
│   │       ├── birds.py      # 鸟类识别 API
│   │       └── map_endpoint.py # 地图 API
│   └── requirements.txt
├── frontend/
│   ├── electron/
│   │   ├── main.cjs          # Electron 主进程
│   │   └── preload.cjs       # 预加载脚本
│   ├── src/
│   │   ├── api/
│   │   ├── pages/
│   │   └── types/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API 接口

### 扫描 API
- `POST /api/scan/scan` - 扫描文件夹中的照片
- `GET /api/scan/supported-formats` - 获取支持的照片格式

### 鸟类识别 API
- `POST /api/birds/identify` - 批量识别照片中的鸟类
- `POST /api/birds/detect-bird` - 上传单张照片检测
- `GET /api/birds/species-list` - 获取支持的鸟类列表

### 地图 API
- `GET /api/map/daily` - 获取当日观鸟地图
- `GET /api/map/generate` - 生成完整观鸟地图

## 支持的 RAW 格式

- Canon: .cr2, .cr3
- Nikon: .nef
- Sony: .arw
- Fujifilm: .raf
- Olympus: .orf
- Pentax: .pef
- Samsung: .srw
- Adobe: .dng

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+O | 选择文件夹扫描 |
| Ctrl+Q | 退出应用 |
| Ctrl+R | 刷新页面 |
| F12 | 打开开发者工具 |
| Ctrl++ | 放大 |
| Ctrl+- | 缩小 |
| Ctrl+0 | 重置缩放 |

## 注意事项

1. RAW 照片处理需要较大的内存，建议至少 8GB RAM
2. 首次扫描大量照片可能需要较长时间
3. GPS 信息依赖于照片 EXIF 数据
4. 鸟类识别准确率取决于模型训练数据
5. 后端服务需要与桌面应用同时运行

## License

MIT
