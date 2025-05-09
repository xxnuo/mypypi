from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


DEBUG = bool(os.getenv("DEBUG", False))  # 是否开启 Debug 模式

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()  # 数据存储的文件夹
PKG_DIR = Path(os.getenv("PKG_DIR", f"{DATA_DIR}/packages")).resolve()  # 包存储的文件夹
WEB_DIR = Path(
    os.getenv("WEB_DIR", f"{DATA_DIR}/web")
).resolve()  # Web 界面存放的文件夹
CONFIG_DIR = Path(
    os.getenv("CONFIG_DIR", f"{DATA_DIR}/config")
).resolve()  # 配置文件存储的文件夹

DISABLE_WEB = bool(os.getenv("DISABLE_WEB", False))  # 关闭 Web 界面
DISABLE_CORS = bool(os.getenv("DISABLE_CORS", True))  # 关闭 CORS
DISABLE_OPENAPI = bool(os.getenv("DISABLE_OPENAPI", False))  # 关闭 OpenAPI
DISABLE_DOCS = bool(os.getenv("DISABLE_DOCS", False))  # 关闭 OpenAPI 文档
DISABLE_REDOC = bool(os.getenv("DISABLE_REDOC", False))  # 关闭 Redoc 文档

HOST = os.getenv("HOST", "0.0.0.0")  # Uvicorn 主机地址
PORT = int(os.getenv("PORT", 3000))  # Uvicorn 端口

DB_URL = os.getenv("DB_URL", f"sqlite:///{CONFIG_DIR}/server.sqlite")  # KV 数据库 URL
DB_NAME = os.getenv("DB_NAME", "server")  # KV 数据库名称


ROOT_PYPI_URL = os.getenv(
    "ROOT_PYPI_URL", "https://mirrors.ustc.edu.cn/pypi/simple/"
)  # 根 PyPI 源地址, 默认使用中科大源
