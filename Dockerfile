# ============ 阶段 1：构建前端 ============
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ============ 阶段 2：Python 后端 + Nginx 服务 ============
FROM python:3.12-slim

# 安装 Nginx 和 Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制后端代码
COPY backend/ ./

# 复制前端构建产物到 Nginx 服务目录
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

# 删除 Nginx 默认站点配置，防止冲突
RUN rm -f /etc/nginx/sites-enabled/default

# Zeabur 要求暴露 8080 端口
ENV PORT=8080
EXPOSE 8080

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/app.conf"]
