import numpy as np
import argparse
from copy import deepcopy

from inputcard_converter import Inputcard



def prepare_lattice_relaxation(relax_path, inputcard, max_dev, en_points, precision=3):
    def get_dirname(dev):
        name = ''
        if dev == 0:
            name = 'n'
        elif dev < 0:
            name = f'm_{np.abs(dev * 100):.2f}'
        elif dev > 0:
            name = f'p_{dev * 100:.2f}'
        
        return name
    
    inital_lat_const = float(inputcard.get_parameter('lattice')['lattice-constant'])

    new_inputcard = deepcopy(inputcard)

    if max_dev > 1:
        max_dev = max_dev / 100

        deviations = np.linspace(-max_dev, max_dev, en_points)

    for dev in deviations:
        
        calc_path = relax_path / get_dirname(dev)
        calc_path.mkdir(parents=True, exist_ok=True)

        new_lat_const = inital_lat_const * (1 + dev)

        new_inputcard.change_parameter('lattice', {'lattice-constant': new_lat_const})
        new_inputcard.write_to_json(calc_path / 'inputcard.json')
