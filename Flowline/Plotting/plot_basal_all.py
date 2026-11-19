## Script for plotting snapshots from all times and an animation of a timeseries of .pvtu files.
# 06/11/2026

# This includes merging all the individual pickle files from the individual timesteps
# into a single dictionary that can be used when making the animation.

import numpy as np
from collections import defaultdict
import pickle
import glob
import argparse
import os
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("input_dir", help="Directory in which the pickle output files are stored.")
parser.add_argument("root_name", help="Root name of the pickle output files (without .pkl)")
parser.add_argument("output_dir", help="Directory in which to save plots.")

args = parser.parse_args()

INPUT_DIR = args.input_dir
ROOT_NAME = args.root_name
OUTPUT_DIR = args.output_dir

def nested_defaultdict():
    return defaultdict(list)

base = os.path.normpath(INPUT_DIR)
file_all_times = base + "/" + ROOT_NAME + "_all_times.pkl"

print(file_all_times)

print(os.stat(file_all_times).st_size)

with open(file_all_times,'rb') as file:
    data_all = pickle.load(file)

# Use only timesteps that contain basal coordinates. Some output files have no
# basal points, leaving every extracted variable empty for that timestep. (From Copilot).
empty_timesteps = [t for t, x_vals in data_all['x_vals'].items() if not x_vals]
Timesteps = np.array([t for t, x_vals in data_all['x_vals'].items() if x_vals])

if not len(Timesteps):
    raise ValueError(f"No timesteps with basal data found in {file_all_times}")
if empty_timesteps:
    print(f"Skipping timesteps with no basal data: {empty_timesteps}")

print(Timesteps)
print(len(Timesteps))

fignum = 1
fig = plt.figure(fignum)
# fig.clear()
num_plots = 6
ax = fig.subplots(num_plots,1, sharex=True)

# fig, ax = plt.subplots(num_plots, 1, num=fignum, sharex=True)

