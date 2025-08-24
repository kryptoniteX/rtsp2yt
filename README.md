# rtsp2yt-multicam

`rtsp2yt-multicam` is a Python + FFmpeg solution to stream single or multiple RTSP camera feeds to YouTube Live in real-time. It supports multi-camera grids, automatic scaling, audio mixing, and chunked streaming for easy backup and management. Docker-ready for quick deployment.

---

## Features

* **Single & Multi-Camera Support**: Arrange multiple camera feeds in grid layouts using `xstack`.
* **Automatic Video & Audio Handling**: Video scaling, framerate adjustment, audio extraction, resampling, and mixing.
* **Chunked Streaming**: Automatically starts a new stream every 12 hours, preserving previous chunks for backup.
* **Configurable via Environment Variables**: Resolution, FPS, bitrate, YouTube stream key, chunk duration.
* **Docker-Ready**: Run on any system with Docker support without complex setup.

---

## Tech Stack

* Python
* FFmpeg
* Docker
* RTSP
* YouTube Live (RTMP)

---

## Use Cases

* Home surveillance
* Event streaming
* Multi-camera broadcasting

---

## Environment Variables

| Variable        | Default                          | Description                      |
| --------------- | -------------------------------- | -------------------------------- |
| `OUTPUT_WIDTH`  | 1920                             | Output video width               |
| `OUTPUT_HEIGHT` | 1080                             | Output video height              |
| `CAM_FPS`       | 25                               | Output video framerate           |
| `BITRATE`       | 5000k                            | Video bitrate                    |
| `PRESET`        | veryfast                         | FFmpeg encoding preset           |
| `YT_RTMP_URL`   | rtmp\://a.rtmp.youtube.com/live2 | YouTube RTMP server URL          |
| `STREAM_KEY`    | **Required**                     | YouTube Live stream key          |
| `CHUNK_HOURS`   | 12                               | Duration of each streaming chunk |

---

## Usage

### Docker

```bash
docker build -t rtsp2yt-multicam .
docker run -d --env-file .env rtsp2yt-multicam

---

## How It Works

1. Reads RTSP feeds from configured cameras.
2. Applies scaling, framerate adjustments, and audio mixing.
3. Uses FFmpeg `xstack` for multi-camera grids.
4. Streams output to YouTube Live.
5. Automatically restarts every `CHUNK_HOURS` to preserve previous streams.

---

## License

MIT License
