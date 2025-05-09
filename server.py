import os
import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("DEBUG", False)

    uvicorn.run("mypypi_server.routers:app", host=host, port=port, reload=debug)
