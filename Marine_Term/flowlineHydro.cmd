#!/bin/bash
#SBATCH --output=./slurms/Flowline_slurm-%j.out
#SBATCH --job-name="FineCareful"
#SBATCH --ntasks=512
#SBATCH --time=72:00:00
#SBATCH --mail-type=all

pwd
set -e

MODE=""
NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        careful)
            MODE="careful"
            ;;
        sloppy)
            MODE="sloppy"
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
mkdir -p VTUs
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

ElmerGrid 14 2 footprint.msh -metiskway $SLURM_NTASKS -autoclean # > /dev/null 2>&1
ElmerGrid 14 5 footprint.msh -metiskway $SLURM_NTASKS -autoclean # > /dev/null 2>&1

echo "Done"
echo""


if [[ "$MODE" == "careful" ]]; then
        HYDROLOGY_SOLVER="sheetsolverhwCS.f90"
elif [[ "$MODE" == "preEGU" ]]; then
        HYDROLOGY_SOLVER="sheetsolverhwpreEGU.f90"
elif [[ "$MODE" == "sloppy" ]]; then
        HYDROLOGY_SOLVER="sheetsolverhw.f90"
fi

echo "Compile hydrology solver"
elmerf90 ./../SRC/$HYDROLOGY_SOLVER -o ./../SRC/SheetSolverhw.so
#elmerf90 ./../SRC/sheetsolverhwpreEGU.f90 -o ./../SRC/SheetSolverhw.so
echo "Done"


SCRIPT_FOLDER="./Initialisation"
cd "$SCRIPT_FOLDER" || { echo "Folder $SCRIPT_FOLDER not found"; exit 1; }

echo "Scaling Inititial Conditions"
python3 InitialiseGeometry.py
echo "Done"
echo ""
cd ../
echo "Running Initialisation run"
nohup mpirun -np $SLURM_NTASKS ElmerSolver InitialiseVel.sif > Initialisation/ScriptOutputs/InitialVel.out 
nohup mpirun -np $SLURM_NTASKS ElmerSolver InitialiseT.sif > Initialisation/ScriptOutputs/InitialT.out 
echo "Done"
echo ""
echo "Running Full Thermo_Coupled run"

SIF_TEMPLATE="ThermoCoupled_template.sif"
SIF_FILE="${NAME}.sif"
sed "s/__RUNNAME__/${NAME}/g" "${SIF_TEMPLATE}" > "${SIF_FILE}"
mkdir -p "FlowlineTCScriptOutputs"
nohup mpirun -np $SLURM_NTASKS ElmerSolver "${SIF_FILE}" > ScriptOutputs/${NAME}.out 
echo "DONE"
