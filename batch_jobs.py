import subprocess 

modules = ['IR', 'VMR', 'TB', 'MP', 'PC', 'TP', 'TPD', 'DR', 'ALL', 'NONE']
samples = ['DispSUSY', 'Higgs900', 'Higgs1500']
algos = ['HYBRID', 'HYBRID_DISPLACED', 'HYBRID_NEWKF', 'HYBRID_SIM', 'HYBRID_SIM_DISPLACED']

n_events_by_sample = {
    'DispSUSY': 10000, 'Higgs900': 50000, 'Higgs1500': 50000
}

num_threads_by_sample = {
    'DispSUSY': 1, 'Higgs900': 1, 'Higgs1500': 1
}