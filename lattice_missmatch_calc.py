import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pathlib as pl

from copy import deepcopy
from scipy.optimize import curve_fit, minimize

from inputcard_converter import Inputcard


def polynom(x, a0, a1, a2, a3):
    return a0 + a1 * x + a2 * x**2 + a3 * x**3

def prepare_lattice_missmatch_relaxation(relax_path, inputcard, min_ratio, max_ratio, en_points, precision=3, lattice_constant=None):
    # implicitly uses the lattice constant of the inputcard given as the lattice constant of a=b
    def get_dirname(ratio):
        name=f'ac_{ratio:.2f}'

        return name

    if lattice_constant:
        in_plane_lat_const = lattice_constant # primitive lattice constant in a0
        inputcard.change_parameter('lattice', {'lattice-constant': lattice_constant})
    else:
        in_plane_lat_const = float(inputcard.get_parameter('lattice')['lattice-constant'])

    bravais_lat = np.array(inputcard.get_parameter('lattice')['bravais-lattice']).T

    ## create directory for running original scf cycle and generate the starting potential
    calc_path = relax_path / get_dirname(1)
    calc_path.mkdir(parents=True, exist_ok=True)
    inputcard.write_to_json(calc_path / 'inputcard.json')
    

    c_over_a_ratios = np.linspace(min_ratio, max_ratio, en_points)
    
    for ratio in c_over_a_ratios:
        if ratio == 1:
            continue
        calc_path = relax_path / get_dirname(ratio)
        calc_path.mkdir(parents=True, exist_ok=True)

        trans_mat = np.eye(3)
        trans_mat[2,2] = ratio
        new_bravais = np.matmul(bravais_lat, trans_mat)
        
        inputcard.change_parameter('lattice', {'bravais-lattice': new_bravais.T.tolist()})
        inputcard.write_to_json(calc_path / 'inputcard.json')
        #print(trans_mat)

if __name__ == '__main__':
    inputcard = Inputcard()
    inputcard.read_in_json('inputcard_InN.json')

    path = pl.Path('test_lat_missmatch')

    prepare_lattice_missmatch_relaxation(path, inputcard, 0.5, 2, 7)
    #prepare_lattice_missmatch_relaxation('test_lat_missmatch', inputcard, 2, 5, lattice_constant=5.6)