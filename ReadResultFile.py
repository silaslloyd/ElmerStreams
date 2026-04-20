import numpy as np
from collections import defaultdict
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import glob
import os
import pickle 
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.animation import FuncAnimation, PillowWriter

def cantor_pair(n, m):
    #return n
    return (n + m) * (n + m + 1) // 2 + m

def nested_defaultdict():
    return defaultdict(list)

def read_partitioned_vars(result_base, data, restart):
    if restart:
        data = defaultdict(nested_defaultdict)
    VarNames = []
    Timesteps = []
    permtable = []
    current_vals = []
    currentvar = []
    result_files = sorted(glob.glob(result_base + ".*"))
    skipTimestep = False

    if not result_files:
        raise RuntimeError("No partitioned result files found")

    for fname in result_files:
        #
        #if fname != "./footprint/InitialT2LOWRES16.result.7":
        #    continue

        print(fname)
        num = int(fname.split('.')[-1])
        if num > number_of_nodes:
            continue
        get_var_list = False
        get_var_vals = False
        read_perm_table = False
    
        with open(fname) as f:
            timestepcounter = 0
            for line in f:

                if line.strip() == "Degrees of freedom:":
                    get_var_list = True
                    continue
                if line.split()[0] == "Total":
                    get_var_list = False
                if get_var_list == True:
                    parts = line.split()
                    VarString = ' '.join(parts[:parts.index(':')])
                    if VarString not in VarNames:
                        VarNames.append(VarString)

                if line.split()[0] == "Time:":
                    skipTimestep = False
                    currentTime = line.split()[3]
            
                    
                    if restart == False and currentTime in Timesteps:
                        skipTimestep = True
                        continue
                    if timestepcounter <= 500:
                        skipTimestep = True
                        timestepcounter += 1
                    else:
                        timestepcounter = 0
                    get_var_vals = True
                    if currentTime not in Timesteps:
                        Timesteps.append(currentTime)                 
                    continue

                if skipTimestep == True:
                    continue

                if get_var_vals == True and skipTimestep == False:

                    if line.strip() in VarNames and line.strip() != currentvar and currentvar in VarNames:
                        #print(currentvar)
                        #print("PERMTABLE")

                        idx = np.int16(np.array(permtable)[:,1])-1

                        #print("IDX")
                        #print(idx)
                        #current_vals = np.array(current_vals)[idx]
                        
                       # if currentvar == "nodalcoords 1":
                       #     print(np.shape(current_vals))
                        
                        nodeids = cantor_pair(np.array(permtable, dtype=int)[:,0],num)
                        #print(currentvar)
                        current_vals = np.column_stack((nodeids, current_vals))

                       # if currentvar == "nodalcoords 1":
                       #     print("CurrentValsNodes")
                       #     print(np.shape(current_vals))

                       #     print(np.shape(data[currentvar][currentTime]))
                        #print(data[currentvar])
                        if currentTime not in data[currentvar]:
                            data[currentvar][currentTime] = current_vals
                        else:
                            data[currentvar][currentTime] = np.vstack((data[currentvar][currentTime], current_vals))
                        if currentvar == "temperature":
                            np.set_printoptions(threshold=np.inf)
                            #print(len(data["temperature"][currentTime]))
                            #print(data["temperature"][currentTime])

                       # if currentvar == "nodalcoords 1":
                       #     print(np.shape(data[currentvar][currentTime]))

                        current_vals = []
                        currentvar = line.strip()
                    
                    if line.strip() in VarNames and currentvar not in VarNames:
                        currentvar = line.strip()
                        continue
                    #print(line.split()[0])
                    #plt.pause(1)
                    if line.split()[0] == "Perm:" and line.split()[1] != "use": 
                        #print(line.split())
                        #plt.pause(1000)    
                        permtable = []   
                        read_perm_table = True
                        continue
                    if len(line.split()) == 1 and line.strip() not in VarNames:
                        read_perm_table = False
                        current_vals.append(np.float64(line.split()[0]))

                    if read_perm_table == True:        
                        permtable.append([line.split()[0], line.split()[1]])
            
    print(VarNames) 
    return data, Timesteps




# -------- PATHS -------- 
plt.ion()
WRITE = False
restart = False
print("starting")
#if restart == True:
#    cont = input("THIS WILL WIPE DATA> PRESS ANY KEY TO CONTINUE")
RESULT_BASE   ="./footprint/InitialT2FULL64RESTART.result"

fig = plt.figure()
ax2 = fig.add_subplot(212) #, projection='2d'
ax = fig.add_subplot(211) #, projection='2d'


if restart == False:
        #LOWRES4
    with open('/import/ontap-m-glaciology/Lloyd/Flowline/FlowlineGITtest/saved_data_FULLTEST64.pkl', 'rb') as f:
        data = pickle.load(f)

    with open('/import/ontap-m-glaciology/Lloyd/Flowline/FlowlineGITtest/saved_timesteps_FULLTEST64.pkl', 'rb') as f:
        Timesteps = pickle.load(f)

   #with open('/import/ontap-m-glaciology/Lloyd/Flowline/FlowlineGITtest/saved_data_restart.pkl', 'rb') as f:
   #     data2 = pickle.load(f)

    #with open('/import/ontap-m-glaciology/Lloyd/Flowline/FlowlineGITtest/saved_timesteps_restart.pkl', 'rb') as f:
    #    Timesteps2 = pickle.load(f)


