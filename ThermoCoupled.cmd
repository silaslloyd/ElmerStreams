#!/bin/bash
#SBATCH --output=./slurms/ThermoCoupled_slurm-%j.out
#SBATCH --job-name="FlowlineThermoCoupled"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

set -e

if [ -z "$1" ]; then
    echo "ERROR: No run name provided."
    echo "Usage: sbatch script.sh <run_name>"
    exit 1
fi

RUNNAME=$1

SIF_TEMPLATE="ThermoCoupled_template.sif"
SIF_FILE="${RUNNAME}.sif"
sed "s/__RUNNAME__/${RUNNAME}/g" "${SIF_TEMPLATE}" > "${SIF_FILE}"

nodes=$(lua -e "dofile('parameters.lua'); print(nodes)")

mkdir -p "ThermoCoupledScriptOutputs"
export DIM=2
module load elmerfem 
echo "Solving for Full ThermoCoupled Problem: ${RUNNAME}"
nohup mpirun -np $nodes ElmerSolver "${SIF_FILE}" > ThermoCoupledScriptOutputs/${RUNNAME}.out 
echo "Done"
echo ""

cd OutputPlots
mkdir -p ${RUNNAME}
cd ${RUNNAME}
mkdir -p PNGs
cd ../../

nohup mpirun -np 64 python -u ReadResultFile.py "./footprint/${RUNNAME}" "./OutputPickles/${RUNNAME}" > "ThermoCoupledScriptOutputs/data_${RUNNAME}.out"
nohup python -u PlotResults.py "./OutputPickles/${RUNNAME}" "./OutputPlots/${RUNNAME}/" > "ThermoCoupledScriptOutputs/plot_${RUNNAME}.out"
echo "DONE"
