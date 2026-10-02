### Script for reading in data from a single .pvtu or .vtu file (not a time series), extracting relavant variables at the bed, and saving them (pickle)

import pyvista as pv
import pickle
import numpy as np
import argparse

import matplotlib.pyplot as plt


# The script accepts 2 arguments: the .pvtu or .vtu file, and the filename with which to save the outputted nested dictionary of values of be variables
# e.g. python3 readvtu_basal.py './../../../../import/tethys-3g-nfs-data/woods/ElmerStreams/VTUs/ChristianFixedFine/ChristianFixedFine_t0369.pvtu' 'ChristianFineEndBed'
parser = argparse.ArgumentParser()
parser.add_argument("vtu_file", help="The .pvtu or .vtu file")
parser.add_argument("output_name", help="Filename of pickle file that will be saved")

args = parser.parse_args()

VTU_FILE = args.vtu_file
OUTPUT_NAME = args.output_name

#####################################################################################################################

# Names of variables to extract basal values of (using sif file / Paraview names)
bed_variables = {'temperature', 'melt rate', 'coldtempmask', 'temperature loads', 'water sheet thickness', 'normal vector', 'velocity', 'zb', 'groundedmask', 'friction loads', 'temperature boundary weights'}

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

######################################################################################################################

## Extract basal quantities

zb = mesh.point_data['zb']   # list of basal elevation data points

# Find indices of basal points (where z = zb)
bed_ids = []
for nid, z in enumerate(zvals):
    if z == zb[nid]:
        bed_ids.append(nid)

# Find the middle y value (so that we can take basal values along this centre line)
y_distinct = sorted(list(dict.fromkeys(yvals)))         # ordered list of distinct y values, e.g. [0.0, 500.0, 1000.0]
y_centre = y_distinct[int(np.ceil(len(y_distinct)/2))-1]  # the middle y value from the ordered list, e.g. 500.0

# Find indices of basal points that lie on the centre-line of the y plane
bed_centre_ids = []
for i in bed_ids:
    if yvals[i] == y_centre:
        bed_centre_ids.append(i)

# Put the x coordinates of the basal nodes into a dictionary (key = node id)
x_bed_dict = {nid: xvals[nid] for nid in bed_centre_ids}

# Sort the dictionaries of bed values so that they are in order of increasing x
x_bed_dict_sorted = {}
for key in sorted(x_bed_dict, key=x_bed_dict.get):      # https://www.geeksforgeeks.org/python/sort-python-dictionary-by-value/
    x_bed_dict_sorted[key] = x_bed_dict[key]

# Function for creating a dictionary of the basal values of a given variable, in order of increasing x
def extract_basal_vals(var_name): #,x_bed_dict):
    var = mesh.point_data[var_name]
    var_bed_dict = {nid: var[nid] for nid in bed_centre_ids}
    var_bed_dict_sorted = {}
    for key in x_bed_dict_sorted:
        var_bed_dict_sorted[key] = var_bed_dict[key]      # note: x and other variable dictionaries have the same keys: the node ids
    return var_bed_dict_sorted

# Create nested dictionary of dictionaries of desired bed variable values
var_vals_bed = {}
for varname in bed_variables:
    var_vals_bed[varname] = extract_basal_vals(varname)

# Add the x value dictionary to the nested dictionary
var_vals_bed['x_vals'] = x_bed_dict_sorted

# Calculate basal sliding speed (i.e. tangential to the bed) ub, basal heat flux and frictional heating
ub_dict = {}
heat_flux_dict = {}
frictional_heating_dict = {}
for nid in x_bed_dict_sorted.keys():
    normal = var_vals_bed['normal vector'][nid]
    velocity = var_vals_bed['velocity'][nid]
    weights = var_vals_bed['temperature boundary weights'][nid]
    ub_dict[nid] = np.sqrt(normal[0]**2 + normal[2]**2)*(normal[2]*velocity[0]-normal[0]*velocity[2])   # velocity dot unit tangential vector
    heat_flux_dict[nid] = -(var_vals_bed['temperature loads'][nid] - var_vals_bed['friction loads'][nid])/weights
    frictional_heating_dict[nid] = var_vals_bed['friction loads'][nid]/weights

var_vals_bed['sliding speed'] = ub_dict
var_vals_bed['heat flux'] = heat_flux_dict      # actually the jump [-k*dT/dz]+ - [-k*dT/dz]-
var_vals_bed['frictional heating'] = frictional_heating_dict

# Save the nested dictionary of bed data using pickle
filename = OUTPUT_NAME
with open(filename,'wb') as file:
    pickle.dump(var_vals_bed,file)


# Plotting test
x_bed = list(var_vals_bed['x_vals'].values())
temp_bed = list(var_vals_bed['temperature'].values())
plt.plot(x_bed,temp_bed)
#plt.plot(x_bed,melt_bed)
#plt.plot(x_bed,list(var_vals_bed['water sheet thickness'].values()))
plt.xlabel('x (m)')
plt.ylabel('T (K)')
plt.show()