#    t1 = np.array(Timesteps1, dtype=float)
#    t2 = np.array(Timesteps2, dtype=float)

#    t2 = t2[2:len(t2)]
#     dt = t2[1] - t2[0]   # timestep spacing
#     offset = t1[-1] + dt
#     t2_shifted = t2 + offset


#     Timesteps_all = list(t1) + list(t2_shifted)

#     data_all = {}



#     for var in data1:
#         data_all[var] = {}

#         # dataset 1 (unchanged)
#         for T in Timesteps1:
#             data_all[var][float(T)] = data1[var][T]

#         # dataset 2 (shifted time)
#         for old_T, new_T in zip(Timesteps2, t2_shifted):
#             data_all[var][new_T] = data2[var][old_T]


#     Timesteps = Timesteps_all
#     data = data_all

# else:

if restart == True:
    data = []


if WRITE == True:
    number_of_nodes = 64
    data, Timesteps = read_partitioned_vars(RESULT_BASE, data, restart)
    with open('saved_data_FULLTEST64RESTART.pkl', 'wb') as f:
        pickle.dump(data, f)
    with open('saved_timesteps_FULLTEST64RESTART.pkl', 'wb') as f:
        pickle.dump(Timesteps, f)


def basis_i(x,x_arr,i):
    if i > (len(x_arr) -2) or i < 1:
        return 0
    if x < x_arr[i-1]:
        return 0
    elif x > x_arr[i+1]:
        return 0
    elif x < x_arr[i+1] and x > x_arr[i]:
        return (x_arr[i+1] - x)/(x_arr[i+1] - x_arr[i])
    else:
        return (x - x_arr[i-1])/(x_arr[i] - x_arr[i-1])

def Dbasis_iDx(x,x_arr,i):    
    if i > (len(x_arr) -2) or i < 1:
        return 0

    if x < x_arr[i-1]:
        return 0
    elif x > x_arr[i+1]:
        return 0
    elif x < x_arr[i+1] and x > x_arr[i]:
        return -1/(x_arr[i+1] - x_arr[i])
    else:
        return 1/(x_arr[i] - x_arr[i-1])

