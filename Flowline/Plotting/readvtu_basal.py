### Script for reading in data from a single .pvtu or .vtu file (not a time series), extracting relavant variables at the bed, and saving them (pickle)

import pyvista as pv
import pickle
import numpy as np
import argparse
from scipy import interpolate
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
bed_variables = {'temperature', 'melt rate', 'coldtempmask', 'temperature loads', 'water sheet thickness', 'normal vector', 
                 'velocity', 'zb', 'groundedmask', 'friction loads', 'temperature boundary weights', 'stress 3', 
                 'effective pressure output', 'hydraulic conductivity output'}

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
    var_bed_dict = {nid: np.array(var[nid]) for nid in bed_centre_ids}
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
hydraulic_potential_dict = {}
yearindays = 365.25
yearinsec = yearindays*24*60*60
MPainPa = 1.0e6
rhow = (1003.27/MPainPa)/(yearinsec**2)   # water density (kg m^-3 = Pa m^2 s^2 --> MPa^ m^2 yr^2)
gravity = 9.81*yearinsec**2           # acceleration due to gravity (m s^-2 --> m yr^-1)
for nid in x_bed_dict_sorted.keys():
    normal = var_vals_bed['normal vector'][nid]
    velocity = var_vals_bed['velocity'][nid]
    weights = var_vals_bed['temperature boundary weights'][nid]
    ub_dict[nid] = np.sqrt(normal[0]**2 + normal[2]**2)*(normal[2]*velocity[0]-normal[0]*velocity[2])   # velocity dot unit tangential vector
    heat_flux_dict[nid] = -(var_vals_bed['temperature loads'][nid] - var_vals_bed['friction loads'][nid])/weights
    frictional_heating_dict[nid] = var_vals_bed['friction loads'][nid]/weights
    hydraulic_potential_dict[nid] = -var_vals_bed['stress 3'][nid] - var_vals_bed['effective pressure output'][nid] + rhow*gravity*var_vals_bed['zb'][nid]

var_vals_bed['sliding speed'] = ub_dict
var_vals_bed['heat flux'] = heat_flux_dict      # actually the jump [-k*dT/dz]+ - [-k*dT/dz]-
var_vals_bed['frictional heating'] = frictional_heating_dict
var_vals_bed['hydraulic potential'] = hydraulic_potential_dict

# Calculate the water flux
# (This needs to be done in parts, due to the discontinuity at the cold-temp boundary)

water_flux_post_dict = {}
nids = list(x_bed_dict_sorted.keys())       # keep track of the node indices so we can construct a dictionary of water flux
hydraulic_potential_list = np.array(list(hydraulic_potential_dict.values()))
x_list = np.array(list(x_bed_dict_sorted.values()))
ids = np.int16(np.linspace(0,len(nids)-1,len(nids)))

print(f"x_list = {x_list}")
print(f"hydraulic_potential_list = {hydraulic_potential_list}")
print(f"x_list length = {len(x_list)}")
print(f"hydraulic_potential_list length = {len(hydraulic_potential_list)}")

def satisfies_condition(var, condition_var, condition_val):
    # Returns a list containing the values of the list var corresponding to indices for which the values of the list condition var are GREATER THAN the value condition_val
    satisfied_var = [var[i] for i, cond_var in enumerate(condition_var) if cond_var > condition_val]
    return satisfied_var

# Create lists of the variables needed to calculate the hydraulic potential gradient in wet and dry regions separately
# (Because the hydraulic potential is discontinuous at the dry/wet boundary)

# hw = list(var_vals_bed['water sheet thickness'].values())
# hw_tol = 1e-3      # tolerance for deciding a region is dry/wet
# ids_wet = satisfies_condition(ids, hw, hw_tol)      # indices of wet regions

ctmask = list(var_vals_bed['coldtempmask'].values())
ctmask_tol = 0
ids_wet = satisfies_condition(ids, ctmask, ctmask_tol)

ids_dry = [i for i in ids if i not in ids_wet]      # indices of dry regions

# nids_wet = satisfies_condition(nids, hw, hw_tol)
# hydraulic_potential_wet = satisfies_condition(hydraulic_potential_list, hw, hw_tol)
# x_wet = satisfies_condition(x_list, hw, hw_tol)

nids_wet = [nids[i] for i in ids_wet]
hydraulic_potential_wet = [hydraulic_potential_list[i] for i in ids_wet]
x_wet = [x_list[i] for i in ids_wet]

nids_dry = [nids[i] for i in ids_dry]
hydraulic_potential_dry = [hydraulic_potential_list[i] for i in ids_dry]
x_dry = [x_list[i] for i in ids_dry]

print(f"ids_wet = {ids_wet}")
print()
print(f"ids_dry = {ids_dry}")
print()
print(f"Last dry hp = {hydraulic_potential_list[ids_dry[-1]]}")
print()
print(f"First wet hp = {hydraulic_potential_list[ids_wet[0]]}")
print()
print(f"hydraulic_potential_dry = {hydraulic_potential_dry}")
print()
print(f"hydraulic_potential_wet = {hydraulic_potential_wet}")
print()

