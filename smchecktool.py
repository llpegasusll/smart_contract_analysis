import subprocess
import os
import re
from solcx import install_solc, set_solc_version
from solcx.exceptions import SolcInstallationError, SolcError, UnsupportedVersionError

solidity_dir = "C:\\Users\\stanl\\Desktop\\praccc\\sample"  # Directory containing Solidity files
output_dir = "C:\\Users\\stanl\\Desktop\\praccc\\smjson_outputs"  # Directory to store SmartCheck output files

# List of vulnerability rules
vulnerability_rules = {
    "SOLIDITY_ADDRESS_HARDCODED",
    "SOLIDITY_ARRAY_LENGTH_MANIPULATION",
    "SOLIDITY_BALANCE_EQUALITY",
    "SOLIDITY_BYTE_ARRAY_INSTEAD_BYTES",
    "SOLIDITY_CALL_WITHOUT_DATA",
    "SOLIDITY_CONSTRUCTOR_RETURN",
    "SOLIDITY_DELETE_ON_DYNAMIC_ARRAYS",
    "SOLIDITY_DEPRECATED_CONSTRUCTIONS",
    "SOLIDITY_DIV_MUL",
    "SOLIDITY_DO_WHILE_CONTINUE",
    "SOLIDITY_ERC20_APPROVE",
    "SOLIDITY_ERC20_FUNCTIONS_ALWAYS_RETURN_FALSE",
    "SOLIDITY_ERC20_INDEXED",
    "SOLIDITY_ERC20_TRANSFER_SHOULD_THROW",
    "SOLIDITY_EXACT_TIME",
    "SOLIDITY_EXTRA_GAS_IN_LOOPS",
    "SOLIDITY_FUNCTION_RETURNS_TYPE_AND_NO_RETURN",
    "SOLIDITY_GAS_LIMIT_IN_LOOPS",
    "SOLIDITY_INCORRECT_BLOCKHASH",
    "SOLIDITY_LOCKED_MONEY",
    "SOLIDITY_MSGVALUE_EQUALS_ZERO",
    "SOLIDITY_OVERPOWERED_ROLE",
    "SOLIDITY_PRAGMAS_VERSION",
    "SOLIDITY_PRIVATE_MODIFIER_DOES_NOT_HIDE_DATA",
    "SOLIDITY_REDUNDANT_FALLBACK_REJECT",
    "SOLIDITY_REVERT_REQUIRE",
    "SOLIDITY_REWRITE_ON_ASSEMBLY_CALL",
    "SOLIDITY_SAFEMATH",
    "SOLIDITY_SEND",
    "SOLIDITY_SHOULD_NOT_BE_PURE",
    "SOLIDITY_SHOULD_NOT_BE_VIEW",
    "SOLIDITY_SHOULD_RETURN_STRUCT",
    "SOLIDITY_TRANSFER_IN_LOOP",
    "SOLIDITY_TX_ORIGIN",
    "SOLIDITY_UINT_CANT_BE_NEGATIVE",
    "SOLIDITY_UNCHECKED_CALL",
    "SOLIDITY_UNUSED_FUNCTION_SHOULD_BE_EXTERNAL",
    "SOLIDITY_UPGRADE_TO_050",
    "SOLIDITY_USING_INLINE_ASSEMBLY",
    "SOLIDITY_VAR",
    "SOLIDITY_VAR_IN_LOOP_FOR",
    "SOLIDITY_VISIBILITY",
    "SOLIDITY_WRONG_SIGNATURE"
}

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
    if version < '0.4.11':
        print(f"Skipping unsupported Solidity version {version} for py-solc-x.")
        return False

    print(f"Installing Solidity compiler version {version}...")
    try:
        install_solc(version)
        set_solc_version(version)
        print(f"Solidity compiler version {version} installed and set.")
    except UnsupportedVersionError:
        print(f"Unsupported Solidity version {version} for py-solc-x. Skipping this version.")
        return False
    except SolcInstallationError:
        print(f"Solidity compiler installation error for version {version}. Skipping this version.")
        return False
    except SolcError:
        print(f"Solidity compiler error for version {version}. Skipping this version.")
        return False
    return True

def run_smartcheck(solidity_file):
    print(f"Running SmartCheck on {solidity_file}...")
    smartcheck_command = f"smartcheck -p {solidity_file}"
    result = subprocess.run(smartcheck_command, shell=True, capture_output=True, text=True)
    
    stderr_file_path = os.path.join(output_dir, 'smartcheck_errors.txt')
    with open(stderr_file_path, 'a') as stderr_file:
        stderr_file.write(result.stderr)
    
    if result.returncode != 0:
        print(f"SmartCheck failed with error. Check {stderr_file_path} for details.")
        return None
    
    return result.stdout

def analyze_vulnerabilities(smartcheck_results):
    # Split the SmartCheck results into lines
    lines = smartcheck_results.splitlines()
    
    # Find the vulnerability counts at the end of the output
    for line in lines:
        parts = line.split(':')
        if len(parts) == 2:
            rule = parts[0].strip()
            count = parts[1].strip()
            if rule in vulnerability_rules and count.isdigit() and int(count) > 0:
                return True
    return False

def analyze_file(solidity_file):
    solc_version = get_solidity_version(solidity_file)
    if solc_version:
        print(f"Detected Solidity version: {solc_version} for file {solidity_file}")
        if not install_and_set_solc(solc_version):
            return  # Skip the file if Solidity version is not supported
    else:
        print(f"No Solidity version detected for file {solidity_file}, using default version")

    smartcheck_results = run_smartcheck(solidity_file)
    
    if smartcheck_results:
        # Save SmartCheck results to a file
        output_file_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(solidity_file))[0]}.txt")
        with open(output_file_path, 'w') as output_file:
            output_file.write(smartcheck_results)
        print(f"Results saved to: {output_file_path}")

        if analyze_vulnerabilities(smartcheck_results):
            vulnerable_files.append(solidity_file)
        else:
            non_vulnerable_files.append(solidity_file)
    else:
        print("No SmartCheck results to display.")

def main():
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Clear all existing output files in the output directory
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if file.endswith('.txt'):
            os.remove(file_path)

    for root, dirs, files in os.walk(solidity_dir):
        for file in files:
            if file.endswith('.sol'):
                file_path = os.path.join(root, file)
                print(f"\nAnalyzing file: {file_path}")
                analyze_file(file_path)

    print("\nAnalysis complete. Check the output directory for results.")
    print("\nSummary of analysis:")
    print("Vulnerable files:")
    for file in vulnerable_files:
        print(f"- {file}")

    print("\nNon-vulnerable files:")
    for file in non_vulnerable_files:
        print(f"- {file}")

if __name__ == "__main__":
    main()

