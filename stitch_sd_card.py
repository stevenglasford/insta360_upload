import os
import glob
import ctypes
import subprocess
from pathlib import Path
from datetime import datetime

# Load MediaSDK shared library
lib = ctypes.CDLL('/usr/lib/libMediaSDK.so')


from MediaSDK import VideoStitcher, STITCH_TYPE, CameraAccessoryType

def find_dual_tracks(input_dir):
    all_files = sorted(glob.glob(os.path.join(input_dir, "*_00_*.insv")))
    paired_files = []
    for f in all_files:
        base = f.replace("_00_", "_10_")
        if os.path.exists(base):
            paired_files.append((f, base))
    return paired_files

def stitch_8k_video(pair, output_path, log_path=None):
    _00_file, _10_file = pair
    input_paths = [_00_file, _10_file]
    video_stitcher = VideoStitcher()
    video_stitcher.InitEnv()

    if log_path:
        video_stitcher.SetLogPath(log_path)

    video_stitcher.SetInputPath(input_paths)
    video_stitcher.SetOutputPath(str(output_path))
    video_stitcher.SetOutputSize(7680, 3840)
    video_stitcher.EnableH265Encoder()
    video_stitcher.SetOutputBitRate(100 * 1000 * 1000)
    video_stitcher.SetAiStitchModelFile("/usr/local/share/MediaSDK/modelfile/ai_stitch_model.ins")
    video_stitcher.SetStitchType(STITCH_TYPE.AIFLOW)
    video_stitcher.EnableFlowState(True)
    video_stitcher.EnableDirectionLock(True)
    video_stitcher.EnableStitchFusion(True)
    video_stitcher.SetCameraAccessoryType(CameraAccessoryType.kOnex3LensGuardS)

    print(f"Stitching {_00_file} + {_10_file} → {output_path}")
    video_stitcher.StartStitch()
    print("Stitching complete.")

def upload_to_backblaze(file_path, b2_file_name):
    try:
        result = subprocess.run(
            ['backblaze-b2', '360-videos-insta360', str(file_path), b2_file_name],
            check=True,
            capture_output=True,
            text=True
        )
        print("Upload complete:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Upload failed:\n", e.stderr)
        return False

def main():
    input_dir = "/mount/insta"
    output_dir = "/home/preston/Downloads/temp"
    log_dir = "/home/preston/Downloads/uploadLogs"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    pairs = find_dual_tracks(input_dir)

    for i, pair in enumerate(pairs):
        # Use timestamp from original file for uniqueness and traceability
        timestamp = datetime.fromtimestamp(os.path.getmtime(pair[0])).strftime("%Y%m%d_%H%M%S")
        output_file_name = f"stitched_{timestamp}_{i:03}.mp4"
        output_path = Path(output_dir) / output_file_name
        log_path = Path(log_dir) / f"stitch_log_{timestamp}_{i:03}.txt"

        stitch_8k_video(pair, output_path, log_path)

        if upload_to_backblaze(output_path, output_file_name):
            print(f"Deleting local copy: {output_path}")
            os.remove(output_path)
        else:
            print(f"Keeping local copy due to failed upload: {output_path}")

if __name__ == "__main__":
    main()
