#!/bin/bash
#SBATCH --output=/SCRATCH/slloyd/FlowlineGIT/slurm-%j.out
#SBATCH --job-name="dataread"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
nohup mpirun -np 64 python -u ReadResultFile.py "./footprint/InitialT2" "./OutputPickles/FixedRun" > "Initialisation/ScriptOutputs/dataFixedrun.out"
nohup python -u PlotResults.py "./OutputPickles/FixedRun" "./OutputPlots/FixedRun/" > ./"Initialisation/ScriptOutputs/FixedRun.out"
echo "DONE"
