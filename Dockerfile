ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=22
ARG BUILD_HASH=dev-build

FROM node:${NODE_VERSION}-alpine AS chatbot-frontend
ARG BUILD_HASH
WORKDIR /build/meyo-chatbot
RUN apk add --no-cache git
ENV CYPRESS_INSTALL_BINARY=0 \
    NPM_CONFIG_REGISTRY=https://registry.npmmirror.com \
    ONNXRUNTIME_NODE_INSTALL_CUDA=skip
COPY apps/meyo-chatbot/package.json apps/meyo-chatbot/package-lock.json ./
RUN npm ci --force
COPY apps/meyo-chatbot/ ./
ENV APP_BUILD_HASH=${BUILD_HASH}
RUN npm run build

FROM node:${NODE_VERSION}-alpine AS studio-frontend
WORKDIR /opt/meyo-studio-flow/src/frontend
ENV CYPRESS_INSTALL_BINARY=0 \
    NPM_CONFIG_REGISTRY=https://registry.npmmirror.com \
    ONNXRUNTIME_NODE_INSTALL_CUDA=skip
COPY apps/meyo-studio-flow/src/frontend/package.json apps/meyo-studio-flow/src/frontend/package-lock.json ./
RUN npm ci
COPY apps/meyo-studio-flow/src/frontend/ ./
ENV VITE_LANGFLOW_BASENAME=/studio/ \
    VITE_LANGFLOW_BASE_URL_API=/studio/api/v1/ \
    VITE_LANGFLOW_BASE_URL_API_V2=/studio/api/v2/ \
    BACKEND_URL=/studio
RUN npm run build

FROM python:${PYTHON_VERSION}-slim-bookworm AS python-builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=/usr/local/bin/python \
    UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_HTTP_TIMEOUT=120 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m pip install uv

RUN sed -i \
    -e 's|http://deb.debian.org/debian|http://mirrors.tuna.tsinghua.edu.cn/debian|g' \
    -e 's|http://deb.debian.org/debian-security|http://mirrors.tuna.tsinghua.edu.cn/debian-security|g' \
    /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    gcc \
    git \
    libffi-dev \
    libmariadb-dev \
    libpq-dev \
    libsm6 \
    libssl-dev \
    libxext6 \
    pandoc \
    pkg-config \
    zstd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/meyo
COPY pyproject.toml uv.lock README.md ./
RUN sed -i \
    -e 's|https://files.pythonhosted.org/packages/|https://pypi.tuna.tsinghua.edu.cn/packages/|g' \
    -e 's|https://pypi.org/simple|https://pypi.tuna.tsinghua.edu.cn/simple|g' \
    uv.lock
COPY packages/meyo-core/pyproject.toml packages/meyo-core/README.md packages/meyo-core/
COPY packages/meyo-ext/pyproject.toml packages/meyo-ext/README.md packages/meyo-ext/
COPY packages/meyo-client/pyproject.toml packages/meyo-client/README.md packages/meyo-client/
COPY packages/meyo-serve/pyproject.toml packages/meyo-serve/README.md packages/meyo-serve/
COPY packages/meyo-sandbox/pyproject.toml packages/meyo-sandbox/README.md packages/meyo-sandbox/
COPY packages/meyo-accelerator/pyproject.toml packages/meyo-accelerator/README.md packages/meyo-accelerator/
COPY packages/meyo-app/pyproject.toml packages/meyo-app/README.md packages/meyo-app/
RUN uv sync --frozen --no-dev --package meyo-app \
      --extra base --extra siliconflow --extra storage_common \
      --no-install-workspace
COPY packages/ packages/
COPY configs/ configs/
RUN uv sync --frozen --no-dev --package meyo-app \
      --extra base --extra siliconflow --extra storage_common

WORKDIR /opt/meyo-chatbot
RUN python -m venv /opt/venvs/meyo-chatbot
COPY apps/meyo-chatbot/backend/requirements.txt ./requirements.txt
RUN /opt/venvs/meyo-chatbot/bin/python -m pip install \
      --no-cache-dir --timeout 120 \
      --index-url https://mirror.sjtu.edu.cn/pytorch-wheels/cpu \
      --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple \
      'torch==2.9.1+cpu' 'torchvision==0.24.1+cpu' 'torchaudio==2.9.1+cpu'
RUN uv pip install --python /opt/venvs/meyo-chatbot/bin/python -r requirements.txt
COPY apps/meyo-chatbot/backend/ ./backend/

