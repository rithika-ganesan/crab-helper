import os
import sys
import subprocess
import shutil
import re
from dictionaries import samples

def get_cmssw_base():
    """
    Get the CMSSW_BASE environment variable and return both the full path
    and just the release name (e.g. 'CMSSW_14_0_7').

    Returns:
        tuple: (cmssw_base_path, release_name)
    """
    cmssw_base = os.environ.get("CMSSW_BASE")

    if not cmssw_base:
        sys.exit("ERROR: CMSSW_BASE is not set. Please run 'cmsenv' first.")

    release_name = os.path.basename(cmssw_base)

    return cmssw_base, release_name

def change_truncation_settings(cmssw_base, path_to_settings, module, shell_script):
    """
    Check if a file exists at cmssw_base/path_to_settings, and if so,
    run a shell script passing the full path and module as arguments.

    Args:
        cmssw_base (str): path to the CMSSW release (e.g. from get_cmssw_base())
        path_to_settings (str): relative path (from cmssw_base) to the file to check for
        module (str): module name to pass as the second argument to the shell script
        shell_script (str): path to the shell script to execute

    Returns:
        bool: True if the file was found and the script ran, False otherwise
    """
    absolute_path_to_settings = os.path.join(cmssw_base, path_to_settings)

    if not os.path.isfile(absolute_path_to_settings):
        print(f"File not found: {absolute_path_to_settings}")
        return False

    result = subprocess.run(
        [shell_script, absolute_path_to_settings, module],
        check=True
    )

    return True


