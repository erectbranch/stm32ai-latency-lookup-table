# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

def analyze_footprints(report=None):
    activations_ram = report.ram_size / 1024
    runtime_ram = report.estimated_library_ram_size / 1024
    total_ram = activations_ram + runtime_ram
    weights_rom = report.rom_size / 1024
    code_rom = report.estimated_library_flash_size / 1024
    total_flash = weights_rom + code_rom
    macc = report.macc / 1e6
    print("[INFO] : STM32Cube.AI model memory footprint")
    print("[INFO] : MACCs : {} (M)".format(macc))
    print("[INFO] : Total Flash : {0:.1f} (KiB)".format(total_flash))
    print("[INFO] :     Flash Weights  : {0:.1f} (KiB)".format(weights_rom))
    print("[INFO] :     Estimated Flash Code : {0:.1f} (KiB)".format(code_rom))
    print("[INFO] : Total RAM : {0:.1f} (KiB)".format(total_ram))
    print("[INFO] :     RAM Activations : {0:.1f} (KiB)".format(activations_ram))
    print("[INFO] :     RAM Runtime : {0:.1f} (KiB)".format(runtime_ram))

def analyze_inference_time(report=None):
    cycles = report.cycles
    inference_time = report.duration_ms
    fps = 1000.0/inference_time
    print("[INFO] : Number of cycles : {} ".format(cycles))
    print("[INFO] : Inference Time : {0:.1f} (ms)".format(inference_time))
    print("[INFO] : FPS : {0:.1f}".format(fps))
    return fps

def get_inference_time(report=None):
    cycles = report.cycles
    inference_time = report.duration_ms
    fps = 1000.0/inference_time
    print("[INFO] : Number of cycles : {} ".format(cycles))
    print("[INFO] : Inference Time : {0:.1f} (ms)".format(inference_time))
    print("[INFO] : FPS : {0:.1f}".format(fps))
    return inference_time