import os
import subprocess
import json
import re

# Path to the directory containing your Solidity files
solidity_files_path = "C:\\Users\\stanl\\Desktop\\praccc\\smaple2"

# List of specific detectors you want to run
#detectors_to_run = ["reentrancy-eth", "weak-prng", "suicidal"]

# Function to detect Solidity version
def detect_solidity_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        match = re.search(r'pragma solidity \^?([0-9]+\.[0-9]+\.[0-9]+);', content)
        if match:
            return match.group(1)
    return None

# Function to run Slither with specific detectors on a single file
def run_slither(file_path, solc_version):
    slither_data = []
    try:
        subprocess.run(["solc-select", "use", solc_version, "--always-install"], check=True)
    except Exception as e:
        print(f"An error occurred while switching to solc version {solc_version}: {str(e)}")
        return None

    # for detector in detectors:
    # try:
    output_file = "C:\\Users\\stanl\\Desktop\\praccc\\slteoutput.json"
    result = subprocess.run(
        ["slither", file_path, "--json", output_file],#, "--detect", detector],
        capture_output=True,
        text=True
    )
    # if result.returncode != 0:
    #     print(f"Error running Slither on {file_path} with detector {detector}:\n{result.stderr}")
    #     # continue
    
    if os.path.exists(output_file):
        with open(output_file) as f:
            data = json.load(f)
        slither_data.append(data)
        os.remove(output_file)  # Clean up the JSON file after use
    else:
        print(f"Slither did not generate the expected output file {output_file} for {file_path} with detector ")#{detector}")
# except Exception as e:
#     print(f"An error occurred while running Slither on {file_path} with detector {detector}: {str(e)}")
    return slither_data

# Iterate over all files in the directory and run Slither on each with specific detectors
all_data = []
for file_name in os.listdir(solidity_files_path):
    if file_name.endswith(".sol"):
        file_path = os.path.join(solidity_files_path, file_name)
        solc_version = detect_solidity_version(file_path)
        if solc_version:
            data = run_slither(file_path, solc_version)
            if data:
                all_data.extend(data)
        else:
            print(f"Could not detect Solidity version for {file_path}")

# Save the collected data to a file
with open("slither_test.json", "w") as f:
    json.dump(all_data, f)
