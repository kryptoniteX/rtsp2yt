#!/bin/bash
set -e

# Respect TZ from env
if [ -n "$TZ" ]; then
  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
fi

CHUNK_HOURS="${CHUNK_HOURS:-12}"

while true; do
  echo "[rtsp2yt] Starting new chunk for ${CHUNK_HOURS} hour(s) at $(date)"
  python /app/gen_and_stream.py || true
  echo "[rtsp2yt] Chunk finished at $(date). Restarting..."
done
