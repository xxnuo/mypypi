# MyPyPI

一个具有现代化 Web 界面、可定制软件包、缓存和镜像功能的 PyPI 服务器。

## 特性

- **现代化 Web 界面**：清晰直观的用户界面，便于浏览软件包
- **可定制软件包**：托管您自己的私有 Python 软件包
- **缓存功能**：高效缓存来自上游 PyPI 服务器的软件包
- **镜像功能**：从官方 PyPI 或其他源镜像软件包
- **Docker 就绪**：使用 Docker 和 Docker Compose 轻松部署

## 快速开始

### 使用 Docker Compose

创建 `compose.yml` 文件：

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

启动服务：

```bash
docker compose up -d
```


服务将在以下地址可用：
- PyPI 镜像服务器：http://localhost:10608/simple
- PyPI WebUI：http://localhost:10609

> 默认 PyPI 镜像的服务器为 [清华大学开源软件镜像站](https://pypi.tuna.tsinghua.edu.cn/simple)

### 常用配置

您可以通过设置 `compose.yml` 文件中的环境变量覆盖默认配置：

```yaml
environment:
  - PYPI_UPSTREAM=https://pypi.tuna.tsinghua.edu.cn/simple 
  # 默认 PyPI 镜像的服务器
  - PYPI_BROWSER_OFF=false 
  # 是否关闭 PyPI WebUI，仅使用 PyPI 镜像服务器时，不需要 WebUI 可以设置为 true
```

### 使用方法

#### uv

要使用您的 MyPyPI 服务器，您需要配置 uv 使用您的服务器，例如：

```bash
# 从服务器安装软件包
uv add -i http://localhost:10608/simple some-package

# 配置 uv 始终使用您的服务器(仅供参考，请根据实际情况配置)
mkdir -p ~/.config/uv && \
    printf '%s\n' \
    '[[index]]' \
    'url = "http://localhost:10608/simple"' \
    'default = true' \
    > ~/.config/uv/uv.toml
```

> 更多关于 uv 的配置，请参考 [uv 文档](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-sources)

#### pip

要使用您的 MyPyPI 服务器，您需要配置 pip 使用您的服务器，例如：

```bash
# 从您的服务器安装软件包
pip install -i http://localhost:10608/simple some-package

# 配置 pip 始终使用您的服务器
pip config set global.index-url http://localhost:10608/simple
```

## 开发

### 先决条件

- uv
- make

### 如何开发

参考 `Makefile` 中的命令。

## 许可

本项目使用 [Apache License 2.0](LICENSE)。

## 致谢

- [pypiserver](https://github.com/xxnuo/pypiserver.git)
- [pypi-browser](https://github.com/xxnuo/pypi-browser.git) 
