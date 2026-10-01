### How to read data from .vtu files into Python (for plotting)

import pyvista as pv
import pickle
import numpy as np
import matplotlib.pyplot as plt

mesh = pv.read('./../../../../import/tethys-3g-nfs-data/woods/ElmerStreams/VTUs/ChristianFixedFine/ChristianFixedFine_t0369.pvtu')

## Mesh info
n_points = mesh.n_points        # number of mesh points
print(n_points)
points = mesh.points    # coordinates of mesh points
print(points[0:5,:])    # print coordinates of the first 5 mesh points

xvals = points[:,0]     # x coordinates
yvals = points[:,1]     # y coordinates
zvals = points[:,2]     # z coordinates

print(xvals[0:5])       # print first 5 x coordinates
print(xvals[-6:-1])     # print last 5 x coordinates
print(xvals[n_points-6:n_points-1])     # print last 5 x coordinates

## Variables data
point_data = mesh.point_data
# point_data is a dictionary containing values of all the output variables as arrays.
# The keys are the names from the sif file/Paraview.
# The values are lists of length n_points for scalars, and arrays of size n_points x 3 for vectors.

temp = mesh.point_data['temperature']   # list of temperatue data points

# The x, y, z coordinates of the mesh points can also be accessed as follows:
nodalcoords = point_data['nodalcoords']
xcoords = nodalcoords[:,0]
ycoords = nodalcoords[:,1]
zcoords = nodalcoords[:,2]

# The result is the same as the coordinate values in mesh.points
print(f"Mesh points: {points[0:5,:]}")
print(f"Nodal coordinates: {nodalcoords[0:5,:]}")

print(type(temp))
print(len(temp))

#mesh.plot()

print(mesh.point_data)

#for key in mesh.point_data:     # print all the key (i.e. varaible) names
#    print(key)

## Save the temperature into a file using pickle
filename = 'temp_pickle_test'       # name of file to save data into
with open(filename,'wb') as file:      # 'wb' = write binary. Use 'ab' = append binary when saving multiple objects
    pickle.dump(temp,file)          # save data to file

#print(temp[0])

temp[0] = 0

#print(temp[0])

# To re-load saved data into Python:
with open(filename,'rb') as file:
    temp = pickle.load(file)

#print(temp[0])


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

print(y_distinct, y_centre)

# Find indices of basal points that lie on the centre-line of the y plane
bed_centre_ids = []
for i in bed_ids:
    if yvals[i] == y_centre:
        bed_centre_ids.append(i)

# Find the value of the variables at the bed,
# and put into a dictionary with node ids as keys
temp_bed_dict = {nid: temp[nid] for nid in bed_centre_ids}
x_bed_dict = {nid: xvals[nid] for nid in bed_centre_ids}

x_bed_dict_sorted = {nid: x for nid, x in sorted(x_bed_dict.items(), key=lambda item: item[1])}
temp_bed_dict_sorted = {nid: temp_bed_dict[nid] for nid in x_bed_dict_sorted.keys}

#temp_bed = [temp[nid] for x, nid in x_bed_dict_sorted]

#https://stackoverflow.com/questions/60969987/how-can-i-save-the-original-index-after-sorting-a-list

print(x_bed_dict_sorted)

print(f"Total number of basal points: {len(bed_ids)}")
print(f"Number of basal points along centre line: {len(bed_centre_ids)}")

## Plot basal temperature
#fig, ax1 = plt.subplots()
#ax1.cla()
#plt.cla()
#ax1.plot()

plt.plot(x_bed,temp_bed)
plt.show()