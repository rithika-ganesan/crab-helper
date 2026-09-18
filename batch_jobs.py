import subprocess 

# all options 
# modules = ['IR', 'VMR', 'TB', 'MP', 'PC', 'TP', 'TPD', 'DR', 'ALL', 'NONE']
# samples = ['DispSUSY', 'Higgs900', 'Higgs1500']
# algos = ['HYBRID', 'HYBRID_DISPLACED', 'HYBRID_NEWKF', 'HYBRID_SIM', 'HYBRID_SIM_DISPLACED']

# chosen options 

build = True
test = False
modules = ['IR', 'VMR', 'TB'] #, 'MP', 'PC', 'TP', 'TPD', 'DR', 'ALL', 'NONE']
samples = ['DispSUSY', 'Higgs900', 'Higgs1500']
algos = ['HYBRID'] 

n_events_by_sample = {
    'DispSUSY': 10000, 'Higgs900': 50000, 'Higgs1500': 50000
}

num_threads_by_sample = {
    'DispSUSY': 4, 'Higgs900': 4, 'Higgs1500': 4
}

script_path = "/afs/cern.ch/user/r/rganesan/private/crab-helper/driver.py" 

# loop 
# does not rebuild per module

for module in modules:
    for si, sample in enumerate(samples):
        n_events, num_threads = n_events_by_sample[sample], num_threads_by_sample[sample]

        for ai, algo in enumerate(algos):
            new_build = (si == 0) and (ai == 0) and (build == True)

            if algo == "HYBRID" and sample == "Higgs900" and module == "ALL": 
                continue

            command = [
                "python3", script_path,
                "--module", module,
                "--l1tf_algorithm", algo,
                "--n_events", str(n_events),
                "--data_name", sample,
                "--num_threads", str(num_threads),
            ]

            # if not new_build:
            #     command.append("--nobuild")

            if test == True:
                command.append("--test")

            print(f"Running: {' '.join(command)}")
            subprocess.run(command, check=True)
