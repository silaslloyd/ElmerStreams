#!/bin/bash
#SBATCH --output=./Initialisation/slurm-%j.out
#SBATCH --job-name="FlowlineInit"
#SBATCH --ntasks=64
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
set -e
nodes=$(lua -e "dofile('parameters.lua'); print(nodes)")

export DIM=2

echo "Building Result Directories"
cd Initialisation
mkdir -p ScriptOutputs
cd ..
mkdir -p looper_slurms
mkdir -p OuputPickles
mkdir -p OutputPlots
mkdir -p VTUs
echo "Done"
echo ""

echo "Running on $nodes nodes"
echo "----------------------------------"
echo "Starting Initialisation"
echo ""
module load elmerfem


echo ""
echo "Building Mesh"

python3 Initialisation/createGeoFile.py
gmsh footprint.geo -1 -2 -o footprint.msh -v 0

ElmerGrid 14 2 footprint.msh -partition $nodes 1 1 -parttol 1 -autoclean  > /dev/null 2>&1
ElmerGrid 14 5 footprint.msh -partition $nodes 1 1 -parttol 1 -autoclean  > /dev/null 2>&1

echo "Done"
echo""

SCRIPT_FOLDER="./Initialisation"
cd "$SCRIPT_FOLDER" || { echo "Folder $SCRIPT_FOLDER not found"; exit 1; }


echo "Scaling Initial Conditions"
python3 InitialiseGeometry.py
echo "Done"
echo ""
cd ../

echo "Solving for Steady-State Strain Heating"
nohup mpirun -np $nodes ElmerSolver InitialiseVel.sif > Initialisation/ScriptOutputs/InitialVel.out 
echo "Done"
echo ""

echo "Solving for Diffusion Only Temperature Field"
nohup mpirun -np $nodes ElmerSolver InitialiseT1.sif > Initialisation/ScriptOutputs/InitialT1.out 
echo "Done"
echo ""

echo "InitialT1.out" > restart.txt
