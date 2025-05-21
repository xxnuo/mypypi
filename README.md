# MyPyPI

A PyPI server with a modern Web interface, customizable packages, caching, and mirroring functionality.

[中文说明](README_zh.md)

## Features

- **Modern Web Interface**: Clean and intuitive UI for browsing packages
- **Customizable Packages**: Host your own private Python packages
- **Caching**: Efficiently cache packages from upstream PyPI servers
- **Mirroring**: Mirror packages from official PyPI or other sources
- **Docker Ready**: Easy deployment with Docker and Docker Compose

## Quick Start

### Using Docker Compose

Create a `compose.yml` file:

```yml
services:
  mypypi:
    image: xxnuo/mypypi:latest
    ports:
      - 10608:10608 # Pypi Server
      - 10609:10609 # Pypi WebUI
    volumes:
      - ./packages:/app/packages
    restart: unless-stopped
```

Start the service:

```bash
docker compose up -d
```

The services will be available at:
- PyPI Server: http://localhost:10608/simple
- PyPI WebUI: http://localhost:10609

> The default PyPI mirror server is [Tsinghua University Open Source Software Mirror Site](https://pypi.tuna.tsinghua.edu.cn/simple)

### Common Configuration

You can override the default configuration by setting environment variables in the `compose.yml` file:

```yaml
environment:
  - PYPI_UPSTREAM=https://pypi.tuna.tsinghua.edu.cn/simple 
  # Default PyPI mirror server
  - PYPI_BROWSER_OFF=false 
  # Whether to turn off PyPI WebUI, can be set to true if you only need the PyPI mirror server
```

### Usage

#### uv

To use your MyPyPI server, you need to configure uv to use your server, for example:

```bash
# Install packages from your server
uv add -i http://localhost:10608/simple some-package

# Configure uv to always use your server (only for reference, please configure according to actual situation)
mkdir -p ~/.config/uv && \
    printf '%s\n' \
    '[[index]]' \
    'url = "http://localhost:10608/simple"' \
    'default = true' \
    > ~/.config/uv/uv.toml
```

> For more information about uv configuration, please refer to [uv documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-sources)

#### pip

To use your MyPyPI server, you need to configure pip to use your server, for example:

```bash
# Install packages from your server
pip install -i http://localhost:10608/simple some-package

# Configure pip to always use your server
pip config set global.index-url http://localhost:10608/simple
```

## Development

### Prerequisites

- uv
- make

### How to Develop

Refer to the commands in the `Makefile`.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Acknowledgements

- [pypiserver](https://github.com/pypiserver/pypiserver.git)
- [pypi-browser](https://github.com/xxnuo/pypi-browser.git)