# Function that calculates the derivative of y with respect to x (using spline interpolation)
def interpolate_derivative(y,x):
    y_spline = interpolate.splrep(x, y, s=1)                        # spline interpolation of y
    #x_fine = np.linspace(x[0],x[-1],len(x)*5)                       # finer mesh to calculate derivative on
    #dydx_fine = interpolate.splev(x_fine, y_spline, der=1)          # first derivative on fine mesh
    #dydx_fine_spline = interpolate.splrep(x_fine, dydx_fine, s=0)   # spline interpolation of first derivative
    #dydx = interpolate.splev(x, dydx_fine_spline, der=0)       # dydx at original x values
    dydx = interpolate.splev(x, y_spline, der=1)       # dydx at original x values
    return dydx

#print(f"x_wet = {x_wet}")
#print(f"x_dry = {x_dry}")

# x = np.array(x_wet)
# y = np.array(hydraulic_potential_wet)
# y_spline = interpolate.splrep(x, y, s=1)                        # spline interpolation of y
# x_fine = np.linspace(x[0],x[-1],len(x)*5)                       # finer mesh to calculate derivative on
# dydx_fine = interpolate.splev(x_fine, y_spline, der=1)          # first derivative on fine mesh
# dydx_fine_spline = interpolate.splrep(x_fine, dydx_fine, s=0)   # spline interpolation of first derivative
# dydx = interpolate.splev(x_list, dydx_fine_spline, der=0)       # dydx at original x values
# hp_derivative_wet = dydx

print(f"len(x_wet) = {len(x_wet)}")
print()
# print(f"len(hydraulic_potential_wet) = {len(hydraulic_potential_wet)}")
# print()
# print(f"y_spline = {y_spline}")
# print()
# print(f"x_fine = {x_fine}")
# print()
# print(f"dydx_fine = {dydx_fine}")
# print()

hp_derivative_wet = interpolate_derivative(hydraulic_potential_wet, x_wet)
hp_derivative_dry = interpolate_derivative(hydraulic_potential_dry, x_dry)

hp_derivative_wet_dict = {}
hp_derivative_dry_dict = {}

for i in range(0,len(ids_wet)):      # water flux = - kappa * dq/dx   !!! SHOULD THIS HAVE A dq/dz TERM TOO!
    hp_derivative_wet_dict[nids_wet[i]] = hp_derivative_wet[i]
    # water_flux_post_dict[nids_wet[i]] = -var_vals_bed['hydraulic conductivity output'][nids_wet[i]]*hp_derivative_wet[i]
    # hp_derivative_dict[nids_wet[i]] = hp_derivative_wet[i]

for i in range(0,len(ids_dry)):      # water flux = - kappa * dq/dx   !!! SHOULD THIS HAVE A dq/dz TERM TOO!
    hp_derivative_dry_dict[nids_dry[i]] = hp_derivative_dry[i]
    # water_flux_post_dict[nids_dry[i]] = -var_vals_bed['hydraulic conductivity output'][nids_dry[i]]*hp_derivative_dry[i]
    # hp_derivative_dict[nids_dry[i]] = hp_derivative_dry[i]

hp_derivative_dict = hp_derivative_dry_dict | hp_derivative_wet_dict        # combine the two dictionaries

for nid in x_bed_dict_sorted.keys():
    water_flux_post_dict[nid] = -var_vals_bed['hydraulic conductivity output'][nid]*hp_derivative_dict[nid]

var_vals_bed['water flux post'] = water_flux_post_dict

print(f"len(hp_derivative_wet) = {len(hp_derivative_wet)}")
print()
print(f"len(hp_derivative_dry) = {len(hp_derivative_dry)}")
print()
print(f"hp_derivative_wet = {hp_derivative_wet}")
print()
print(f"hp_derivative_dry = {hp_derivative_dry}")
print()
print(f"len(water flux) = {len(list(water_flux_post_dict.values()))}")
print()
print(f"len(x_list) = {len(x_list)}")

# Save the nested dictionary of bed data using pickle
filename = OUTPUT_NAME
with open(filename,'wb') as file:
    pickle.dump(var_vals_bed,file)


# Plotting test
x_bed = list(var_vals_bed['x_vals'].values())
temp_bed = list(var_vals_bed['temperature'].values())
# plt.plot(x_bed,temp_bed)
plt.plot(x_bed,hydraulic_potential_list,'x')
#plt.plot(x_bed,melt_bed)
#plt.plot(x_bed,list(var_vals_bed['water sheet thickness'].values()))
plt.xlabel('x (m)')
# plt.ylabel('T (K)')
plt.ylabel('hydraulic potential (?)')
plt.show()


plt.figure(figsize=(12,12))

plt.subplot(4,1,1)
plt.plot(x_wet, hydraulic_potential_wet, label="Wet")
plt.plot(x_dry, hydraulic_potential_dry, label="Dry")
plt.xlabel('x')
plt.ylabel('hydraulic potential')
plt.legend()

plt.subplot(4,1,2)
plt.plot(x_wet, hp_derivative_wet, label="Wet")
plt.plot(x_dry, hp_derivative_dry, label="Dry")
plt.plot(x_list, list(hp_derivative_dict.values()),'g--', label="Comb")
plt.xlabel('x')
plt.ylabel('dPhidx')
plt.legend()

plt.subplot(4,1,3)
plt.plot(x_list, list(var_vals_bed['hydraulic conductivity output'].values()))
plt.xlabel('x')
plt.ylabel('hydraulic conductivity')

plt.subplot(4,1,4)
plt.plot(x_list, list(water_flux_post_dict.values()))
plt.xlabel('x')
plt.ylabel('q')
#plt.legend()

plt.tight_layout()
plt.show()