def update(frame_idx):
    T = Timesteps[frame_idx]
    if frame_idx > 0:
        dT = np.float64(Timesteps[frame_idx]) - np.float64(Timesteps[frame_idx-1])
    else:
        dT = T
    print(T)
    # --- Build coordinate lookups ---
    xs = np.float64(data["nodalcoords 1"][T])
    ys = np.float64(data["nodalcoords 2"][T])
    zs = np.float64(data["nodalcoords 3"][T])

    x_lookup = {nid: x for nid, x in xs}
    y_lookup = {nid: y for nid, y in ys}
    z_lookup = {nid: z for nid, z in zs}

    # --- Variables you want ---
    variables = ["water sheet thickness", "melt rate", "hydraulic conductivity output", "effective pressure output", "stress 3", "zb", "coldtempmask", "bedrock", "zs", "groundedmask"]

    var_lookups = {}
    for varname in variables:
        var = np.float64(data[varname][T])
        var_lookups[varname] = {nid: v for nid, v in var}

    # --- Find common nodes ONCE ---
    common_nodes = set(x_lookup) & set(y_lookup) & set(z_lookup)
    #for v in var_lookups.values():
    #    common_nodes &= set(v)
    common_nodes_bed = common_nodes & set(var_lookups["zb"])
    common_nodes_surf = sorted(common_nodes & set(var_lookups["zs"]))
    common_nodes_bed_0 = sorted(n for n in common_nodes_bed if y_lookup[n] < 100)
    common_nodes_surf_0 = sorted(n for n in common_nodes_surf if y_lookup[n] < 100)
    common_nodes_bed_1 = sorted(n for n in common_nodes_bed if y_lookup[n] > 10)
    common_nodes_surf_1 = sorted(n for n in common_nodes_surf if y_lookup[n] > 10)
    
    # --- Build arrays ---
    x = np.array([x_lookup[n] for n in common_nodes_bed_0])
    x_surf = np.array([x_lookup[n] for n in common_nodes_surf_0])

    x2 = np.array([x_lookup[n] for n in common_nodes_bed_1])
    x_surf2 = np.array([x_lookup[n] for n in common_nodes_surf_1])

    var_arrays = {}
    var_arrays2 = {}

    for varname in variables:
        if varname != "zs":
            var_arrays[varname] = np.array([var_lookups[varname][n] for n in common_nodes_bed_0])
        else:
            var_arrays[varname] = np.array([var_lookups[varname][n] for n in common_nodes_surf_0])
    
    for varname in variables:
        if varname != "zs":
            var_arrays2[varname] = np.array([var_lookups[varname][n] for n in common_nodes_bed_1])
        else:
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
        if varname != "zs":
            var_arrays[varname] = var_arrays[varname][idx]
        else:
            var_arrays[varname] = var_arrays[varname][idx_surf]

    
    for varname in variables:
        if varname != "zs":
            var_arrays2[varname] = var_arrays2[varname][idx2]
        else:
            var_arrays2[varname] = var_arrays2[varname][idx_surf2]

    
    # --- Now plot however you like ---
    ax.clear()
    ax2.clear()

    h = var_arrays["water sheet thickness"]
    h2 = var_arrays2["water sheet thickness"]

    melt = var_arrays["melt rate"]
    global int_h
    global int_q
    if frame_idx == 0:
        int_h = melt*0
    else:
        int_h = int_h*0
        #int_h += melt*dT

    m = var_arrays["melt rate"]*10
    ct = var_arrays["coldtempmask"]
    ct2 = var_arrays2["coldtempmask"]

    gm = var_arrays["groundedmask"]

    zb = var_arrays["zb"]
    zs = var_arrays["zs"]
    bed = var_arrays["bedrock"]

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

    if frame_idx == 0:
        int_q = melt*0
    else:
        #int_q += -gradflux*dT
        int_q = int_q*0
    #hydrocond =  var_arrays["hydraulic conductivity output"][indices]
    #print(cond)
    #flux = -hydrocond*grad_phi
    #print(h)
    # Example combinations:
    ax2.plot(x, h*30,  label="adjusted hw", color = "blue", alpha = 0.5)
   # ax2.plot(x, h*30,  label="hw [0.1 m]", color = "blue", alpha = 0.5)

    #ax.plot(x, (ct+1)/2*0.1*(1+phi0)**(-1) *100, color = "black")

    ax2.plot(x, melt*1000,  label="adjusted melt", color = "purple")
    ax2.plot(x, ct*4,  label="adjusgted CT mask:", color = "green", linestyle = '--')

    #ax.plot(x_surf, zs/100,  label="hw [0.1 m]", color = "cyan")

    #ax.plot(x, bed*0 +int_h*1000,  label="hw [0.1 m]", color = "red")

    #ax.plot(x, cavity*10+1, label="cavity height")

    #ax.scatter(x, h, s = 5)
    #ax.plot(x, m*100, label="Melt rate [m/(100yr)]")
    #ax.plot(x, phi/20, label="Phi/20 [MPa]")
    #ax.plot(x, phi0/20, label="Overburden/20 [MPa]")
    #ax.plot(x, N/20, label="N/20 [MPa]")

    #ax.plot(x, cond, label="k ")
    #ax.plot(x, N/100, label="effective Pressure Output")
    #ax.plot(x, N2/100, label="New effective Pressure")

    #ax.plot(x, phi/100, label="phi/100")
    #ax2.plot(x_midpoint, flux/10, label="water flux", color = "red")
    #ax2.scatter(x_midpoint, flux/100, label="water flux", color = "red")
    #ax2.plot(x_full, flux_full/100, label="water flux", color = "red")
    #ax2.plot(x_full, h_full*30, label="water flux", color = "blue")

    #ax.plot(x, ct*400, label="N/1000")
    ax.plot(x, bed +h*500,  label="hw [0.1 m]", color = "blue")

    # Example derived quantity:
    #ax.plot(x, phi/0.0098420787, linestyle = "--")
    #ax.plot(x, N/0.0098420787)
    ax.plot(x,zb, color = "cyan")
    ax.plot(x_surf, zs, color = "cyan")
    #ax.plot(x,bed, color = "black")
    #ax.plot(x,(h*1000 - int_h*1000)*(ct>0)*(gm>0))



    ax.fill_between(x, -1000, bed +500*h, color='grey', alpha=0.5)
    ax.fill_between(x, bed +500*h, bed, color='blue', alpha=0.7)
    ax.fill_between(x, bed, zb, color='blue', alpha=0.7)
    ax.fill_between(x_surf, zs,10000, color='deepskyblue', alpha=1)

    ax.set_xlim(0,4.5e6)
    ax2.set_xlim(2e6,2.7e6)

    #
    print(len(x))
    ax.set_ylim(-1000, 3500)
    ax2.set_ylim(-0.5, 2)

    for x_ind in range(1,len(x)-1):
        if (x[x_ind] == x[x_ind - 1] or x[x_ind] == x[x_ind + 1]) and x[x_ind] < 3.5*10**6:
            ax2.axvline(x[x_ind], linestyle = "--", alpha = 0.4)
    #for x_ind in range(1,len(x)-1):
    #    ax2.axvline(x[x_ind], linestyle = "--", alpha = 0.2)
    #ax2.axhline(0,linestyle = "--", alpha = 0.4)
    ax.set_title(f"Time = {(T)} years")
    #ax.legend(loc='upper right')
    #plt.show()

Timesteps = Timesteps[0:420]
Timesteps = Timesteps[::1]
print(Timesteps)

anim = FuncAnimation(fig, update, frames=len(Timesteps), interval=100)

anim.save("animation_no_parts_zoom.gif", writer=PillowWriter(fps=25), dpi=400)
#plt.show()