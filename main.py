#!/usr/bin/env python3
import os
import time
import subprocess
from pathlib import Path

# CONFIGURATION
CAMERA_MOUNT_PATH = "/mnt/camera"
LOCAL_VIDEO_PATH = Path.home() / "Insta360Downloads"
STITCHED_VIDEO_PATH = Path.home() / "Insta360Stitched"
SDK_BINARY = "/opt/Insta360/MediaSDK/bin/stitcher_demo"  # Replace with your compiled binary
AI_MODEL_PATH = "/opt/Insta360/MediaSDK/modelfile/ai_stitch_model.ins"

# Ensure folders exist
LOCAL_VIDEO_PATH.mkdir(parents=True, exist_ok=True)
STITCHED_VIDEO_PATH.mkdir(parents=True, exist_ok=True)

def wait_for_camera_mount():
    print("Waiting for camera connection (Android mode)...")
    while not Path(CAMERA_MOUNT_PATH).exists():
        time.sleep(2)
    print(f"Camera mounted at {CAMERA_MOUNT_PATH}")

def download_insv_files():
    insv_files = []
    for root, dirs, files in os.walk(CAMERA_MOUNT_PATH):
        for file in files:
            if file.lower().endswith(".insv"):
                src = os.path.join(root, file)
                dst = LOCAL_VIDEO_PATH / file
                if not dst.exists():
                    print(f"Copying {file}")
                    subprocess.run(["cp", src, str(dst)], check=True)
                insv_files.append(str(dst))
    return sorted(insv_files)

def group_dual_track_files(insv_files):
    grouped = []
    visited = set()
    for f in insv_files:
        if f in visited: continue
        if "_00_" in f:
            pair = f.replace("_00_", "_10_")
            if pair in insv_files:
                grouped.append((f, pair))
                visited.add(f)
                visited.add(pair)
            else:
                grouped.append((f,))
                visited.add(f)
    return grouped

def stitch_video(pair):
    input_files = list(pair)
    basename = Path(input_files[0]).stem.split("_00_")[0]
    output_file = STITCHED_VIDEO_PATH / f"{basename}_stitched.mp4"

    cmd = [
        SDK_BINARY,
        "--input", *input_files,
        "--output", str(output_file),
        "--ai_model", AI_MODEL_PATH,
        "--stitch_type", "AIFLOW",
        "--flowstate", "true",
        "--directionlock", "true",
        "--bitrate", str(60 * 1000 * 1000)
    ]

    print(f"Stitching {basename}...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"Stitched to {output_file}")
    else:
        print(f"Error stitching {basename}")

def main():
    wait_for_camera_mount()
    insv_files = download_insv_files()
    video_groups = group_dual_track_files(insv_files)
    for pair in video_groups:
        stitch_video(pair)

if __name__ == "__main__":
    main()
