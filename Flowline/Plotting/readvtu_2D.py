### Script for reading in data from a single .pvtu or .vtu file (not a time series), extracting relavant variables in the ice, and saving them (pickle)

import pyvista as pv
import pickle
import numpy as np
import argparse
import matplotlib.pyplot as plt


# The script accepts 2 arguments: the .pvtu or .vtu file, and the filename with which to save the outputted nested dictionary of values of be variables
# e.g. python3 readvtu_2D.py './../../../../import/tethys-3g-nfs-data/woods/ElmerStreams/VTUs/ChristianFixedFine/ChristianFixedFine_t0369.pvtu' 'ChristianFineEndIce'
parser = argparse.ArgumentParser()
parser.add_argument("vtu_file", help="The .pvtu or .vtu file")
parser.add_argument("output_name", help="Filename of pickle file that will be saved")

args = parser.parse_args()

VTU_FILE = args.vtu_file
OUTPUT_NAME = args.output_name

#####################################################################################################################

# Names of variables to extract bulk values of (using sif file / Paraview names)
ice_variables = {'temperature', 'velocity', 'pressure', 'strain heating'}

#####################################################################################################################

## Extract data from .vtu or .pvtu file

mesh = pv.read(VTU_FILE)
point_data = mesh.point_data        # values of variables
# point_data is a dictionary containing values of all the output variables as arrays.
# The keys are the names from the sif file/Paraview.
# The values are lists of length n_points for scalars, and arrays of size n_points x 3 for vectors.

points = mesh.points    # coordinates of mesh points

xvals = points[:,0]     # x coordinates
yvals = points[:,1]     # y coordinates
zvals = points[:,2]     # z coordinates

print(yvals)

######################################################################################################################

zb = mesh.point_data['zb']   # list of basal elevation data points

# Find indices of points in the ice (where z > zb)
bulk_ids = []
for nid, z in enumerate(zvals):
    if z > zb[nid]:
        bulk_ids.append(nid)

# Find the middle y value (so that we can take basal values along this centre line)
y_distinct = sorted(list(dict.fromkeys(yvals)))         # ordered list of distinct y values, e.g. [0.0, 500.0, 1000.0]
y_centre = y_distinct[int(np.ceil(len(y_distinct)/2))-1]  # the middle y value from the ordered list, e.g. 500.0

# Find indices of basal points that lie on the centre-line of the y plane
centre_ids = []
for i in bulk_ids:
    if yvals[i] == y_centre:
        centre_ids.append(i)

print(f"ycentre = {y_centre}")
print()
#print(f"centre_ids = {centre_ids}")

# Create a nested dictionary if dictionaries of variables (key = node id, item = variable value at node)
var_vals_ice = {}
for var_name in ice_variables:
    var = mesh.point_data[var_name]         # dictionary with node indices as keys and variable values as items (lists)
    var_dict = {nid: np.array(var[nid]) for nid in centre_ids}  # turn lists into np arrays
    var_vals_ice[var_name] = var_dict

print("Here")

# Put x, y, z coordinates in dictionary too
x_dict = {nid: np.array(xvals[nid]) for nid in centre_ids}
var_vals_ice['x_vals'] = x_dict
y_dict = {nid: np.array(yvals[nid]) for nid in centre_ids}
var_vals_ice['y_vals'] = y_dict
z_dict = {nid: np.array(zvals[nid]) for nid in centre_ids}
var_vals_ice['z_vals'] = z_dict


print("Here")

# Save the nested dictionary of bed data using pickle
filename = OUTPUT_NAME
with open(filename,'wb') as file:
    pickle.dump(var_vals_ice,file)
