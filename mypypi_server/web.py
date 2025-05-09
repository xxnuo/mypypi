import os
from mypypi_server.utils import ensure_dir
from mypypi_server.config import WEB_DIR


def init_web() -> bool:
    """初始化 Web 界面"""
    if not ensure_dir(WEB_DIR):
        return False
    if not os.path.exists(WEB_DIR / "index.html"):
        if not download_web_assets():
            return False
    return True


def download_web_assets() -> bool:
    """下载 Web 界面资源"""
    pass
