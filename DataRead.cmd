#!/bin/bash
#SBATCH --output=/SCRATCH/slloyd/FlowlineGIT/looper_slurms/slurm-%j.out
#SBATCH --job-name="2DSheet_looper"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
set -e
nodes=$(lua -e "dofile('parameters.lua'); print(nodes)")

ID=$1

MAX=30    
STOP_AT=30

echo "Reading Data"
cd "OutputPickles"
mkdir -p run_${ID}
cd ..
cd "OutputPlots"
mkdir -p run_${ID}
cd "run_${ID}"
mkdir -p sheet
cd ../..
nohup mpirun -np 64 python -u ReadResultFile.py "./footprint/run_${ID}" "./OutputPickles/run_${ID}/" > "Initialisation/ScriptOutputs/data_Read${ID}.out"
nohup python -u PlotResults.py "./OutputPickles/run_${ID}" "./OutputPlots/run_${ID}/" > "Initialisation/ScriptOutputs/data_Plot${ID}.out"

if [ "$ID" -eq "$STOP_AT" ]; then
    echo "Reached STOP_AT=$STOP_AT, breaking loop"
     break
fi

ID=$((ID + 1))

if [ "$ID" -gt "$MAX" ]; then
    break
fi

sbatch looper.cmd $ID