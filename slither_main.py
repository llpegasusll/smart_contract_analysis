import os
import subprocess
import json
import re
from solcx import install_solc, set_solc_version
from solcx.exceptions import UnsupportedVersionError

# Paths to the Solidity files directory and tools output
solidity_dir = "C:\\Users\\stanl\\Desktop\\praccc\\sample"
json_output_dir = "C:\\Users\\stanl\\Desktop\\praccc\\slijson_outputs"

vulnerability_pairs = [
    ('High', 'High'), ('High', 'Low'), ('High', 'Medium'),
    ('Medium', 'High'), ('Medium', 'Medium'),
    ('Low', 'High'), ('Low', 'Medium'),
    ('Informational', 'High'), ('Informational', 'Medium'),
    ('Optimization', 'High')
]

vulnerable_files = []
non_vulnerable_files = []

def get_solidity_version(solidity_file):
    with open(solidity_file, 'r', encoding='utf-8') as file:
        content = file.read()
        match = re.search(r'pragma solidity \^?([\d.]+);', content)
        if match:
            return match.group(1)
    return None

def install_and_set_solc(version):
    print(f"Installing Solidity compiler version {version}...")
    try:
        install_solc(version)
        set_solc_version(version)
        print(f"Solidity compiler version {version} installed and set.")
    except UnsupportedVersionError:
        print(f"Unsupported Solidity version {version} for py-solc-x. Skipping this version.")
        return False
    return True

def run_slither(solidity_file, output_file):
    print(f"Running Slither on {solidity_file}...")
    slither_command = f"slither {solidity_file} --json {output_file}"
    result = subprocess.run(slither_command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Slither failed with error:\n{result.stderr}")
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            slither_results = json.load(file)
        print(f"Slither results for {solidity_file} obtained.")
        return slither_results
    else:
        print(f"Slither did not produce output for {solidity_file}.")
        return {'results': {'detectors': []}}

def is_vulnerable(vulnerability):
    impact = vulnerability.get('impact')
    confidence = vulnerability.get('confidence')
    return (impact, confidence) in vulnerability_pairs

def analyze_vulnerabilities(vulnerabilities):
    significant_vulns = [v for v in vulnerabilities if is_vulnerable(v)]
    return significant_vulns

def compare_results(slither_results, file_path):
    slither_vulns = slither_results['results']['detectors']
    significant_vulns = analyze_vulnerabilities(slither_vulns)
    
    print("Vulnerabilities found by Slither:")
    for vuln in significant_vulns:
        print(f"- {vuln['check']}: {vuln['description']} (Impact: {vuln['impact']}, Confidence: {vuln['confidence']})")

    print("\nComparison:")
    print(f"Total significant vulnerabilities found by Slither: {len(significant_vulns)}")
    if significant_vulns:
        print("The file is considered vulnerable.")
        vulnerable_files.append(file_path)
    else:
        print("The file is not considered vulnerable.")
        non_vulnerable_files.append(file_path)
    print("-" * 50)

def analyze_file(solidity_file):
    solc_version = get_solidity_version(solidity_file)
    if solc_version:
        print(f"Detected Solidity version: {solc_version} for file {solidity_file}")
        if not install_and_set_solc(solc_version):
            return  # Skip the file if Solidity version is not supported
    else:
        print(f"No Solidity version detected for file {solidity_file}, using default version")

    # Generate output file path
    output_file = os.path.join(json_output_dir, os.path.basename(solidity_file) + '.json')
    slither_results = run_slither(solidity_file, output_file)
    
    compare_results(slither_results, solidity_file)

def main():
    # Create the output directory if it does not exist
    if not os.path.exists(json_output_dir):
        os.makedirs(json_output_dir)

    # Clear all existing JSON files in the output directory
    for file in os.listdir(json_output_dir):
        file_path = os.path.join(json_output_dir, file)
        if file.endswith('.json'):
            os.remove(file_path)

    for root, dirs, files in os.walk(solidity_dir):
        for file in files:
            if file.endswith('.sol'):
                file_path = os.path.join(root, file)
                print(f"\nAnalyzing file: {file_path}")
                analyze_file(file_path)

    print("\nSummary of analysis:")
    print("Vulnerable files:")
    for file in vulnerable_files:
        print(f"- {file}")

    print("\nNon-vulnerable files:")
    for file in non_vulnerable_files:
        print(f"- {file}")

if __name__ == "__main__":
    main()
