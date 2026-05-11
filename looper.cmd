#!/bin/bash
#SBATCH --output=/SCRATCH/slloyd/FlowlineGIT/looper_slurms/slurm-%j.out
#SBATCH --job-name="2DSheet_looper"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
nodes=$(lua -e "dofile('parameters.lua'); print(nodes)")

ID=$1


RESTART=$(cat restart.txt)

module load elmerfem

OUTDIR="SIFs"
mkdir -p "$OUTDIR"

echo "Iteration $ID"
echo "Using restart: $RESTART"

SIF=run_${ID}.sif

sed \
    -e "s|__PREVNAME__|$RESTART|g" \
    -e "s|__CURRENTNAME__|run_${ID}|g" \
    case_template.sif > "$OUTDIR/$SIF"

RESTART="run_${ID}.result"
echo "$RESTART" > restart.txt

echo "running loop $ID"
timeout 71h mpirun -np $nodes ElmerSolver "$OUTDIR/$SIF" > "Initialisation/ScriptOutputs/run_${ID}.out"


sbatch DataRead.cmd $ID

