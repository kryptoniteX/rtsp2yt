import os, subprocess, shlex, sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

def env(name, default=None):
    v = os.environ.get(name)
    return v if v else default

def gather_cameras(max_n=8):
    cams = []
    for i in range(1, max_n+1):
        rtsp = env(f"CAM{i}_RTSP")
        label = env(f"CAM{i}_LABEL", f"CAM{i}")
        if rtsp:
            cams.append({"idx": i, "rtsp": rtsp, "label": label})
    return cams

def pick_grid(n):
    if n <= 1: return (1,1)
    if n == 2: return (2,1)
    if n <= 4: return (2,2)
    if n <= 6: return (3,2)
    return (4,2)

def build_ffmpeg_cmd(cams):
    out_w = int(env("OUTPUT_WIDTH", "1920"))
    out_h = int(env("OUTPUT_HEIGHT", "1080"))
    fps   = int(env("CAM_FPS", "25"))
    bitrate = env("BITRATE", "5000k")
    preset  = env("PRESET", "veryfast")
    yt_url  = env("YT_RTMP_URL", "rtmp://a.rtmp.youtube.com/live2")
    key     = env("STREAM_KEY")
    chunk_h = float(env("CHUNK_HOURS", "12"))
    duration = int(chunk_h * 3600)

    if not key:
        print("[error] STREAM_KEY is required")
        sys.exit(1)

    num_cams = len(cams)
    inputs = []
    filters = []
    labels = []
    audio_labels = []

    # Prepare inputs
    for idx, cam in enumerate(cams):
        inp = [
            "-rtsp_transport", "tcp",
            "-timeout", "10000000",
            "-reorder_queue_size", "1000",
            "-i", cam["rtsp"]
        ]
        inputs += inp
        labels.append(f"v{idx}")
        audio_labels.append(f"a{idx}")

    # Single-camera setup
    if num_cams == 1:
        filters.append(f"[0:v]scale={out_w}:{out_h},fps={fps}[v0]")
        map_v = "[v0]"
        map_a = ["-map", "0:a?"]  # Use camera audio directly

    # Multi-camera setup with xstack
    else:
        cols, rows = pick_grid(num_cams)
        tile_w = out_w // cols
        tile_h = out_h // rows

        for idx in range(num_cams):
            filters.append(f"[{idx}:v]scale={tile_w}:{tile_h},fps={fps}[v{idx}]")
            filters.append(f"[{idx}:a?]aresample=44100,pan=stereo|c0=c0|c1=c0[{audio_labels[idx]}]")

        # Layout for xstack
        layout_pairs = []
        for r in range(rows):
            for c in range(cols):
                x = c * tile_w
                y = r * tile_h
                layout_pairs.append(f"{x}_{y}")
        layout = "|".join(layout_pairs[:num_cams])

        xstack_inputs = "".join(f"[{lab}]" for lab in labels)
        filters.append(f"{xstack_inputs}xstack=inputs={num_cams}:layout={layout}[grid]")
        map_v = "[grid]"

        # Mix all audio tracks
        amix_inputs = "".join(f"[{lab}]" for lab in audio_labels)
        filters.append(f"{amix_inputs}amix=inputs={num_cams}:normalize=1[aout]")
        map_a = ["-map", "[aout]"]

    vf = ",".join(filters)

    cmd = [
        "ffmpeg",
        *inputs,
        "-filter_complex", vf,
        "-map", map_v,
        *map_a,
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", preset,
        "-b:v", bitrate,
        "-maxrate", bitrate,
        "-bufsize", str(int(int(bitrate.strip('k'))*2))+"k" if bitrate.endswith("k") else "10M",
        "-g", str(fps*2),
        "-t", str(duration),
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-f", "flv",
        f"{yt_url}/{key}"
    ]

    print("[info] Running FFmpeg:\n", " ".join(shlex.quote(a) for a in cmd))
    return cmd


def main():
    cams = gather_cameras(8)
    if not cams:
        print("[error] No cameras configured/found. Set CAMn_RTSP in .env")
        sys.exit(1)

    cmd = build_ffmpeg_cmd(cams)
    proc = subprocess.Popen(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    finally:
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()
