
import numpy as np
from collections import defaultdict
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import glob
import os
import pickle 
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.animation import FuncAnimation, PillowWriter
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("input_dir", help="Directory containing .result.* files")
parser.add_argument("output_dir", help="Directory to save pickle files")

args = parser.parse_args()

INPUT_DIR = args.input_dir
OUTPUT_DIR = args.output_dir

plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'

fig, ax1 = plt.subplots(subplot_kw={"projection": "3d"})

cbar = None
#ax2 = plt.twinx(ax1)

#ax2 = fig.add_subplot(212) #, projection='2d'
#ax = fig.add_subplot(211) #, projection='2d'

files = sorted(glob.glob(f"{INPUT_DIR}/saved_data_part_*.pkl"))
files2 = sorted(glob.glob(f"./OutputPickles/surge3.1/saved_data_part_*.pkl"))
def nested_defaultdict():
    return defaultdict(list)

def update(frame_idx, data, Timesteps):
    global cbar
#    ax1.cla()
 #   plt.cla()
    T = Timesteps[frame_idx]
    print(" plotting frame at time:")
    print(T)
    # --- Build coordinate lookups ---
    xs = np.float64(data["nodalcoords 1"][T])
    ys = np.float64(data["nodalcoords 2"][T])
    zs = np.float64(data["nodalcoords 3"][T])
    print(xs)

    x_lookup = {nid: x for nid, x in xs}
    y_lookup = {nid: y for nid, y in ys}
    z_lookup = {nid: z for nid, z in zs}

    # --- Variables you want ---
   # variables = ["zb residual","fwater 3", "temperature","velocity 1", "velocity 2", "velocity 3", "water sheet thickness", "melt rate", "hydraulic conductivity output", "effective pressure output", "stress 3", "zb", "coldtempmask", "bedrock", "zs", "groundedmask"]
    variables = ["zs", "zb"]
    var_lookups = {}
    for varname in variables:
        var = np.float64(data[varname][T])
        var_lookups[varname] = {nid: v for nid, v in var}

    # --- Find common nodes ONCE ---
    common_nodes = set(x_lookup) & set(y_lookup) & set(z_lookup)
    #for v in var_lookups.values():
    #    common_nodes &= set(v)
    common_nodes_bed = common_nodes & set(var_lookups["zb"])
    print(common_nodes)    
    common_nodes_surf = sorted(common_nodes & set(var_lookups["zs"]))
    print(common_nodes_bed)   
# common_nodes_bulk = common_nodes & set(var_lookups["velocity 1"])
   # common_nodes_bedrock = sorted(n for n in common_nodes_bulk)

    common_nodes_bed_0 = sorted(n for n in common_nodes_bed if y_lookup[n] < 100)
    common_nodes_surf_0 = sorted(n for n in common_nodes_surf if y_lookup[n] < 100)
    common_nodes_bed_1 = sorted(n for n in common_nodes_bed if y_lookup[n] > 10)
    common_nodes_surf_1 = sorted(n for n in common_nodes_surf if y_lookup[n] > 10)
  #  common_nodes_bulk = sorted(n for n in common_nodes_bulk if y_lookup[n] < 10)
    

    # --- Build arrays ---
    x = np.array([x_lookup[n] for n in common_nodes_bed_0])
    x_surf = np.array([x_lookup[n] for n in common_nodes_surf_0])

    print(x)
    print(x_surf)
   # x_body = np.array([x_lookup[n] for n in common_nodes_bulk])
   # z_body = np.array([z_lookup[n] for n in common_nodes_bulk])
    
   # x_bedrock = np.array([x_lookup[n] for n in common_nodes_bedrock])
   # z_bedrock = np.array([z_lookup[n] for n in common_nodes_bedrock])

    #velx_body = np.array([var_lookups["velocity 1"][n] for n in common_nodes_bulk])
    #velz_body = np.array([var_lookups["velocity 3"][n] for n in common_nodes_bulk])
    
   # temp_body = np.array([var_lookups["temperature"][n] for n in common_nodes_bed])

    # --- Sort once ---
    #idx = np.argsort(x_body)
    #x_body = x_body[idx]
    #z_body = z_body[idx]
    #velx_body = velx_body[idx]
    #velz_body = velz_body[idx]
    #vel_mag = (velx_body **2 + velz_body**2)**0.5

