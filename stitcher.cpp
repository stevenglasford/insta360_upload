#include <iostream>
#include <vector>
#include <string>
#include <memory>

#include "ins_stitcher.h"

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <input_00.insv> <input_10.insv> <output.mp4>" << std::endl;
        return 1;
    }

    std::string input_file_00 = argv[1];
    std::string input_file_10 = argv[2];
    std::string output_file = argv[3];

    std::vector<std::string> input_paths = {input_file_00, input_file_10};

    ins::InitEnv();  // Initialize the SDK

    std::shared_ptr<ins::Stitcher> stitcher = std::make_shared<ins::Stitcher>();

    // Set input and output paths
    stitcher->SetInputPath(input_paths);
    stitcher->SetOutputPath(output_file);

    // Output settings
    stitcher->SetOutputSize(7680, 3840); // 8K
    stitcher->EnableH265Encoder();       // H.265 hardware encoding
    stitcher->SetOutputBitRate(100 * 1000 * 1000); // 100 Mbps

    // AI Stitching model (required)
    stitcher->SetAiStitchModelFile("/usr/local/share/MediaSDK/modelfile/ai_stitch_model.ins");
    stitcher->SetStitchType(ins::STITCH_TYPE::AIFLOW);

    // Optional corrections
    stitcher->EnableFlowState(true);
    stitcher->EnableDirectionLock(true);
    stitcher->EnableStitchFusion(true);

    // Set lens guard type if applicable
    stitcher->SetCameraAccessoryType(ins::CameraAccessoryType::kOnex3LensGuardS);

    std::cout << "Starting stitching...\n";
    stitcher->StartStitch();
    std::cout << "Stitching complete: " << output_file << "\n";

    return 0;
}
