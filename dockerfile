FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tzdata \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir onvif-zeep python-dotenv requests

WORKDIR /app
COPY app/ /app/
COPY stream_loop.sh /app/stream_loop.sh
RUN chmod +x /app/stream_loop.sh

ENV TZ=UTC

CMD ["/app/stream_loop.sh"]