#    idx = np.argsort(x_bedrock)
#    x_bedrock = x_bedrock[idx]
#    z_bedrock = z_bedrock[idx]
    #temp_body = temp_body[idx]


    x2 = np.array([x_lookup[n] for n in common_nodes_bed_1])
    x_surf2 = np.array([x_lookup[n] for n in common_nodes_surf_1])

    var_arrays = {}
    var_arrays2 = {}

    for varname in variables:
        if varname != "zs" and varname != "zb residual":
            print(varname)
            var_arrays[varname] = np.array([var_lookups[varname][n] for n in common_nodes_bed_0])
        elif varname == "zs":
            var_arrays[varname] = np.array([var_lookups[varname][n] for n in common_nodes_surf_0])
    
    for varname in variables:
        if varname != "zs" and varname != "zb residual":
            var_arrays2[varname] = np.array([var_lookups[varname][n] for n in common_nodes_bed_1])
        elif varname == "zs":
            var_arrays2[varname] = np.array([var_lookups[varname][n] for n in common_nodes_surf_1])

    # --- Sort once ---
    idx = np.argsort(x)
    x = x[idx]
    idx_surf = np.argsort(x_surf)
    x_surf = x_surf[idx_surf]

    idx2 = np.argsort(x2)
    x2 = x2[idx2]
    idx_surf2 = np.argsort(x_surf2)
    x_surf2 = x_surf2[idx_surf2]

    for varname in variables:
        if varname != "zs" and varname != "zb residual":
            var_arrays[varname] = var_arrays[varname][idx]
        elif varname == "zs":
            var_arrays[varname] = var_arrays[varname][idx_surf]

    
    for varname in variables:
        if varname != "zs" and varname != "zb residual":
            var_arrays2[varname] = var_arrays2[varname][idx2]
        elif varname == "zs":
            var_arrays2[varname] = var_arrays2[varname][idx_surf2]

    
    # --- Now plot however you like ---
    #ax.clear()
    #ax2.clear()

#    h = var_arrays["water sheet thickness"]
#    h2 = var_arrays2["water sheet thickness"]

#    melt = var_arrays["melt rate"]
#    temp = var_arrays["temperature"]


 #   m = var_arrays["melt rate"]*10
 #   ct = var_arrays["coldtempmask"]
  #  ct2 = var_arrays2["coldtempmask"]

  # gm = var_arrays["groundedmask"]
    zb = var_arrays["zb"]
    zs = var_arrays["zs"]
