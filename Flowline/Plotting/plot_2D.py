## Script for plotting quantities in the ice as colour maps, which have been extracted from a .vtu ot .pvtu file and pickled

import pickle
import matplotlib.pyplot as plt
import numpy as np


filename = 'ChristianFineEndIce'

with open(filename,'rb') as file:
    ice_vals = pickle.load(file)


# Function for turning the variable values from the nested dictionary into a list
def vals_array(vals_dict,varname):
    var_vals = np.array(list(vals_dict[varname].values()))
    return var_vals

x = vals_array(ice_vals,'x_vals')
y = vals_array(ice_vals,'y_vals')
z = vals_array(ice_vals,'z_vals')
temp = vals_array(ice_vals,'temperature')
vel = vals_array(ice_vals,'velocity')
pressure = vals_array(ice_vals,'pressure')

# Velocity components
u = np.array([vel[i][0] for i in range(len(vel))])
v = np.array([vel[i][1] for i in range(len(vel))])
w = np.array([vel[i][2] for i in range(len(vel))])

vel_mag = np.sqrt(u**2 + v**2 + w**2)       # velocity magnitude

print(x[1])
print(type(vel), len(vel))
print(vel[0][0])

# Plotting
fignum = 1
fig = plt.figure(fignum, figsize=(10,7))


vel_contours = plt.tricontourf(x, z, u ,cmap = "cool", vmin = 0, vmax = 150, levels = np.linspace(0,150,100))
#temp_contours = plt.tricontourf(x, z, temp ,cmap = "cool", vmin = min(temp), vmax = max(temp), levels = np.linspace(min(temp),max(temp),100))

cbar = plt.colorbar(vel_contours, label = "$u \\; \\mathrm{{(m/yr)}}$", shrink = 0.6)
#cbar = plt.colorbar(temp_contours, label = "$T \\; \\mathrm{{(K)}}$", shrink = 0.6)
#cbar.set_ticks(np.linspace(min(temp),max(temp),6))

#cp = plt.pcolormesh(x,y,temp,cmap='parula')

plt.show()