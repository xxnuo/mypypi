#!/usr/bin/env python3

import concurrent.futures
import hashlib
import json
import logging
import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup

# 设置日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 全局常量
CHUNK_SIZE = 8192
PROGRESS_FILE = "sync/sync_metadata.json"
PACKAGES_FILE = "sync/packages.txt"
SOURCE_FILE = "sync/source.txt"
DATA_DIR = "sync/data"
PYPI_DIR = "pypi"


class DownloadManager:
    def __init__(self):
        self.output_dir = Path(DATA_DIR)
        self.output_dir.mkdir(exist_ok=True)
        self.progress = self._load_progress()
        self._build_filename_map()

    def _load_progress(self):
        """加载下载进度记录"""
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"无法加载进度文件: {e}")
        return {}

    def _save_progress(self):
        """保存下载进度"""
        try:
            with open(PROGRESS_FILE, "w") as f:
                json.dump(self.progress, f)
        except Exception as e:
            logging.error(f"保存进度失败: {e}")

    def _build_filename_map(self):
        """构建文件名到URL的映射，用于重复检测"""
        self.filename_map = {}
        pattern = re.compile(r"(.+\.whl)(?:#sha256=.+)?$")

        # 从进度文件中构建映射
        for url, info in self.progress.items():
            if info.get("status") == "completed":
                filename = os.path.basename(url)
                match = pattern.match(filename)
                if match:
                    clean_name = match.group(1)
                    self.filename_map[clean_name] = url

        # 从data目录构建映射
        for file_path in self.output_dir.glob("*.whl"):
            clean_name = file_path.name
            # 如果文件存在但不在进度记录中，添加一个虚拟记录
            if clean_name not in self.filename_map:
                self.filename_map[clean_name] = f"file://{file_path}"

        # 从pypi目录构建映射
        pypi_dir = Path(PYPI_DIR)
        if pypi_dir.exists():
            # 递归查找所有包目录中的whl文件
            for file_path in pypi_dir.glob("**/*.whl"):
                clean_name = file_path.name
                if clean_name not in self.filename_map:
                    self.filename_map[clean_name] = f"file://{file_path}"
                    logging.debug(f"在pypi目录找到已存在的文件: {clean_name}")

    def _calculate_file_hash(self, file_path):
        """计算文件的SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_file_size(self, url):
        """获取远程文件大小"""
        try:
            response = requests.head(url)
            return int(response.headers.get("content-length", 0))
        except Exception:
            return 0

    def _get_clean_filename(self, url):
        """获取不包含SHA256校验部分的文件名"""
        filename = os.path.basename(unquote(url))
        match = re.match(r"(.+\.whl)(?:#sha256=.+)?$", filename)
        return match.group(1) if match else filename

    def is_already_downloaded(self, url):
        """检查文件是否已经下载"""
        clean_filename = self._get_clean_filename(url)

        # 检查是否在文件名映射中
        if clean_filename in self.filename_map:
            existing_url = self.filename_map[clean_filename]
            logging.info(f"文件 {clean_filename} 已存在，跳过下载")

            # 如果是实际URL，将当前URL添加到进度记录中
            if existing_url.startswith("http"):
                existing_info = self.progress.get(existing_url, {})
                if existing_info.get("status") == "completed":
                    self.progress[url] = existing_info.copy()
                    self._save_progress()
            return True

        # 检查进度记录
        if url in self.progress and self.progress[url]["status"] == "completed":
            output_path = self.output_dir / clean_filename
            pypi_path = None

            # 在pypi目录中查找文件
            pkg_pattern = re.compile(r"^([a-zA-Z0-9_.-]+?)(?:-\d|[-_]\d)")
            match = pkg_pattern.match(clean_filename)
            if match:
                package_name = match.group(1).replace("-", "_").lower()
                pypi_path = Path(PYPI_DIR) / package_name / clean_filename

            # 检查data目录或pypi目录是否存在文件
            if output_path.exists():
                file_hash = self._calculate_file_hash(output_path)
                if file_hash == self.progress[url]["hash"]:
                    logging.info(
                        f"文件已存在于data目录且验证通过，跳过: {clean_filename}"
                    )
                    return True
            elif pypi_path and pypi_path.exists():
                file_hash = self._calculate_file_hash(pypi_path)
                if file_hash == self.progress[url]["hash"]:
                    logging.info(
                        f"文件已存在于pypi目录且验证通过，跳过: {clean_filename}"
                    )
                    return True

        return False

    def download_wheel(self, url):
        """下载wheel文件，支持断点续传"""
        try:
            # 检查是否已下载
            if self.is_already_downloaded(url):
                return True

            filename = os.path.basename(url)
            clean_filename = self._get_clean_filename(url)
            output_path = self.output_dir / clean_filename
            temp_path = self.output_dir / f"{clean_filename}.temp"

            # 获取远程文件大小
            total_size = self._get_file_size(url)

            # 准备断点续传
            headers = {}
            local_size = 0
            if temp_path.exists():
                local_size = temp_path.stat().st_size
                if local_size < total_size:
                    headers["Range"] = f"bytes={local_size}-"
                else:
                    temp_path.unlink()
                    local_size = 0

            # 开始下载
            mode = "ab" if local_size > 0 else "wb"
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            with open(temp_path, mode) as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        local_size += len(chunk)

            # 验证并完成下载
            if temp_path.exists():
                file_hash = self._calculate_file_hash(temp_path)

                # 如果目标文件已存在，先删除
                if output_path.exists():
                    output_path.unlink()

                temp_path.rename(output_path)
                self.progress[url] = {
                    "status": "completed",
                    "hash": file_hash,
                    "size": local_size,
                    "filename": clean_filename,
                }
                self._save_progress()

                # 更新文件名映射
                self.filename_map[clean_filename] = url

                logging.info(f"成功下载: {clean_filename}")
                return True

        except requests.RequestException as e:
            logging.error(f"下载失败 {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()
        except Exception as e:
            logging.error(f"处理文件时出错 {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()
        return False

    def rename_files_remove_hash(self):
        """重命名文件，移除SHA256校验部分"""
        count = 0
        pattern = re.compile(r"(.+\.whl)#sha256=.+")

        for file_path in self.output_dir.glob("*.whl*"):
            file_name = file_path.name
            match = pattern.match(file_name)

            if match:
                new_name = match.group(1)
                new_path = self.output_dir / new_name

                try:
                    # 如果目标文件已存在，先删除
                    if new_path.exists() and new_path != file_path:
                        new_path.unlink()

                    file_path.rename(new_path)
                    count += 1
                    logging.info(f"重命名文件: {file_name} -> {new_name}")

                    # 更新进度记录中的文件名
                    for url, info in self.progress.items():
                        if (
                            info.get("status") == "completed"
                            and os.path.basename(url) == file_name
                        ):
                            info["filename"] = new_name

                except Exception as e:
                    logging.error(f"重命名文件失败 {file_name}: {e}")

        if count > 0:
            self._save_progress()

        logging.info(f"总共重命名了 {count} 个文件")

    def organize_by_package(self):
        """将wheel文件按照包名分类移动到pypi/目录下的包名目录内"""
        pypi_dir = Path(PYPI_DIR)
        pypi_dir.mkdir(exist_ok=True)

        # 正则表达式用于从wheel文件名中提取包名
        # 格式通常为: package_name-version-py3-none-any.whl
        pattern = re.compile(r"^([a-zA-Z0-9_.-]+?)(?:-\d|[-_]\d)")

        count = 0
        for file_path in self.output_dir.glob("*.whl"):
            file_name = file_path.name
            match = pattern.match(file_name)

            if match:
                package_name = match.group(1)
                # 处理包名中的特殊字符，如将'-'替换为'_'
                package_name = package_name.replace("-", "_").lower()

                # 创建包目录
                package_dir = pypi_dir / package_name
                package_dir.mkdir(exist_ok=True)

                # 目标路径
                target_path = package_dir / file_name

                try:
                    # 如果目标文件已存在，先删除
                    if target_path.exists():
                        target_path.unlink()

                    # 移动文件到目标目录
                    shutil.move(file_path, target_path)
                    count += 1
                    logging.info(f"移动文件到包目录: {file_name} -> {package_name}/")

                except Exception as e:
                    logging.error(f"移动文件失败 {file_name}: {e}")
            else:
                logging.warning(f"无法从文件名提取包名: {file_name}")

        logging.info(f"总共整理了 {count} 个文件到包目录")


def read_source():
    """读取PyPI源地址"""
    with open(SOURCE_FILE, "r") as f:
        return f.read().strip()


def read_packages():
    """读取需要下载的包列表"""
    with open(PACKAGES_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def get_package_page(base_url, package):
    """获取包的页面URL"""
    url = urljoin(base_url, package) + "/"
    logging.info(f"正在获取包页面: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text, url  # 返回页面内容和实际URL
    except requests.RequestException as e:
        logging.error(f"获取包 {package} 的页面失败: {e}")
        return None, None


def get_wheel_urls(page_content, page_url):
    """解析页面内容获取wheel文件的URL"""
    if not page_content or not page_url:
        return []

    soup = BeautifulSoup(page_content, "html.parser")
    links = soup.find_all("a")
    logging.info(f"找到 {len(links)} 个链接")

    # 打印所有链接的href属性
    for link in links:
        href = link.get("href", "")
        logging.debug(f"链接: {href}")

    wheel_urls = []
    for link in links:
        href = link.get("href", "")
        if ".whl" in href:
            full_url = urljoin(page_url, href)
            wheel_urls.append(full_url)

    logging.info(f"找到 {len(wheel_urls)} 个wheel文件")
    if wheel_urls:
        for url in wheel_urls:
            logging.debug(f"Wheel文件: {url}")
    else:
        logging.debug("页面内容:")
        logging.debug(page_content[:1000])
    return wheel_urls


def main():
    base_url = read_source()
    packages = read_packages()
    download_manager = DownloadManager()

    logging.info(f"开始从 {base_url} 下载包")

    for package in packages:
        logging.info(f"处理包: {package}")

        page_content, page_url = get_package_page(base_url, package)
        if not page_content:
            continue

        wheel_urls = get_wheel_urls(page_content, page_url)
        if not wheel_urls:
            logging.warning(f"没有找到包 {package} 的wheel文件")
            continue

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(download_manager.download_wheel, url)
                for url in wheel_urls
            ]
            concurrent.futures.wait(futures)

    # 下载完成后重命名文件
    download_manager.rename_files_remove_hash()

    # 按包名整理文件
    download_manager.organize_by_package()


if __name__ == "__main__":
    main()
