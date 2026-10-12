## Script for plotting basal quantities, which have been extracted from a .vtu ot .pvtu file and pickled

import pickle
import matplotlib.pyplot as plt
import numpy as np

filenames = {'ChristianFineMidBed','ChristianFineEndBed'}

zoomed = 0      # 1 to zoom in to the x limits specified below, 0 to plot entire grounded region
x1 = 5e5    # left x lim
x2 = 5.4e5  # right x lim

fignum = 0
for filename in filenames:
    fignum = fignum + 1

    with open(filename,'rb') as file:
        bed_vals = pickle.load(file)

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

    
    fig = plt.figure(fignum)
    fig.clear()
    ax = fig.subplots(6,1, sharex=True)
    ax[0].plot(grounded(x_bed,gm),grounded(temp_bed,gm))
    # plt.xlabel('x (m)')
    ax[0].set_xticks([])
    ax[0].set_ylabel('T (K)')
    # plt.show()

    ax[4].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
    ax[4].plot(grounded(x_bed,gm),grounded(melt,gm))
    # plt.xlabel('x (m)')
    ax[4].set_xticks([])
    ax[4].set_ylabel('m (m/yr)')

    ax[2].plot(grounded(x_bed,gm),grounded(hw,gm))
    # plt.xlabel('x (m)')
    ax[2].set_xticks([])
    ax[2].set_ylabel('hw (m)')

    # ax[1].plot(grounded(x_bed,gm),grounded(ctmask,gm))
    # # ax[1].set_xlabel('x (m)')
    # ax[1].set_xticks([])
    # ax[1].set_ylabel('CT mask')

    ax[1].plot(grounded(x_bed,gm),grounded(water_flux,gm))
    # ax[1].set_xlabel('x (m)')
    # ax[1].set_xticks([])
    ax[1].set_ylabel('q (?)')
    #x[1].set_ylim([-0.1,0.1])

    ax[3].plot(grounded(x_bed,gm),grounded(hydraulic_potential,gm)) #, label='...potential')
    #ax[3].plot(grounded(x_bed,gm),grounded(hydraulic_conductivity,gm), label='...conductivity')
    # ax[3].set_xlabel('x (m)')
    ax[3].set_xticks([])
    ax[3].set_ylabel('Phi (?)')
    # ax[3].legend()

    # ax[3].plot(grounded(x_bed,gm),grounded(ub,gm))
    # # ax[3].set_xlabel('x (m)')
    # ax[3].set_xticks([])
    # ax[3].set_ylabel('ub (m/yr)')

    ax[5].plot(grounded(x_bed,gm), np.zeros(len(grounded(x_bed,gm))), 'k-', label=None)
    ax[5].plot(grounded(x_bed,gm),grounded(heat_flux,gm), label='heat flux jump')
    # ax[5].set_xlabel('x (m)')
    # ax[5].set_xticks([])
    # ax[5].set_ylabel('heat flux jump')

    ax[5].plot(grounded(x_bed,gm),grounded(friction_heat,gm), label='taub*ub')
    ax[5].set_xlabel('x (m)')
    # ax[5].set_ylabel('taub*ub')
    # ax[5].set_ylabel('Basal energy balance (?)')
    ax[5].legend()

    for i in range(0,6):
        ax[i].axvline(x_first_temp,linewidth=1,color='k',linestyle='--')
        ax[i].axvline(x_last_cold,linewidth=1,color='k',linestyle='--')

    if zoomed == 1:
        # ax[5].set_xlim([5e5,5.4e5])
        # ax[5].relim()
        # ax[5].autoscale()
        # plt.draw()
        ax[5].set_xticks([x1,x2])
        plt.savefig(filename+'Zoom.png', dpi=400)
    else:
        ax[5].set_xticks(np.array([0,1,2,3,4,5,6,7])*1e5)
        plt.savefig(filename+'.png', dpi=400)
    
    plt.show()