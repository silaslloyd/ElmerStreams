## Script for plotting basal quantities, which have been extracted from a .vtu ot .pvtu file and pickled

import pickle
import matplotlib.pyplot as plt
import numpy as np

filename = 'ChristianFineEndBed'


with open(filename,'rb') as file:
    bed_vals = pickle.load(file)

print(bed_vals.keys())

# Function for turning the variable values from the nested dictionary into a list
def bed_vals_list(bed_vals_dict,varname):
    var_vals = list(bed_vals_dict[varname].values())
    return var_vals

x_bed = bed_vals_list(bed_vals_dict=bed_vals,varname='x_vals')
hw = bed_vals_list(bed_vals_dict=bed_vals,varname='water sheet thickness')
melt = bed_vals_list(bed_vals_dict=bed_vals,varname='melt rate')
temp_bed = bed_vals_list(bed_vals_dict=bed_vals,varname='temperature')
gm = bed_vals_list(bed_vals_dict=bed_vals,varname='groundedmask')
ctmask = bed_vals_list(bed_vals_dict=bed_vals,varname='coldtempmask')
ub = bed_vals_list(bed_vals_dict=bed_vals,varname='sliding speed')
heat_flux = bed_vals_list(bed_vals_dict=bed_vals,varname='heat flux')
friction_heat = bed_vals_list(bed_vals_dict=bed_vals,varname='frictional heating')

def grounded(var,groundedmask):
    grounded_var = [var[i] for i, gm in enumerate(groundedmask) if gm > 0]
    return grounded_var

x_grounded = grounded(x_bed, gm)

fig1, ax = plt.subplots(6,1)
ax[0].plot(grounded(x_bed,gm),grounded(temp_bed,gm))
# plt.xlabel('x (m)')
ax[0].set_xticks([])
ax[0].set_ylabel('T (K)')
# plt.show()

ax[4].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
ax[4].plot(grounded(x_bed,gm),grounded(melt,gm))
# plt.xlabel('x (m)')
ax[4].set_xticks([])
ax[4].set_ylabel('melt rate (m/yr)')

ax[2].plot(grounded(x_bed,gm),grounded(hw,gm))
# plt.xlabel('x (m)')
ax[2].set_xticks([])
ax[2].set_ylabel('hw (m)')

ax[1].plot(grounded(x_bed,gm),grounded(ctmask,gm))
# ax[1].set_xlabel('x (m)')
ax[1].set_xticks([])
ax[1].set_ylabel('CT mask')

ax[3].plot(grounded(x_bed,gm),grounded(ub,gm))
# ax[3].set_xlabel('x (m)')
ax[3].set_xticks([])
ax[3].set_ylabel('ub (m/yr)')

ax[5].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
ax[5].plot(grounded(x_bed,gm),grounded(heat_flux,gm), label='heat flux jump')
# ax[5].set_xlabel('x (m)')
ax[5].set_xticks([])
# ax[5].set_ylabel('heat flux jump')

ax[5].plot(grounded(x_bed,gm),grounded(friction_heat,gm), label='taub*ub')
ax[5].set_xlabel('x (m)')
# ax[5].set_xticks([])
# ax[5].set_ylabel('taub*ub')
ax[5].set_ylabel('Basal energy balance (?)')
ax[5].legend()


plt.show()