FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y --no-install-recommends curl dumb-init

WORKDIR /app

COPY thirdparty thirdparty

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip3 install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY start.sh start.sh

# Server
ENV PYPI_LOCAL_PACKAGES_DIR=./packages
ENV PYPI_UPSTREAM=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYPI_HOST=0.0.0.0
ENV PYPI_PORT=10608

# WebUI
ENV PYPI_BROWSER_OFF=false
ENV PYPI_BROWSER_PYPI_URL=http://0.0.0.0:10608/simple
ENV PYPI_BROWSER_HOST=0.0.0.0
ENV PYPI_BROWSER_PORT=10609

EXPOSE ${PYPI_PORT} ${PYPI_BROWSER_PORT}

ENTRYPOINT ["/usr/bin/dumb-init","--"]

RUN mkdir -p /app/packages

CMD ["/app/start.sh"]