def rebuild_cmssw(cmssw_base, num_jobs=8, log_path=None):
    """
    cd into cmssw_base/src and run 'scram b clean' followed by 'scram b -j <num_jobs>'.
    Output from both commands is saved to a log file.
 
    Args:
        cmssw_base (str): path to the CMSSW release
        num_jobs (int): number of parallel jobs to pass to 'scram b -j' (default 8)
        log_path (str): where to write the scram output log. Defaults to
            '<cmssw_base>/scram_build.log' if not given.
 
    Returns:
        bool: True if both scram commands succeeded
    """
    src_path = os.path.join(cmssw_base, "src")
 
    if not os.path.isdir(src_path):
        print(f"Directory not found: {src_path}")
        return False
 
    if log_path is None:
        log_path = os.path.join(cmssw_base+'/src', "scram_build.log")
 
    with open(log_path, "w") as log_file:
        log_file.write(f"=== scram b clean ===\n")
        log_file.flush()
        subprocess.run(
            ["scram", "b", "clean"],
            cwd=src_path,
            check=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
 
        log_file.write(f"\n=== scram b -j {num_jobs} ===\n")
        log_file.flush()
        subprocess.run(
            ["scram", "b", "-j", str(num_jobs)],
            cwd=src_path,
            check=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
 
    print(f"scram output saved to {log_path}")
 
    return True
 
 
def apply_truncation_settings(cmssw_base, path_to_settings, module, shell_script, num_jobs=8, log_path=None):
    """
    Change truncation settings, and if successful, rebuild CMSSW.
 
    Args:
        cmssw_base (str): path to the CMSSW release
        path_to_settings (str): relative path (from cmssw_base) to the settings file
        module (str): module name to pass to the shell script
        shell_script (str): path to the shell script to execute
        num_jobs (int): number of parallel jobs to pass to 'scram b -j' (default 8)
        log_path (str): where to write the scram output log (see rebuild_cmssw)
 
    Returns:
        bool: True if settings were changed AND the rebuild succeeded
    """
    settings_changed = change_truncation_settings(cmssw_base, path_to_settings, module, shell_script)
 
    if not settings_changed:
        return False
 
    return rebuild_cmssw(cmssw_base, num_jobs=num_jobs, log_path=log_path)

def fill_template_to_output(template_name, replacements, output_dir, output_filename, use_regex=False):
    """
    Read a template file (located in the same directory as this script),
    apply replacements, and write the result to output_dir under output_filename,
    overwriting any existing file of that name there.

    Args:
        template_name (str): filename of the template (e.g. 'crabConfig_template.py'),
            expected to live alongside this script
        replacements (dict): mapping of {pattern: replacement}
        output_dir (str): directory to write the filled-in file to (created if it doesn't exist)
        output_filename (str): filename to give the filled-in file (e.g. 'crabConfig_run123.py')
        use_regex (bool): whether replacement keys are regex patterns

    Returns:
        str: full path to the written output file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, template_name)

    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r") as f:
        content = f.read()

    for pattern, replacement in replacements.items():
        if use_regex:
            content = re.sub(pattern, replacement, content)
        else:
            content = content.replace(pattern, replacement)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w") as f:
        f.write(content)

    return output_path

def build_replacements_l1tf(l1tf_algorithm, n_events, data_name, truncation_setting, num_threads, output_file_name_append=None):
    """
    Build the replacements dictionary for the L1TrackNtupleMaker_cfg file,
    mapping each placeholder to its corresponding value.

    Args:
        l1tf_algorithm (str): value to substitute for __L1TF_ALGORITHM__
        n_events (int or str): value to substitute for __N_EVENTS__
        data_name (str): key into `samples`; samples[data_name][0] substitutes
            for __DATA_NAME__, and samples[data_name][1] is used to build the
            output filename
        truncation_setting (str): for output filename
        num_threads (int or str): value to substitute for __NUM_THREADS__
        output_file_name_append (str, optional): extra string appended to the
            output filename (e.g. a run number or variant label)

    Returns:
        dict: {placeholder: replacement} ready to pass to fill_template_to_output()
    """
    if data_name not in samples:
        valid_options = ", ".join(samples.keys())
        raise ValueError(f"Invalid data_name '{data_name}'. Valid options are: {valid_options}")

    if output_file_name_append:
        output_file_name_append = '-' + str(output_file_name_append)
    else:
        output_file_name_append = ''

    output_file_name = f'algo_{l1tf_algorithm}-nevents_{n_events}-{samples[data_name][1]}-{truncation_setting}{output_file_name_append}.root'

    return {
        "__L1TF_ALGORITHM__": str(l1tf_algorithm),
        "__N_EVENTS__": str(n_events),
        "__DATA_NAME__": str(samples[data_name][0]),
        "__NUM_THREADS__": str(num_threads),
        "__OUTPUT_FILE_NAME__": str(output_file_name),
    }

def build_crab_config_replacements(request_name, num_threads, input_dataset, num_events, max_memory=None):
    """
    Build the replacements dictionary for the CRAB config template,
    mapping each placeholder to its corresponding value.

    Args:
        request_name (str): value to substitute for __REQUEST_NAME__
        num_threads (int or str): value to substitute for __NUM_THREADS__
        max_memory (int or str): value to substitute for __MAX_MEMORY__
        input_dataset (str): value to substitute for __INPUT_DATASET__
        num_events (int or str): value to substitute for __NUM_EVENTS__

    Returns:
        dict: {placeholder: replacement} ready to pass to fill_template_to_output()
    """

    if max_memory == None:
        base_ = 0
        mb_per_thread = 2000
        max_memory = base_ + mb_per_thread*num_threads

    return {
        "__REQUEST_NAME__": str(request_name),
        "__NUM_THREADS__": str(num_threads),
        "__MAX_MEMORY__": str(max_memory),
        "__INPUT_DATASET__": str(input_dataset),
        "__NUM_EVENTS__": str(num_events),
    }

if __name__ == "__main__":
    cmssw_base, release = get_cmssw_base()
    print(f"CMSSW_BASE path: {cmssw_base}")
    print(f"Release name:    {release}")

    path_to_settings = "src/L1Trigger/TrackFindingTracklet/interface/Settings.h"
    path_to_test = "src/L1Trigger/TrackFindingTracklet/test/"
    module = "ALL"
    shell_script = "./changeTruncationSettings.sh"

    # apply_truncation_settings(cmssw_base, path_to_settings, module, shell_script)

    print("\n=== Test: fill_template_to_output() ===")
    test_replacements = build_replacements_l1tf(
        l1tf_algorithm="HYBRID_SIM",
        n_events=50000,
        data_name="Higgs900",
        output_file_name_append="newCheck",
    )
    test_output_dir = cmssw_base+"/"+path_to_test
    print(test_output_dir)
    l1tfcfg_output_path = fill_template_to_output("L1TrackNtupleMaker_cfg_template.py", test_replacements, test_output_dir, output_filename="L1TrackNtupleMaker_cfg.py")
    print(f"  Result: written to {l1tfcfg_output_path}")

    # test_crab_replacements_auto = build_crab_config_replacements(
    #     request_name="MyRequest_2026",
    #     num_threads=2,
    #     input_dataset="/ZeroBias/Run2024-v1/RAW-MINIAOD",
    #     num_events=1000,
    # )
    # crab_output_path = fill_template_to_output("crab_cfg_template.py", test_crab_replacements_auto, test_output_dir, output_filename="crab_cfg.py")

