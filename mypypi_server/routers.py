from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import mypypi_server.config as config
from mypypi_server.router.pypi import pypi_router

app = FastAPI(
    title="MyPyPi Server",
    debug=config.DEBUG,
    docs_url=None if config.DISABLE_DOCS else "/docs",
    redoc_url=None if config.DISABLE_REDOC else "/redoc",
    redirect_slashes=True,
)

if config.DISABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(pypi_router, prefix="/pypi")
