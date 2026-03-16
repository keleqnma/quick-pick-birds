# Quick Pick Birds - 桌面应用

## 开发模式启动

### 第一步：启动后端服务

```bash
cd backend
# 使用 Anaconda Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 第二步：启动 Electron 桌面应用

```bash
cd frontend
# 启动 Vite 开发服务器并自动打开 Electron
npm run dev:electron
```

或者直接运行：
```bash
npm run dev:electron
```

## 打包构建

### Windows
```bash
cd frontend
npm run build:electron
```

构建完成后，安装包在 `release/` 目录下。

### Mac
```bash
cd frontend
npm run build:electron
```

### Linux
```bash
cd frontend
npm run build:electron
```

## 输出文件

- **Windows**: `release/Quick Pick Birds-{version}.exe` (NSIS 安装器)
- **Mac**: `release/Quick Pick Birds-{version}.dmg`
- **Linux**: `release/Quick Pick Birds-{version}.AppImage`

## 注意事项

1. 打包前确保后端服务已打包或独立部署
2. 生产环境需要修改 API 地址配置
3. 首次安装需要同时安装后端运行环境
