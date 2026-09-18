### File descriptions 

`utils.py`: contains functions 
`dictionaries.py`: contains dictionaries with sample and module information 
`driver.py`: chains functions together to run a single job 
`batch_jobs.py`: submit multiple jobs at once

`changeTruncationSettings.sh`: edits settings file 
`L1TrackNtupleMaker_cfg_template.py`, `crab_cfg_template.py`: templates 

To run single jobs from the command line, add the following line to your bash_profile:
```
alias crabdriver="python3 /afs/cern.ch/user/**j**/**janedoe**/private/crab-helper/driver.py"
```

To edit and multiple jobs, add to bash_profile:
```
crabbatcher="/afs/cern.ch/user/r/rganesan/private/crab-helper/batch_jobs.py"
``` 
and run:
```
code $crabbatcher       # to edit. use whatever text editor to open the file and change the params
python3 $crabbatcher    # run 
```