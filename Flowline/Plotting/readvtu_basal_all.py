### Script for reading in data from all .pvtu files (representing a times series) in a folder, extracting relavant variables at the bed, and saving them (pickle)

import pyvista as pv
import pickle
import numpy as np
import argparse
from scipy import interpolate
import matplotlib.pyplot as plt
import os
import glob
from collections import defaultdict


# The script accepts 3 arguments, described in the parser below.
# e.g. python3 readvtu_basal_all.py './../../../../import/tethys-3g-nfs-data/woods/ElmerStreams/VTUs/ChristianFixedFine/' 'ChristianFixedFine' 'OutputPickles'
parser = argparse.ArgumentParser()
parser.add_argument("input_dir", help="Directory in which the .pvtu files are stored. Include ending /")
parser.add_argument("root_name", help="Root name of the .pvtu files (without _t___.pvtu)")
parser.add_argument("output_dir", help="Directory in which to save pickle files. Include ending /")

args = parser.parse_args()

INPUT_DIR = args.input_dir
ROOT_NAME = args.root_name
OUTPUT_DIR = args.output_dir

base = os.path.normpath(INPUT_DIR)
name_pattern = base + "/" + ROOT_NAME + "*.pvtu"
print(name_pattern)
pvtu_files = sorted(glob.glob(name_pattern))        # list of pvtu files, at all times

print(pvtu_files)

def time_from_filename(vtu_filename):
    # Extract the time from the pvtu file name, ending in e.g. _t253.pvtu.
    t_time_pvtu = vtu_filename.split('_')[-1]   # Splits the string into chunks dived by _ and gives the last chunk (e.g. t253.pvtu)
    t_time = t_time_pvtu.split('.')[0]          # Splits the string into chunks dived by . and gives the first chunk (e.g. t253)
    time = int(t_time[1:])                      # Gives the time (e.g. 253)
    return time


def read_one_file(vtu_filename,root_name,output_dir):
    #####################################################################################################################

    # Names of variables to extract basal values of (using sif file / Paraview names)
    bed_variables = {'temperature', 'melt rate', 'coldtempmask', 'temperature loads', 'water sheet thickness', 'normal vector', 
                    'velocity', 'zb', 'groundedmask', 'friction loads', 'temperature boundary weights', 'stress 3', 
                    'effective pressure output', 'hydraulic conductivity output'}

    #####################################################################################################################

    ## Extract data from .vtu or .pvtu file

    VTU_FILE = vtu_filename

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

    # print(f"x_list = {x_list}")
    #print(f"hydraulic_potential_list = {hydraulic_potential_list}")
    # print(f"x_list length = {len(x_list)}")
    # print(f"hydraulic_potential_list length = {len(hydraulic_potential_list)}")

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

    # Function that calculates the derivative of y with respect to x (using spline interpolation)
    def interpolate_derivative(y,x):
        y_spline = interpolate.splrep(x, y, s=1)                        # spline interpolation of y
        dydx = interpolate.splev(x, y_spline, der=1)       # dydx at original x values
        return dydx


    # print(f"len(x_wet) = {len(x_wet)}")
    # print()

    if len(x_wet) > 0:
        hp_derivative_wet = interpolate_derivative(hydraulic_potential_wet, x_wet)
    else:
        hp_derivative_wet = []

    if len(x_dry) > 0:
        hp_derivative_dry = interpolate_derivative(hydraulic_potential_dry, x_dry)
    else:
        hp_derivative_dry = []

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

    # Save the nested dictionary of bed data using pickle
    t = time_from_filename(vtu_filename)    # extract time from pvtu filename
    # base_out = os.path.normpath(output_dir)
    # filename = base_out + "/" + root_name + "_t" + str(t).zfill(4) + ".pkl"
    # with open(filename,'wb') as file:
    #     pickle.dump(var_vals_bed,file)

    return t, var_vals_bed


# Create a nested dictionary in which to store the data dictionaries for each timestep
def nested_defaultdict():
    return defaultdict(list)
data_all_times = defaultdict(nested_defaultdict)

# Loop through all the files for different time, 
# extracting the data for each timestep and toring in the nested dictionary,
# which is then pickled and saved
for i, filename in enumerate(pvtu_files):
    print(i)
    print(filename)
    timestep, var_vals_bed = read_one_file(filename,ROOT_NAME,OUTPUT_DIR)
    print(timestep)

    for var in var_vals_bed.keys():
        data_all_times[var][timestep] = var_vals_bed[var]

    base_out = os.path.normpath(OUTPUT_DIR)
    filename = base_out + "/" + ROOT_NAME + "_all_times.pkl"

    with open(filename,'wb') as file:
        pickle.dump(data_all_times,file)