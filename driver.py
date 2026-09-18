from utils import *
from dictionaries import *
import argparse
import os 
import sys
import subprocess

# check that cmssw is active
cmssw_base, release = get_cmssw_base()
print(f"\nRunning {release}. \n")

script_dir = os.path.dirname(os.path.abspath(__file__))

# get args
parser = argparse.ArgumentParser(description="Submit CRAB jobs with configurable parameters.")
parser.add_argument("-m", "--module", type=str, required=True,
                        help="Module name to pass to the truncation settings shell script")
parser.add_argument("-a", "--l1tf_algorithm", type=str, required=True, choices=algos,
                     help=f"L1 track finding algorithm to use. Valid options: {', '.join(algos)}")
parser.add_argument("-n", "--n_events", type=int, required=True,
                        help="Number of events to process")
parser.add_argument("-s", "--data_name", type=str, required=True,
                        help=f"Key into the samples dictionary. Valid options: {', '.join(samples.keys())}")
parser.add_argument("-o", "--output_file_name_append", type=str, default=None,
                        help="Optional string appended to the output filename")
parser.add_argument("-nthreads", "--num_threads", type=int, default=4,
                        help="Number of threads to request")
parser.add_argument("--max_memory", type=int, default=None,
                     help="Max memory in MB. If omitted, calculated automatically from num_threads")
parser.add_argument("--test", "--no-submit", dest="submit", action="store_false", default=True,
                     help="Skip submitting the CRAB job (submission happens by default)")
parser.add_argument("-nb", "--noscram", "--no-build", "--nobuild", dest="build", action="store_false", default=True,
                     help="Skip rebuilding CMSSW (rebuild happens by default)")

args = parser.parse_args()

# options
path_to_settings = "src/L1Trigger/TrackFindingTracklet/interface/Settings.h"
path_to_test = "src/L1Trigger/TrackFindingTracklet/test/"

l1_cfg_template = os.path.join(script_dir, "L1TrackNtupleMaker_cfg_template.py")
crab_cfg_template = os.path.join(script_dir, "crab_cfg_template.py")
shell_script = os.path.join(script_dir, "./changeTruncationSettings.sh")

file_output_dir = cmssw_base+"/"+path_to_test
output_filename_l1tf="L1TrackNtupleMaker_cfg.py" # this is hardcoded in the crab template !! do not change unless you change it everywhere
output_filename_crab="crab_cfg.py"

# truncate 
settings_changed = change_truncation_settings(
    cmssw_base,
    path_to_settings,
    args.module,
    shell_script,
)

if not settings_changed:
    sys.exit(f"ERROR: Failed to change truncation settings using {shell_script}")

if args.build == True:
    print("Rebuilding CMSSW...")
    rebuild_cmssw(cmssw_base, log_path=file_output_dir+"/scram_log.log")
    print(f"Truncation settings updated for module: {args.module}. \n")
else:
    print("Using existing CMSSW build!\n")

# change l1tf file 
l1tf_replacements = build_replacements_l1tf(
    l1tf_algorithm=args.l1tf_algorithm,
    n_events=args.n_events,
    data_name=args.data_name,
    truncation_setting=args.module,
    num_threads=args.num_threads,
    output_file_name_append=args.output_file_name_append,
)

l1tf_output_path = fill_template_to_output(
    l1_cfg_template,
    l1tf_replacements,
    file_output_dir,
    output_filename_l1tf,
)

print(f"L1TrackNtupleMaker_cfg config written to {l1tf_output_path}.\n")

# change crab config file 
if args.output_file_name_append == None:
    args.output_file_name_append = ''
else:
    args.output_file_name_append = '-'+str(args.output_file_name_append)
request_name = f'algo_{args.l1tf_algorithm}-nevents_{args.n_events}-sample_{samples[args.data_name][1]}{args.output_file_name_append}-{module_desc[args.module.upper()]}'

crab_replacements = build_crab_config_replacements(
    request_name=request_name,
    num_threads=args.num_threads,
    input_dataset=samples[args.data_name][0],
    num_events=args.n_events,
     max_memory=args.max_memory
)

crab_output_path = fill_template_to_output(
    crab_cfg_template,
    crab_replacements,
    file_output_dir,
    output_filename_crab,
)

print(f"CRAB config written to {crab_output_path}.\n")

if args.submit == True:
    print(f"Submitting CRAB job: {request_name}")
    subprocess.run(
        ["crab", "submit", output_filename_crab],
        cwd=file_output_dir,
        check=True,
    )