#    bed = var_arrays["bedrock"]
    """
    Fw = var_arrays["fwater 3"]
    zbres = var_arrays["zb residual"]

    cavity = var_arrays["zb"] - var_arrays["bedrock"]
    N = var_arrays["effective pressure output"]
    cond = (var_arrays["hydraulic conductivity output"])
    PI = - var_arrays["stress 3"]
    phi0 =  PI + 0.0098420787*var_arrays["zb"]
    phi = phi0 - N
   # ax.scatter(x, phi/100, alpha = 0.5)
    grad_phi = np.diff(phi) / (np.diff(x))

    x_midpoint = (x[1:] + x[:-1])/2
    cond_midpoint = (cond[1:] + cond[:-1])/2
    ct_midpoint = ct[:-1]
    gm_midpoint = gm[:-1]


    x_full = np.linspace(2.9e6,3.5e6,10000)
    kappa_full = x_full*0
    h_full = x_full*0
    grad_phi_full = x_full*0
   # for ind1 in range(len(x_full)):
   #     for ind2 in range(len(x)):
   #         kappa_full[ind1] += cond[ind2]*basis_i(x_full[ind1],x, ind2)
   #         h_full[ind1] += h[ind2]*basis_i(x_full[ind1],x, ind2)

   #         grad_phi_full[ind1] += phi[ind2]*Dbasis_iDx(x_full[ind1],x, ind2)
    flux_full = - kappa_full*grad_phi_full
    flux = -(gm_midpoint+1)/2*(ct_midpoint+1)/2*cond_midpoint* grad_phi
    gradflux = np.diff(flux) / (np.diff(x_midpoint))
    gradflux = np.pad(gradflux, (1, 1), mode='constant', constant_values=0)




    #print(gm)
    #print(x)
    #gl_idx = np.where(gm == -1)
    #print(gl_idx)
    #print(gl_idx[0][0])
    #gl = x[gl_idx[0][0]]
    #uscale = 1923691/133021
    #uzscale = 2137/133021
    gl  = 1e10 
    z_surf_grounded = zs[np.where(x_surf < gl)]
    x_surf_grounded = x_surf[np.where(x_surf < gl)]

    x_grounded = x[np.where(x<gl)]
    T_grounded = temp[np.where(x<gl)]
    x_Temperate = x_grounded[np.where(T_grounded > 273.1)]
    vol_temperate = np.sum(np.diff(x_Temperate))
    Total_vol = np.sum(np.diff(x_grounded))
    Temp_fraction = vol_temperate/Total_vol 
    grounded_vol = np.sum(np.diff(x_surf_grounded)*z_surf_grounded[0:-1])
    # vel_contours = ax1.tricontourf(x_body[np.where(x_body < gl)], z_body[np.where(x_body < gl)], velx_body[np.where(x_body < gl)] ,cmap = "cool", vmin = 0, vmax = 150, levels = np.linspace(0,150,100))
    #ax1.tricontour(x_body[np.where(x_body < gl)]/1923691, z_body[np.where(x_body < gl)]/2137, velx_body[np.where(x_body < gl)]/uscale, levels = 50, vmin = 0, vmax = 15, colors = "white", linewidths = 0.21)
    #temp_contours = ax1.tricontourf(x_bedrock, z_bedrock, temp_body)
    global GL, Vol, TempFrac

    GL = np.concatenate((GL,[gl]))
    Vol = np.concatenate((Vol,[grounded_vol]))
    TempFrac = np.concatenate((TempFrac,[Temp_fraction]))

    ax1.scatter(gl, Temp_fraction, grounded_vol, color = "black")
    #ax1.set_xlim(1.8e6,2.6e6)
    #ax1.set_xlim(0,4.5e6)
   # ax1.fill_between(x_surf, zs, 10000, color='white', alpha=1)
   # ax1.plot(x_surf, zs, color='black', alpha=1)
   # ax1.plot(x, zb, color='black', alpha=1)
    #ax1.plot(x/1923691, (Fw+zbres)/1e6, color='blue', alpha=1)
    #ax1.plot(x/1923691, (zbres)*1e8, color='red', alpha=1)


   # ax1.fill_between(x, -1000, bed, color='grey', alpha=0.5)
   # ax1.fill_between(x[np.where(ct>0)], -1000, bed[np.where(ct>0)], color='gold', alpha=1)
   # ax1.fill_between(x[np.where((temp>272.15) &  (temp < 273.15))], -1000, bed[np.where((temp>272.15) &  (temp < 273.15))], color='orange', alpha=1)
   # ax1.fill_between(x[np.where(temp<272.15)], -1000, bed[np.where(temp<272.15)], color='lightblue', alpha=1)


    #ax1.fill_between(x/1923691, bed +500*h, bed, color='blue', alpha=0.7)
  #  ax1.set_xlim(3.8e6, 4.3e6)

   # ax1.set_ylim(-1000, 1000)

   # ax1.set_xlim(0e6, 4.5e6)

   # ax1.set_ylim(-1000, 4000)

    ax1.set_title(f"$ t = {np.int64(np.float64(T))} \\; \\mathrm{{years}}$")
    ax1.set_xlabel(f"$x \\; \\mathrm{{(m)}}$")
    ax1.set_ylabel(f"$z \\; \\mathrm{{(m)}}$")
    #ax1.set_aspect(0.5e3)
    #if cbar is not None:
    #    cbar.remove()   # ← key line
    #cbar = plt.colorbar(vel_contours, label = "$u \\; \\mathrm{{(m/yr)}}$", shrink = 0.6)
    #cbar.set_ticks(np.linspace(0,150,6))
    #ax2.set_ylabel(r"$m \quad /\mathrm{mm/yr}$")
    """   
    x, idx = np.unique(x, return_index=True)
    print(x)
    zb = zb[idx]
    x_surf, idx = np.unique(x_surf, return_index=True)
    zs = zs[idx]
       
    saved_zb =  np.column_stack((x, zb))
    saved_zs =  np.column_stack((x_surf, zs))
    print(saved_zb)
    np.savetxt('zs_new.xy', saved_zs, fmt='%g', delimiter=' ')
    np.savetxt('zb_new.xy', saved_zb, fmt='%g', delimiter=' ')

    #ax.legend(loc='upper right')
    #plt.show()
    plt.subplots_adjust(bottom=0.1)