WORKDIR /opt/meyo-studio-flow
COPY apps/meyo-studio-flow/pyproject.toml apps/meyo-studio-flow/uv.lock apps/meyo-studio-flow/README.md ./
RUN sed -i \
    -e 's|https://files.pythonhosted.org/packages/|https://pypi.tuna.tsinghua.edu.cn/packages/|g' \
    -e 's|https://pypi.org/simple|https://pypi.tuna.tsinghua.edu.cn/simple|g' \
    uv.lock
COPY apps/meyo-studio-flow/src/backend/base/pyproject.toml apps/meyo-studio-flow/src/backend/base/README.md src/backend/base/
COPY apps/meyo-studio-flow/src/lfx/pyproject.toml apps/meyo-studio-flow/src/lfx/README.md src/lfx/
COPY apps/meyo-studio-flow/src/sdk/pyproject.toml apps/meyo-studio-flow/src/sdk/README.md src/sdk/
RUN uv sync --frozen --no-dev --package langflow --extra postgresql --no-install-workspace
COPY apps/meyo-studio-flow/ ./
RUN uv sync --frozen --no-dev --package langflow --extra postgresql

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    DOCKER=true \
    ENV=prod \
    MEYO_CONFIG=/opt/meyo/configs/meyo.toml \
    MEYO_WEB_HOST=127.0.0.1 \
    MEYO_WEB_PORT=5670 \
    CHATBOT_HOST=127.0.0.1 \
    CHATBOT_PORT=8080 \
    STUDIO_HOST=127.0.0.1 \
    STUDIO_PORT=7860 \
    ENABLE_OPENAI_API=true \
    ENABLE_OLLAMA_API=false \
    OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1 \
    RAG_OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1 \
    MEYO_OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1 \
    DATA_DIR=/data/meyo-chatbot \
    LANGFLOW_CONFIG_DIR=/data/meyo-studio-flow \
    LANGFLOW_SAVE_DB_IN_CONFIG_DIR=true \
    LANGFLOW_DATABASE_URL=sqlite+aiosqlite:////data/meyo-studio-flow/langflow.db \
    LANGFLOW_KNOWLEDGE_BASES_DIR=/data/meyo-studio-flow/knowledge_bases \
    LANGFLOW_ROOT_PATH=/studio \
    LANGFLOW_AUTO_LOGIN=true \
    LANGFLOW_SKIP_AUTH_AUTO_LOGIN=true \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false

RUN sed -i \
    -e 's|http://deb.debian.org/debian|http://mirrors.tuna.tsinghua.edu.cn/debian|g' \
    -e 's|http://deb.debian.org/debian-security|http://mirrors.tuna.tsinghua.edu.cn/debian-security|g' \
    /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    ffmpeg \
    jq \
    libgomp1 \
    libmariadb3 \
    libpq5 \
    libsm6 \
    libxext6 \
    nginx \
    pandoc \
    zstd \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

COPY --from=python-builder /opt/meyo /opt/meyo
COPY --from=python-builder /opt/meyo-chatbot /opt/meyo-chatbot
COPY --from=python-builder /opt/venvs/meyo-chatbot /opt/venvs/meyo-chatbot
COPY --from=python-builder /opt/meyo-studio-flow /opt/meyo-studio-flow
COPY --from=chatbot-frontend /build/meyo-chatbot/build /opt/meyo-chatbot/build
COPY --from=chatbot-frontend /build/meyo-chatbot/CHANGELOG.md /opt/meyo-chatbot/CHANGELOG.md
COPY --from=chatbot-frontend /build/meyo-chatbot/package.json /opt/meyo-chatbot/package.json
COPY --from=studio-frontend /opt/meyo-studio-flow/src/frontend/build /opt/meyo-studio-flow/src/backend/base/langflow/frontend

COPY docker/meyo-stack-nginx.conf /etc/nginx/nginx.conf
COPY docker/meyo-stack-entrypoint.sh /usr/local/bin/meyo-stack-entrypoint.sh

RUN chmod +x /usr/local/bin/meyo-stack-entrypoint.sh \
    && mkdir -p /data/meyo-chatbot /data/meyo-studio-flow /opt/meyo/logs /opt/meyo/pilot

WORKDIR /opt/meyo

EXPOSE 80
VOLUME ["/data/meyo-chatbot", "/data/meyo-studio-flow", "/opt/meyo/pilot", "/opt/meyo/logs"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl --silent --fail http://127.0.0.1/healthz >/dev/null || exit 1

ENTRYPOINT ["/usr/local/bin/meyo-stack-entrypoint.sh"]
