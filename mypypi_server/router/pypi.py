import httpx
from fastapi import APIRouter, Response
from urllib.parse import urljoin

import mypypi_server.config as config

pypi_router = APIRouter()


@pypi_router.get("/simple")
async def simple():
    """返回包索引页面"""
    async with httpx.AsyncClient() as client:
        response = await client.get(config.ROOT_PYPI_URL)
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "text/html"),
        )


@pypi_router.get("/simple/{package}")
async def package_info(package: str):
    """返回特定包的信息页面"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{config.ROOT_PYPI_URL}{package}/")
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "text/html"),
        )


@pypi_router.get("/packages/{path:path}")
async def download_package(path: str):
    """下载包文件"""
    # 构建正确的包下载 URL
    # 从 simple 页面获取的包下载链接通常是相对路径，需要基于源 URL 构建完整的下载链接
    root_url = config.ROOT_PYPI_URL.rsplit("/simple/", 1)[0]
    package_url = f"{root_url}/packages/{path}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(package_url)
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "application/octet-stream"),
            headers={
                "Content-Disposition": response.headers.get(
                    "content-disposition",
                    f'attachment; filename="{path.split("/")[-1]}"',
                )
            },
        )
