#!/bin/bash
#SBATCH --output=./slurm-%j.out
#SBATCH --job-name="dataread"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
nohup mpirun -np 64 python -u ReadResultFile.py "./footprint/InitT2" "./OutputPickles/T2" > "Initialisation/ScriptOutputs/dataT2.out"
nohup python -u PlotResults.py "./OutputPickles/T2" "./OutputPlots/T2/" > ./"Initialisation/ScriptOutputs/plotT2.out"
echo "DONE"
