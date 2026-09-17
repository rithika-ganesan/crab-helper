import os
import sys
import subprocess
import shutil

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
        log_path = os.path.join(cmssw_base, "scram_build.log")
 
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





if __name__ == "__main__":
    cmssw_base, release = get_cmssw_base()
    print(f"CMSSW_BASE path: {cmssw_base}")
    print(f"Release name:    {release}")

    path_to_settings = "src/L1Trigger/TrackFindingTracklet/interface/Settings.h"
    module = "ALL"
    shell_script = "./changeTruncationSettings.sh"

    apply_truncation_settings(cmssw_base, path_to_settings, module, shell_script)