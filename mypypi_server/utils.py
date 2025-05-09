import os


def ensure_dir(path: str) -> bool:
    """确保目录存在"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception:
            return False
    return True
