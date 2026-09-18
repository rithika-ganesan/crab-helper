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