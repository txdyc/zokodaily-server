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

### uWSGI + Nginx（socket）

- 已提供 `uwsgi` 配置文件：`uwsgi.ini`
- 默认 Unix socket：`/run/zokodaily-api/uwsgi.sock`
- 适合由 Nginx 通过 `uwsgi_pass` 反向代理

启动示例

```bash
cd server
uwsgi --ini uwsgi.ini
```

Nginx 示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/run/zokodaily-api/uwsgi.sock;
        uwsgi_read_timeout 60s;
    }
}
```

说明

- 建议配合 `systemd` 设置 `WorkingDirectory=server` 后再执行：`uwsgi --ini uwsgi.ini`
- 生产环境配置建议写入 `.env.production`
- 如果 Nginx 用户为 `www-data`，请确保 socket 所在目录和 socket 文件对该用户组可读写

## Ubuntu 心跳守护

- 启动脚本：`scripts/run_api_service.sh`
- 每分钟心跳检查脚本：`scripts/check_api_heartbeat.sh`
- 安装 `systemd` 服务与 watchdog：`scripts/install_ubuntu_watchdog.sh`
- 卸载 `systemd` 服务与 watchdog：`scripts/uninstall_ubuntu_watchdog.sh`

默认行为

- API 心跳地址：`http://127.0.0.1:8000/api/health`
- watchdog 每 `1` 分钟执行一次
- 如果心跳检查失败，则执行：`systemctl restart zokodaily-api.service`

安装示例

```bash
cd server
chmod +x ./scripts/*.sh
sudo ./scripts/install_ubuntu_watchdog.sh
```

可选环境变量

- `SERVICE_NAME`：默认 `zokodaily-api`
- `FLASK_PORT`：默认 `8000`
- `HEALTH_URL`：默认 `http://127.0.0.1:8000/api/health`
- `ENV_FILE`：默认 `server/.env.production`
- `RUN_USER` / `RUN_GROUP`：指定 systemd 运行用户
- `PYTHON_BIN`：显式指定 Python 解释器

验证命令

```bash
systemctl status zokodaily-api.service
systemctl status zokodaily-api-watchdog.service
systemctl status zokodaily-api-watchdog.timer
systemctl list-timers | grep zokodaily-api-watchdog
```
