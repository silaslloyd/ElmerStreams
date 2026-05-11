Repo for initialising flowline variables in thermo-coupled ice sheet. 

To use: 
first run Initialise.cmd
    This sets up the geometry and solves for an initial temperature field. 
Then run either: 
    InitialiseT2.sif > fully coupled flowline using previously intialised IC.
    read.cmd > converts output data into pickles and then produces a plot
OR run:
    looper.cmd: runs a fully coupled problem, extracts data, plots, and then loops, restarting from the final timestep of the previous run. Allows for indefinite runs