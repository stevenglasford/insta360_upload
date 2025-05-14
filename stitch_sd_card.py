import os
import glob
import subprocess
from pathlib import Path
from datetime import datetime

def find_dual_tracks(input_dir):
    """Finds _00_/_10_ .insv file pairs."""
    all_files = sorted(glob.glob(os.path.join(input_dir, "*_00_*.insv")))
    paired_files = []
    for f in all_files:
        match = f.replace("_00_", "_10_")
        if os.path.exists(match):
            paired_files.append((f, match))
    return paired_files

def stitch_with_cpp_wrapper(input_00, input_10, output_path, wrapper_path="./insta360_stitcher"):
    """Calls the compiled C++ stitcher binary with full arguments."""
    try:
        result = subprocess.run(
            [
                wrapper_path,
                "-inputs", input_00, input_10,
                "-output", str(output_path),
                "-ai_stitching_model", "/home/preston/Documents/Linux_CameraSDK-2.0.2-build1-20250418+MediaSDK-3.0.1-build1-20250418/libMediaSDK-dev-3.0.1-20250418-amd64/modelfile/ai_stitcher_v2.ins",
                "-stitch_type", "aistitch",
                "-enable_flowstate",
                "-enable_directionlock",
                "-enable_h265_encoder",
                "-bitrate", "60000000",
                "-output_size", "3840x1920"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print("Stitching success:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Stitching failed:\n", e.stderr)
        return False

def upload_to_backblaze(file_path, b2_file_name):
    """Uploads the stitched video to Backblaze B2 using CLI."""
    try:
        result = subprocess.run(
            ['backblaze-b2', 'upload-file', '360-videos-insta360', str(file_path), b2_file_name],
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
    wrapper_bin = "./insta360_stitcher"  # Adjust if necessary

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    pairs = find_dual_tracks(input_dir)

    for i, pair in enumerate(pairs):
        timestamp = datetime.fromtimestamp(os.path.getmtime(pair[0])).strftime("%Y%m%d_%H%M%S")
        output_filename = f"stitched_{timestamp}_{i:03}.mp4"
        output_path = Path(output_dir) / output_filename
        log_path = Path(log_dir) / f"stitch_log_{timestamp}_{i:03}.txt"

        print(f"\nProcessing pair {i + 1}/{len(pairs)}")
        print(f"  Input files:\n    {pair[0]}\n    {pair[1]}")
        print(f"  Output: {output_path}")

        if not stitch_with_cpp_wrapper(pair[0], pair[1], output_path, wrapper_path=wrapper_bin):
            print("Skipping upload due to stitching error.")
            continue

        if upload_to_backblaze(output_path, output_filename):
            print(f"Deleting local stitched file: {output_path}")
            os.remove(output_path)
        else:
            print(f"Upload failed. Keeping: {output_path}")

if __name__ == "__main__":
    main()