def plot_timestep(frame_id, data_all, Timesteps):

    # fig, ax = plt.subplots(num_plots, 1, num=fignum, sharex=True)

    for axis in ax:
        axis.clear()

    #ax.clear()

    zoomed = 0      # Set to 1 to plot zoomed in values

    # Extract time of timestep
    t = Timesteps[frame_id]

    # Load data for that timestep
    # bed_vals = data_all[:][t]
    bed_vals = {}
    for key in data_all.keys():
        bed_vals[key] = data_all[key][t]

    print(bed_vals.keys())

    # Function for turning the variable values from the nested dictionary into a list
    def bed_vals_list(bed_vals_dict,varname):
        var_vals = np.array(list(bed_vals_dict[varname].values()))
        return var_vals

    x_bed = bed_vals_list(bed_vals_dict=bed_vals, varname='x_vals')
    hw = bed_vals_list(bed_vals_dict=bed_vals, varname='water sheet thickness')
    melt = bed_vals_list(bed_vals_dict=bed_vals, varname='melt rate')
    temp_bed = bed_vals_list(bed_vals_dict=bed_vals, varname='temperature')
    gm = bed_vals_list(bed_vals_dict=bed_vals, varname='groundedmask')
    ctmask = bed_vals_list(bed_vals_dict=bed_vals, varname='coldtempmask')
    ub = bed_vals_list(bed_vals_dict=bed_vals, varname='sliding speed')
    heat_flux = bed_vals_list(bed_vals_dict=bed_vals, varname='heat flux')
    friction_heat = bed_vals_list(bed_vals_dict=bed_vals, varname='frictional heating')
    water_flux = bed_vals_list(bed_vals_dict=bed_vals, varname='water flux post')
    hydraulic_potential = bed_vals_list(bed_vals_dict=bed_vals, varname='hydraulic potential')
    hydraulic_conductivity = bed_vals_list(bed_vals_dict=bed_vals, varname='hydraulic conductivity output')

    def grounded_pure(var,groundedmask):
        grounded_var = np.array([var[i] for i, gm in enumerate(groundedmask) if gm > 0])
        return grounded_var

    def new_lims(var,x_bed,lim1,lim2):
        zoomed_var = np.array([var[i] for i, x in enumerate(x_bed) if x > lim1 and x < lim2])
        return zoomed_var

    if zoomed == 0:
        def grounded(var,groundedmask):
            return grounded_pure(var,groundedmask)

    else:
        def grounded(var,groundedmask):
            return(new_lims(grounded_pure(var,groundedmask),x_bed,x1,x2))

    def satisfies_condition(var, condition_var, condition_val):
        # Returns a list containing the values of the list var corresponding to indices for which the values of the list condition var are GREATER THAN the value condition_val
        satisfied_var = [var[i] for i, cond_var in enumerate(condition_var) if cond_var > condition_val]
        return satisfied_var

    x_temp = satisfies_condition(x_bed, ctmask, 0)      # x coordimates of temperate bed nodes
    x_first_temp = min(np.array(x_temp))                # x coordinate of first temperate bed node
    x_cold = satisfies_condition(x_bed, -np.array(ctmask), 0)
    x_last_cold = max(np.array(x_cold))


    x_grounded = grounded(x_bed, gm)

    
    #fig = plt.figure(fignum)
    #fig.clear()
    #ax = fig.subplots(6,1, sharex=True)
    #ax[0].clear
    ax[0].plot(grounded(x_bed,gm),grounded(temp_bed,gm))
    ax[0].set_xticks([])
    ax[0].set_ylabel('T (K)')
    ax[0].set_title(f"t = {t} years")

    #ax[4].clear
    ax[4].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
    ax[4].plot(grounded(x_bed,gm),grounded(melt,gm))
    ax[4].set_xticks([])
    ax[4].set_ylabel('m (m/yr)')

    #ax[2].clear
    ax[2].plot(grounded(x_bed,gm),grounded(hw,gm))
    ax[2].set_xticks([])
    ax[2].set_ylabel('hw (m)')

    #ax[1].clear
    ax[1].plot(grounded(x_bed,gm),grounded(water_flux,gm))
    ax[1].set_ylabel('q (?)')
    ax[1].set_ylim(-100,100)

    #ax[3].clear
    ax[3].plot(grounded(x_bed,gm),grounded(hydraulic_potential,gm)) #, label='...potential')
    ax[3].set_xticks([])
    ax[3].set_ylabel('Phi (?)')

    #ax[5].clear
    ax[5].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
    ax[5].plot(grounded(x_bed,gm),grounded(heat_flux,gm), label='heat flux jump')

    ax[5].plot(grounded(x_bed,gm),grounded(friction_heat,gm), label='taub*ub')
    ax[5].set_xlabel('x (m)')
    ax[5].legend()

    for i in range(0,num_plots):
        ax[i].axvline(x_first_temp,linewidth=1,color='k',linestyle='--')
        ax[i].axvline(x_last_cold,linewidth=1,color='k',linestyle='--')

    base_out = os.path.normpath(OUTPUT_DIR)
    save_name_root = base_out + "/" + ROOT_NAME
    save_name = save_name_root + "_t" + str(t).zfill(4) + ".png"

    if zoomed == 1:
        ax[5].set_xticks([x1,x2])
        save_name = save_name_root + "Zoom_t" + str(t).zfill(4) + ".png"
        plt.savefig(save_name, dpi=400)
    else:
        ax[5].set_xticks(np.array([0,1,2,3,4,5,6,7])*1e5)
        save_name = save_name_root + "_t" + str(t).zfill(4) + ".png"
        plt.savefig(save_name, dpi=400)
    
    #plt.show()


PlotTimestep = lambda x: plot_timestep(x, data_all, Timesteps)
# Make animation
anim = FuncAnimation(fig, PlotTimestep, frames = len(Timesteps), interval = 1)

# Save animation
base_out = os.path.normpath(OUTPUT_DIR)
save_name_root = base_out + "/" + ROOT_NAME
save_name = save_name_root + "_animation.gif"
print(save_name)
anim.save(save_name, writer=PillowWriter(fps=4), dpi=400)

# def time_from_filename(filename):
#     # Extract the time from the file name, ending in e.g. _t253.pvtu.
#     t_time_ext = filename.split('_')[-1]   # Splits the string into chunks dived by _ and gives the last chunk (e.g. t253.pvtu)
#     t_time = t_time_ext.split('.')[0]          # Splits the string into chunks dived by . and gives the first chunk (e.g. t253)
#     time = int(t_time[1:])                      # Gives the time (e.g. 253)
#     return time

# def nested_defaultdict():
#     return defaultdict(list)


# ## Merge all pickles files into nested dictionary
# def all_times_pickles(file_list):
#     data_all_times = defaultdict(nested_defaultdict(list))
#     # Load and collect
#     for fname in file_list:
#         t = time_from_filename(fname)
        
#         with open(fname, 'rb') as f:
#             print(f)
#             data_single = pickle.load(f)
        
#         for var in data_single.keys():
#             data_all_times[var][t] = data_single[var]

#     return data_all_times

# files = sorted(glob.glob("./OutputPickles/ChristianFixedFine_*"))

# print(files)

# data_all = all_times_pickles(files)

# print(data_all)
