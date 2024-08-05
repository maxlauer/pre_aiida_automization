import pathlib as pl
import argparse
import sys
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

from lattice_relaxation import lattice_relax_postprocessing
from matplotlib.ticker import StrMethodFormatter


def plot_convergence(conv_para, values, unit, bound, out_path, converged_value = None, converged_para=None, size=None):
    if not size:
        size = (8,6)
    
    fig, ax = plt.subplots(1,1, figsize=size)
    ax.scatter(x=conv_para, y=values)

    if converged_value:
        u_bound = converged_value + bound
        l_bound = converged_value - bound
        ax.axhline(converged_value, color='grey', linestyle='--')
        ax.axhline(u_bound, color='grey', linestyle='-', alpha = 0.5)
        ax.axhline(l_bound, color='grey', linestyle='-', alpha = 0.5)
        ax.fill_between([np.min(conv_para) - 10, np.max(conv_para) + 10], l_bound, u_bound, color='grey', alpha=0.3)

        if converged_para:
            ax.scatter(x=converged_para, y=converged_value, color='purple')

    ax.set_xlim(np.min(conv_para),np.max(conv_para))
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.5f}'))

    ax.set_xlabel(f'Convergence Parameter')
    ax.set_ylabel(f'Convergence Criterion [{unit}]')

    fig.savefig(out_path)
    plt.close()


def determine_lat_convergence(path, conv_parameter, lat_threshold, en_threshold=1e-6, comparisons = 2):
    energy_conv = []
    convergence_path = path / 'convergence.csv'
    if not convergence_path.exists():
        for conv_path in path.iterdir():
            print(conv_path)
            
            # read out the convergence_parameter and the energy of one of the sp calcs
            lat_dirs = [sub_path for sub_path in sorted(conv_path.iterdir())]
            lat_dir = lat_dirs[int(len(lat_dirs)/2)]
            
            with open(lat_dir / 'inputcard.json') as f:
                inputcard_data = json.loads(f.read())

            conv_para_value = inputcard_data[conv_parameter[0]][conv_parameter[1]]
            if type(conv_para_value) == list:
                conv_para_value = conv_para_value[0]

            en_data = pd.read_csv(lat_dir / 'output.csv', index_col=0).loc['e_tot']
            
            if (conv_path / 'lat_const_out.csv').exists():
                lat_data = pd.read_csv(conv_path / 'lat_const_out.csv').iloc[0]
            else:
                lat_data = lattice_relax_postprocessing(conv_path)

            energy_conv.append([conv_para_value, en_data.value, en_data.unit, lat_data.value, lat_data.unit])
        
        energy_conv = pd.DataFrame(energy_conv, columns=['conv_para', 'e_tot', 'e_tot_unit', 'lat_const', 'lat_const_unit'])
        energy_conv.set_index('conv_para', inplace=True)
        
        # save the convergence data
        energy_conv.sort_index(inplace=True)
        energy_conv.to_csv(convergence_path)
    else:
        energy_conv = pd.read_csv(convergence_path, index_col='conv_para')

    # check for convergence
    if (path / 'output.dat').exists():
        (path / 'output.dat').unlink()

    old = 0
    old_lats = []
    old_energies = []

    print(energy_conv)
    for lat_const_idx in range(energy_conv.lat_const.size):
        lat_const = energy_conv.iloc[lat_const_idx].lat_const
        energy = energy_conv.iloc[lat_const_idx].e_tot
        
        lat_diffs = [np.abs(old_lat - lat_const) for old_lat in old_lats]
        en_diffs = [np.abs(energy - old_energy) for old_energy in old_energies]
        
        print(np.all(np.array(lat_diffs) < lat_threshold) and np.all(np.array(en_diffs) < en_threshold))

        if np.all(np.array(lat_diffs) < lat_threshold) and np.all(np.array(en_diffs) < en_threshold) and lat_diffs != []:
            print(energy_conv.iloc[lat_const_idx-len(old_lats)].name)
            with open(path/'output.dat', 'w') as f:             
                f.write(f'Lattice Convergence up to {lat_threshold}  and Energy Convergence up to {en_threshold} was achieved with {energy_conv.iloc[lat_const_idx - len(old_lats)].name} {conv_parameter[1]}')
            break
            
        old_lats.append(lat_const)
        old_energies.append(energy)
        if len(old_lats) > comparisons:
            old_lats.pop(0)
            old_energies.pop(0)


    # plot energy convergence
    plot_convergence(conv_para  = energy_conv.index, 
                     values     = energy_conv.e_tot, 
                     unit       = energy_conv.e_tot_unit.iloc[0], 
                     bound      = en_threshold, 
                     out_path   = path / 'energy_plot',
                     size       = (12,7),
                     converged_value    = energy_conv.iloc[lat_const_idx - len(old_energies)].e_tot,
                     converged_para     = energy_conv.iloc[lat_const_idx- len(old_energies)].name
                     )
    # plot lattice data convergence
    plot_convergence(conv_para          = energy_conv.index, 
                     values             = energy_conv.lat_const, 
                     unit               = energy_conv.loc[:,'lat_const_unit'].iloc[0], 
                     bound              = lat_threshold, 
                     out_path           = path / 'lat_plot', 
                     converged_value    = energy_conv.iloc[lat_const_idx - len(old_lats)].lat_const, 
                     converged_para     = energy_conv.iloc[lat_const_idx - len(old_lats)].name
                     )
    
    


def main():

    parser = argparse.ArgumentParser("Automated Convergence Test check for the Giessen KKR code")


    parser.add_argument('-p', '--path', dest='path',
                        help='path where the calculation is supposed to be performed. Will create subdirectories <path>/voro and <path>/scf')
    
    parser.add_argument('-b', '--conv_bound', dest='c_bound', type=float, 
                        help='bound to achieve convergence, in the atomic units (unless changed with conv_unit | not implemented yet)')

    parser.add_argument('-c','--convergence_parameter', dest='conv_paras',
                        help='parameter to be used for the convergence of the format <dict:parameter> [e.g <lattice:lattice-constant>] to be converged in this run [! they will have the same values!]')
    
    parser.add_argument('--convergence_criterion', dest='conv_crit', default='lat-const',
                        help='the criterion on which the convergence of the calculation is to be evaluated # so far only lat-const implemented for now only 2 option <lat-const> and <energy>')



    args = parser.parse_args()

    if args.conv_crit == 'lat-const':
        out_path = pl.Path(args.path)
        determine_lat_convergence(out_path, args.conv_paras.split(':'), args.c_bound)



if __name__ == '__main__':
    main()