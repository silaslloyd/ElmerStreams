#!/bin/bash
#SBATCH --output=./Initialisation/slurm-%j.out
#SBATCH --job-name="FlowlineThermoCoupled"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
set -e
nodes=$(lua -e "dofile('parameters.lua'); print(nodes)")

export DIM=2
module load elmerfem 
echo "Solving for Full Problem"
nohup mpirun -np $nodes ElmerSolver InitialiseT2.sif > Initialisation/ScriptOutputs/InitialiseT2.out 
echo "Done"
echo ""

