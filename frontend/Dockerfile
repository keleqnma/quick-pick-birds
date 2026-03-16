# 前端服务
FROM node:20-alpine

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 安装 serve 用于提供静态文件
RUN npm install -g serve

# 暴露端口
EXPOSE 5173

# 启动命令
CMD ["serve", "-s", "dist", "-l", "5173"]
