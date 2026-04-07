# zokodaily-server

独立的 Flask API 服务工程，已从 `spider` 项目中拆分出来，采用工程化结构，便于后续继续扩展更多 API。

## 目录结构

```text
server/
├── api_server.py
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── news.py
│   │   └── places.py
│   ├── config.py
│   ├── db.py
│   ├── errors.py
│   ├── repositories/
│   │   ├── news.py
│   │   └── places.py
│   ├── serializers.py
│   └── utils.py
├── requirements.txt
└── wsgi.py
```

## 配置

- 运行时通过 `.env` 文件和环境变量加载配置。
- 本地开发参考 `.env.development.example`。
- 生产环境参考 `.env.production.example`。
- 如果提供 `DATABASE_URL`，将优先使用；否则会根据 `DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`、`DB_PASSWORD` 自动组装。
- 默认媒体目录指向兄弟项目 `../spider/downloads`，生产环境请显式设置 `MEDIA_ROOT`。

## 本地启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.development.example .env
python api_server.py
```

## 生产部署

- 设置 `APP_ENV=production`
- 提供生产环境专用的 `.env` 或系统环境变量
- 使用 `wsgi.py` 作为 WSGI 入口接入 Gunicorn / uWSGI / Waitress 等
