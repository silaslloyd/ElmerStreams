18/11/2026
This folder contains the code for the 2D flowline setup.

To run the transient flowline simulation on tethys, use flowline.cmd as, e.g.
sbatch --ntasks=128 flowline.cmd "periodic" RUN_NAME

The number of partitions can be changed from 128,
and the boundary conditions conditions can be chosen to be either "periodic" or "symmetric".
(But, in practice, only periodic is ever used).

To test different hydrology models (sheetsolvers), use flowlineHydro.cmd as, e.g.
sbatch --ntasks=128 flowlineHydro.cmd SHEETSOLVER_TYPE RUN_NAME

where SHEETSOLVER_TYPE can be (currently) either:
- "careful" to use the latest (hopefully) correct version
- "sloppy" to use the version before Christian's fix of including dhdt contributions 
from temperate nodes in partially temperate elements was included
- "preEGU" to use the version that existed before EGU 2026

The important sif files are:
- InitialiseVel.sif:
- InitialseT.sif:
- ThermoCoupled_template.sif: the template for the full thermomechanically coupled run,
from which a sif file for each specific run is created.

Other notable files are:
- footprint.geo: for changing the mesh
- parameters.lua: for changing the parameter values (including mesh resolution)
- utils.lua: contains useful functions used in the sifs

Note that the our custom solvers live outside the Flowline folder,
in the SRC folder (e.g. the sheetsolver and coldtempmask solver).