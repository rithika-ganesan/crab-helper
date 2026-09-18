
# 0 = das link to sample
# 1 = description for plots/files
# 2 = descriptions for titles
# 3 = llp mass
# 4 = llp ctau


samples = {
    'DispSUSY': ['/DisplacedSUSY_stopToBottom_M-800_50mm_TuneCP5_14TeV-pythia8/Phase2Spring24DIGIRECOMiniAOD-PU200_AllTP_140X_mcRun4_realistic_v4-v1/GEN-SIM-DIGI-RAW-MINIAOD', 
                 'DispSUSY_stopToBottom_800-GeV_50-mm', 
                 'Displaced SUSY (stop to bottom)', 
                 800,
                 50],
    'Higgs900': ['/HTo2LongLivedTo4mu_MH-125_MFF-12_CTau-900mm_TuneCP5_14TeV-pythia8/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v1/GEN-SIM-DIGI-RAW-MINIAOD',
                 'HTo2LongLivedTo4mu_MH-125_MFF-12_CTau-900mm',
                 'Higgs to 2 LLPs to 4 mus',
                 12,
                 900],
    'Higgs1500': ['/HTo2LongLivedTo4mu_MH-125_MFF-25_CTau-1500mm_TuneCP5_14TeV-pythia8/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v1/GEN-SIM-DIGI-RAW-MINIAOD',
                  'HTo2LongLivedTo4mu_MH-125_MFF-25_CTau-1500mm',
                  'Higgs to 2 LLPs to 4 mus',
                  25,
                  1500]
}

algos = ['HYBRID', 'HYBRID_DISPLACED', 'HYBRID_NEWKF', 'HYBRID_SIM', 'HYBRID_SIM_DISPLACED']

module_labels={
    'IR': "InputRouter",
    'VMR': "VMRouter",
    'TB': "TrackBuilder",
    'MP': "MatchProcesser",
    'PC': "ProjectionCalculator",
    'TP': "TrackletProcesser",
    'TPD': "TPDisplaced",
    'DR': "DuplicateRemoval",
    'TRE': "No truncation", #"TRE",
    'ALL': "Global truncation",
    'NONE': "No truncation",
    'TPDPLUSMP': "TPD, MP"
}

module_desc = {key: f"{key.lower()}_truncated" for key in module_labels.keys()}
