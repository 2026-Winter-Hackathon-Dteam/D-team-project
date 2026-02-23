FROM python:3.12-slim

# 環境変数（Pythonの出力バッファ無効化など）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 必要パッケージのインストール、slimイメージ使用の場合は必須
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtから必要なPythonパッケージの取得
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# WORKDIRのappにconfig(Djangoアプリあるところ)へコピー
COPY ./config /app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]