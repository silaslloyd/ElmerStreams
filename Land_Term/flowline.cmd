#!/bin/bash
#SBATCH --output=./slurms/flowline_slurm-%j.out
#SBATCH --job-name="Flowline"
#SBATCH --ntasks=512
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
set -e

MODE=""
NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        periodic)
            MODE="periodic"
            ;;
        symmetric)
            MODE="symmetric"
            ;;
        *)
            NAME="$1"
            ;;
    esac
    shift
done

echo "BCs: $MODE"
echo "Name: $NAME"

echo "Running on $SLURM_NTASKS partitions"
echo "----------------------------------"
echo "Starting Initialisation"

echo ""
echo "Building Result Directories"
cd Initialisation
mkdir -p ScriptOutputs
mkdir -p VTUs
echo "Done"
echo ""


module unload elmerfem/2025-09-26  
module load elmerfem/2026-07-13 
echo "Generating Noise"
python3 perlin.py # > /dev/null 2>&1

echo ""
echo "Building Mesh"
cd ..

python3 Initialisation/createGeoFile_Flowline.py

gmsh footprint.geo -1 -2 -o footprint.msh

if [[ "$MODE" == "periodic" ]]; then
	ElmerGrid 14 2 footprint.msh -partition $((SLURM_NTASKS)) 1 1 -periodic 0 1 0 -autoclean # > /dev/null 2>&1
	ElmerGrid 14 5 footprint.msh -partition $((SLURM_NTASKS)) 1 1 -periodic 0 1 0 -autoclean # > /dev/null 2>&1
elif [[ "$MODE" == "symmetric" ]]; then
	ElmerGrid 14 2 footprint.msh -metiskway $SLURM_NTASKS -autoclean # > /dev/null 2>&1
        ElmerGrid 14 5 footprint.msh -metiskway $SLURM_NTASKS -autoclean # > /dev/null 2>&1
fi

echo "Done"
echo""


SCRIPT_FOLDER="./Initialisation"
cd "$SCRIPT_FOLDER" || { echo "Folder $SCRIPT_FOLDER not found"; exit 1; }

echo "Scaling Inititial Conditions"
python3 InitialiseGeometry.py
echo "Done"
echo ""
cd ../

nohup mpirun -np $SLURM_NTASKS ElmerSolver InitialiseVel.sif > Initialisation/ScriptOutputs/InitialVel.out 
nohup mpirun -np $SLURM_NTASKS ElmerSolver InitialiseT.sif > Initialisation/ScriptOutputs/InitialT.out 
echo "Done"
echo ""
echo "Running Full Thermo_Coupled run"

if [[ "$MODE" == "periodic" ]]; then
        SIF_TEMPLATE="ThermoCoupled_Periodic_template.sif"
elif [[ "$MODE" == "symmetric" ]]; then
        SIF_TEMPLATE="ThermoCoupled_template.sif"
fi
#SIF_TEMPLATE="implicit.sif"
SIF_FILE="${NAME}.sif"
sed "s/__RUNNAME__/${NAME}/g" "${SIF_TEMPLATE}" > "${SIF_FILE}"

mkdir -p "ThermoCoupledScriptOutputs"
nohup mpirun -np $SLURM_NTASKS ElmerSolver "${SIF_FILE}" > ThermoCoupledScriptOutputs/${NAME}.out 
echo "DONE"