def plot_all_parts(frame_idx, Timesteps):
    ax1.cla() 
    ax2.cla() 

    print(frame_idx)

    for f in files:
        print(f)
        with open(f, 'rb') as pf:
            data = pickle.load(pf)
            update(frame_idx, data, Timesteps)
        
def merge_pickles(file_list):
    merged = defaultdict(lambda: defaultdict(list))
    print("MERGING")
    # Load and collect
    for fname in file_list:
        ender = fname.split('_')[-1]
        print(ender)
        num = int(ender.split('.')[0])
        
        with open(fname, 'rb') as f:
            print(f)
            data = pickle.load(f)
        
        for var, timesteps in data.items():
            for t, values in timesteps.items():
                merged[var][t].append(values)
    
    # Concatenate
    for var in merged:
        print(var)
        for t in merged[var]:
            merged[var][t] = np.concatenate(merged[var][t], axis=0)
    #with open("merged_data.pkl", 'wb') as f:
    #    pickle.dump(merged, f, protocol=pickle.HIGHEST_PROTOCOL)

    return merged

with open(f'{INPUT_DIR}/saved_timesteps.pkl', 'rb') as f:
        Timesteps = pickle.load(f)
print(Timesteps)

with open(f'./OutputPickles/surge3.1/saved_timesteps.pkl', 'rb') as f2:
        Timesteps2 = pickle.load(f2)

print("files")
print(files)
merged_data = merge_pickles(files)
merged_data2 = merge_pickles(files2)
#plot_all_parts(-1,Timesteps)

Timesteps = Timesteps[::1]


global GL
global Vol
global TempFrac

GL = np.array([])
Vol = np.array([])
TempFrac = np.array([])


for i in range(len(Timesteps)):
#    print(i)
    update(i,merged_data, Timesteps)

    plt.savefig(f'{OUTPUT_DIR}PNGs/profiles_{Timesteps[i]}.png', dpi = 400)

#for j in range(len(Timesteps2)):
##    print(i)
#    update(j,merged_data2, Timesteps2)
#
#    plt.savefig(f'{OUTPUT_DIR}PNGs/profiles_{Timesteps2[j]}.png', dpi = 400)


np.savez(f"{OUTPUT_DIR}fig.npz", x=GL, y=Vol, z=TempFrac)

plot_all = lambda x: plot_all_parts(x,Timesteps)

with open(f"{INPUT_DIR}/saved_timesteps.pkl", 'rb') as f:
        Timesteps = pickle.load(f)
Timesteps = Timesteps[::1]
Update = lambda x: update(x, merged_data, Timesteps)
#anim = FuncAnimation(fig, Update, frames=len(Timesteps), interval=100)

#anim.save(f"{OUTPUT_DIR}animation.gif", writer=PillowWriter(fps=4), dpi=400)

#update(100)

#plt.show()

