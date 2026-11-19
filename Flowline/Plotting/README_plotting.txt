18/11/2026
This folder contains code to read vtu files and plot the results.
Many of the scripts are currently a work in progress.

The "FromSilas" folder contains Silas' old scripts.

The scripts for reading vtus are:
- readvtu.py: a first attempt at reading from (p)vtu files
- readvtu_basal.py: reads the relavant basal quantities from a single (p)vtu file and saves as a pickle file
- readvtu_basal_all.py: reads the basal quantities from a time series of (p)vtu fies and saves as pickle files
- readvtu_2D.py: WORK IN PROGRESS - will be used to extract bulk quantities from (p)vtu files

The scripts for plotting the pickle data extracted from (p)vtu files
- plot_basal.py: plots basal quantities for a single time snapshot
- plot_basal_all.py: plots basal quantities for each snapshot in a time series and makes a gif animation
- plot_2D.py: WORK IN PROGRESS - will be used to plot bulk ice quantities