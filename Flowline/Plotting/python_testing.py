## Sorting dictionaries
test_dict1 = {1: 'D', 3: 'C', 2: 'B', 4: 'E', 5: 'A'}
print(f"Original dictionary: {test_dict1}")
print(f"Sorted: {sorted(test_dict1)}")
print(f"Sorted by items: {sorted(test_dict1.items())}")
print(f"Sorted by values: {sorted(test_dict1.values())}")
print(test_dict1.get)
sorted_keys = sorted(test_dict1, key=test_dict1.get)
print(f"Keys of the dictionary entries sorted by value: {sorted_keys}")
sorted_dict_vals = {}
for key in sorted_keys:
    sorted_dict_vals[key] = test_dict1[key]
print(f"Dictionary sorted by values: {sorted_dict_vals}")


## Lists of dictionaries
print(f"Original dictionary: {test_dict1}")
print(f"list(dict) = list of keys: {list(test_dict1)}")
print(f"list(dict.values()) = list of values: {list(test_dict1.values())}")
print(f"list(dict.items()) = list of items (i.e. (key, value) pairs): {list(test_dict1.items())}")

## Derivatives of arrays
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt

# Want to differentiate y wrt x
y = np.array([0,2,4,7,9,8,7,6,5])
x = np.array([1,2,3,4,5,6,7,8,9])

# Create a spline interpolation (for different levels of smoothing)
smoothing = [0,1,2,3,4,5] 

spline = {}
for sval in smoothing:
    spline[sval] = interpolate.splrep(x, y, s=sval)      # s is the amount of smoothing

# Interpolate onto finer mesh and calculate derivative
x_fine = np.linspace(1,9,1000)
y_interp = {}
dydx = {}
for sval in smoothing:
    y_interp[sval] = interpolate.splev(x_fine, spline[sval], der=0)     # interpolated y
    dydx[sval] = interpolate.splev(x_fine, spline[sval], der=1)     # interpolated dy/dx

# Plot
plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
for sval in smoothing:
    plt.plot(x_fine, y_interp[sval], label=f"Interpolated, s = {smoothing[sval]}")
plt.plot(x, y, 'o', label="Data points")
plt.xlabel('x')
plt.ylabel('y')
plt.legend()

plt.subplot(2,1,2)
for sval in smoothing:
    plt.plot(x_fine, dydx[sval], label=f"s = {smoothing[sval]}")
plt.xlabel('x')
plt.ylabel('dydx')
plt.legend()

plt.tight_layout()
plt.show()