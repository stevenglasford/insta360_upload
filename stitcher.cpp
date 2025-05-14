#include <iostream>
#include <vector>
#include <string>
#include <memory>

#include "ins_stitcher.h"  // Adjust to your actual include path
#include "video_stitcher.h"
#include "log/log.h"

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <input_00.insv> <input_10.insv> <output.mp4>" << std::endl;
        return 1;
    }

    std::string input_file_00 = argv[1];
    std::string input_file_10 = argv[2];
    std::string output_file = argv[3];

    std::vector<std::string> input_paths = {input_file_00, input_file_10};

    ins::InitEnv();
    ins::SetLogLevel(ins::InsLogLevel::INFO);

    auto stitcher = std::make_shared<ins::VideoStitcher>();

    stitcher->SetInputPath(input_paths);
    stitcher->SetOutputPath(output_file);
    stitcher->SetOutputSize(7680, 3840);  // 8K output
    stitcher->EnableH265Encoder();
    stitcher->SetOutputBitRate(100 * 1000 * 1000); // 100 Mbps

    // AI Stitching
    std::string ai_model = "/usr/local/share/MediaSDK/modelfile/ai_stitch_model.ins";
    stitcher->SetAiStitchModelFile(ai_model);
    stitcher->SetStitchType(ins::STITCH_TYPE::AIFLOW);

    // Stabilization and correction
    stitcher->EnableFlowState(true);
    stitcher->EnableDirectionLock(true);
    stitcher->EnableStitchFusion(true);

    // You can change the lens guard type here if needed
    stitcher->SetCameraAccessoryType(ins::CameraAccessoryType::kOnex3LensGuardS);

    std::cout << "Starting stitching process..." << std::endl;
    stitcher->StartStitch();
    std::cout << "Stitching complete: " << output_file << std::endl;

    return 0;
}
