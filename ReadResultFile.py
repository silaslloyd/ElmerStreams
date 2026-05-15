import numpy as np
from collections import defaultdict
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import glob
import os
import pickle 
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.animation import FuncAnimation, PillowWriter
from mpi4py import MPI
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("input_dir", help="Directory containing .result.* files")
parser.add_argument("output_dir", help="Directory to save pickle files")

args = parser.parse_args()

INPUT_DIR = args.input_dir
OUTPUT_DIR = args.output_dir
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def cantor_pair(n, m):
    #return n
    return (n + m) * (n + m + 1) // 2 + m

def nested_defaultdict():
    return defaultdict(list)

def process_file(fname, OUT_DIR):
    num = int(fname.split('.')[-1])
    print(f"Processing {fname}")

    part_data = defaultdict(nested_defaultdict)
    part_timesteps = []

    VarNames = []
    permtable = []
    current_vals = []
    currentvar = []
    Timesteps = []
    MaxTimestep = 1e10

    get_var_list = False
    get_var_vals = False
    read_perm_table = False
    skipTimestep = False

    with open(fname) as f:
        timestepcounter = 0
        if num <= 200:
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
                        
                        if np.float64(currentTime) > np.float64(MaxTimestep):
                            break           
                        

                        if timestepcounter <= 100:
                            skipTimestep = True
                            timestepcounter += 1
                           # print(timestepcounter)
                        else:
                            timestepcounter = 0
                           # print("bump")
                        get_var_vals = True
                        if currentTime not in Timesteps and skipTimestep == False:
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
                            if currentTime not in part_data[currentvar]:
                                part_data[currentvar][currentTime] = current_vals
                            else:
                                part_data[currentvar][currentTime] = np.vstack((part_data[currentvar][currentTime], current_vals))
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
    print(f"Completed Prcoessing {fname}")    
    # save result
    os.makedirs(OUT_DIR, exist_ok=True)

    out_file = os.path.join(OUT_DIR, f'saved_data_part_{num}.pkl')
    out_file_T = os.path.join(OUT_DIR, f'saved_timesteps.pkl')

    with open(out_file, 'wb') as f:
        pickle.dump(part_data, f)
    if num == 0:
    	with open(out_file_T, 'wb') as f:
            pickle.dump(Timesteps, f)

    return Timesteps

def read_partitioned_vars(result_base, data, Timesteps, restart, lasTimestep):
    if restart:
        part_data = defaultdict(nested_defaultdict)
    VarNames = []
    permtable = []
    current_vals = []
    currentvar = []
    MaxTimestep = 1e8
    result_files = sorted(glob.glob(result_base + ".*"))
    skipTimestep = False

    if not result_files:
        raise RuntimeError("No partitioned result files found")
    print(result_files)
    for fname in result_files:


        print(fname)
        num = int(fname.split('.')[-1])
        
        get_var_list = False
        get_var_vals = False
        read_perm_table = False
    
        with open(fname) as f:
            timestepcounter = 0
            if num <= 128 and num > -1:
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
                        if np.float64(currentTime) > np.float64(MaxTimestep):
                            print(MaxTimestep)
                            print("max reached, breaking")
                            break           
                        
                        if restart == False and (np.float64(currentTime) <= np.float64(lasTimestep)):
                            skipTimestep = True
                            continue
                        if timestepcounter <= 10:
                            skipTimestep = True
                            timestepcounter += 1
                           # print(timestepcounter)
                        else:
                            timestepcounter = 0
                           # print("bump")
                        get_var_vals = True
                        if currentTime not in Timesteps and skipTimestep == False:
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
                            if currentTime not in part_data[currentvar]:
                                part_data[currentvar][currentTime] = current_vals
                            else:
                                part_data[currentvar][currentTime] = np.vstack((part_data[currentvar][currentTime], current_vals))
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
    
        out_dir = "OutputPicklesRestart"
        out_data_file = os.path.join(out_dir,f'saved_data_part_{num}.pkl')

        with open(out_data_file, 'wb') as f:
            pickle.dump(part_data, f)

 
    print(VarNames) 
    return  Timesteps




# -------- PATHS -------- 
restart = True
print("READING OUTPUT FILES")
#if restart == True:
#    cont = input("THIS WILL WIPE DATA> PRESS ANY KEY TO CONTINUE")
base = os.path.normpath(INPUT_DIR)

pattern = base + ".result.*"

result_files = sorted(glob.glob(pattern))
print(result_files)
number_of_nodes = 64
#print(result_files)
for i, fname in enumerate(result_files):
   # print(i)
    if i % size != rank:
        continue

    Timesteps = process_file(fname, OUTPUT_DIR)

