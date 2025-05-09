import httpx
from fastapi import APIRouter, Response

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
    # 从上游 PyPI 服务器下载包
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{config.ROOT_PYPI_URL}../../packages/{path}")
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
