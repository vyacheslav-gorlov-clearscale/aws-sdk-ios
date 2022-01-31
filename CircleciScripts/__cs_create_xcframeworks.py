import os
import sys
import shutil

from __cs_framework_list import xcframeworks
from functions import log, run_command

PWD = os.getcwd()

IOS_DEVICE_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/iOS/"
IOS_SIMULATOR_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/Simulator/"
CATALYST_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/Catalyst/"
TVOS_DEVICE_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/tvOS/"
TVOS_SIMULATOR_ARCHIVE_PATH = f"{PWD}/xcframeworks/output/tvOS-Simulator/"
XCFRAMEWORK_PATH = f"{PWD}/xcframeworks/output/XCF/"

def create_catalyst_archive(framework, project_file):
    archive_path = f"{CATALYST_ARCHIVE_PATH}{framework}"
    destination = "generic/platform=macOS,variant=Mac Catalyst,name=Any Mac"
    cmd = [
        "xcodebuild",
        "archive",
        "-project",
        project_file,
        "-scheme",
        framework,
        "-destination",
        destination,
        "-archivePath",
        archive_path,
        "SKIP_INSTALL=NO",
        "BUILD_LIBRARY_FOR_DISTRIBUTION=YES",
        "SWIFT_SERIALIZE_DEBUGGING_OPTIONS=NO",
        "RUN_CLANG_STATIC_ANALYZER=0"
    ]
    
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created Catalyst archive {framework} {destination}")
    else:
        log(f"Could not create xcodebuild archive: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)

def create_iOS_archive(framework, project_file, build_for_device):
    if build_for_device:
        archive_path = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}"
        destination = "generic/platform=iOS"
    else:
        archive_path = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}"
        destination = "generic/platform=iOS Simulator"
    cmd = [
        "xcodebuild",
        "archive",
        "-project",
        project_file,
        "-scheme",
        framework,
        "-destination",
        destination,
        "-archivePath",
        archive_path,
        "SKIP_INSTALL=NO",
        "BUILD_LIBRARY_FOR_DISTRIBUTION=YES",
        "RUN_CLANG_STATIC_ANALYZER=0"
    ]
    
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created iOS archive {framework} {destination}")
    else:
        log(f"Could not create xcodebuild archive: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)

def create_tvOS_archive(framework, project_file, build_for_device):
    if build_for_device:
        archive_path = f"{TVOS_DEVICE_ARCHIVE_PATH}{framework}"
        destination = "generic/platform=tvOS"
    else:
        archive_path = f"{TVOS_SIMULATOR_ARCHIVE_PATH}{framework}"
        destination = "generic/platform=tvOS Simulator"
    cmd = [
        "xcodebuild",
        "archive",
        "-project",
        project_file,
        "-scheme",
        framework,
        "-destination",
        destination,
        "-archivePath",
        archive_path,
        "SKIP_INSTALL=NO",
        "BUILD_LIBRARY_FOR_DISTRIBUTION=YES",
        "RUN_CLANG_STATIC_ANALYZER=0"
    ]
    
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created tvOS archive {framework} {destination}")
    else:
        log(f"Could not create xcodebuild archive: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)

def map_framework_to_project(framework_list):
    framework_map = {}
    cmd = [
        "xcodebuild",
        "-project",
        "AWSiOSSDKv2.xcodeproj",
        "-list",
    ] 
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"List of schema found")
    else:
        log(f"Xcodebuild list failed: output: {out}; error: {err}")
        sys.exit(exit_code)

    for framework in framework_list:
        if framework not in str(out):
            framework_map[framework] = "./AWSAuthSDK/AWSAuthSDK.xcodeproj"
        else:
            framework_map[framework] = "AWSiOSSDKv2.xcodeproj"
    return framework_map

project_dir = os.getcwd()
log(f"Creating XCFrameworks in {project_dir}")
framework_map = map_framework_to_project(xcframeworks)

# Archive all the frameworks.
for framework in xcframeworks:
#    create_tvOS_archive(framework=framework, project_file=framework_map[framework], build_for_device=True)
#    create_tvOS_archive(framework=framework, project_file=framework_map[framework], build_for_device=False)
    create_iOS_archive(framework=framework, project_file=framework_map[framework], build_for_device=True)
    create_iOS_archive(framework=framework, project_file=framework_map[framework], build_for_device=False)
    create_catalyst_archive(framework=framework, project_file=framework_map[framework])

# Create XCFramework using the archived frameworks.
for framework in xcframeworks:
    tvos_device_framework = f"{TVOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    tvos_device_debug_symbols = f"{TVOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    tvos_simulator_framework = f"{TVOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    tvos_simulator_debug_symbols = f"{TVOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    ios_device_framework = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    ios_device_debug_symbols = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    ios_simulator_framework = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    ios_simulator_debug_symbols = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    catalyst_framework = f"{CATALYST_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    catalyst_debug_symbols = f"{CATALYST_ARCHIVE_PATH}{framework}.xcarchive/dSYMs/{framework}.framework.dSYM"
    
    xcframework = f"{XCFRAMEWORK_PATH}{framework}.xcframework"
    cmd = [
        "xcodebuild",
        "-create-xcframework",
        "-framework",
        ios_device_framework,
        "-debug-symbols",
        ios_device_debug_symbols,
         "-framework",
        ios_simulator_framework,
        "-debug-symbols",
        ios_simulator_debug_symbols,
        "-framework",
        catalyst_framework,
        "-debug-symbols",
        catalyst_debug_symbols,
#        "-framework",
#        tvos_device_framework,
#        "-debug-symbols",
#        tvos_device_debug_symbols,
#         "-framework",
#        tvos_simulator_framework,
#        "-debug-symbols",
#        tvos_simulator_debug_symbols,
        "-output",
        xcframework
    ]
    
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created XCFramework for {framework}")
    else:
        log(f"Could not create XCFramework: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)

shutil.rmtree(IOS_DEVICE_ARCHIVE_PATH)
shutil.rmtree(IOS_SIMULATOR_ARCHIVE_PATH)
#shutil.rmtree(TVOS_DEVICE_ARCHIVE_PATH)
#shutil.rmtree(TVOS_SIMULATOR_ARCHIVE_PATH)
shutil.rmtree(CATALYST_ARCHIVE_PATH)
