from subprocess import run
import pathlib as pl
import numpy as np
from copy import deepcopy
from inputcard_converter import Inputcard


def prepare_voronoi_inputcard(in_inputcard, voro_opts = {'DetermineWeights': 1}):
    
    inputcard = deepcopy(in_inputcard)
    # give voroOpts as Testopt
    inputcard.add_testopt('voroOpts')
    inputcard.change_parameter('voro-opts', voro_opts)

    inputcard.set_refpot("")
    inputcard.set_startpot("")

    # remove empty spheres
    atominfo = inputcard.get_parameter('atominfo') #[atom for atom in inputcard.get_parameter('atominfo') if atom['Z'] != 0]
    atom_basis = inputcard.get_parameter('lattice')['atom-basis']
    
    new_atominfo = []
    new_atom_basis = []
    for atom, basis in zip(atominfo, atom_basis):
        if atom['Z'] != 0:
            new_atominfo.append(atom)
            new_atom_basis.append(basis)

    inputcard.change_parameter('atominfo', new_atominfo, 'r')
    inputcard.change_parameter('lattice', {'atom-basis': new_atom_basis}, 'a')

    return inputcard


def perform_voroni(inputcard, out_path):

    out_path = out_path / 'voro'
    if not out_path.exists():
        out_path.mkdir()

    inputcard_path = out_path / 'inputcard.voro'

    voro_cmd = f"voronoi {inputcard_path} {out_path / 'voro.out'}"

    voro_inputcard = prepare_voronoi_inputcard(inputcard)
    voro_inputcard.write_to(inputcard_path)

    run(voro_cmd, shell=True)



if __name__ == '__main__':
    
    dict = {
        'lattice': {
            'bravais-lattice': [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
            'lattice-constant': 5.4,
            'CARTESIAN': 'T',
            'atom-basis': [[0, 0, 0],
                       [np.sqrt(2), np.sqrt(2), np.sqrt(2)],
                       [1/np.sqrt(2), 1/np.sqrt(2), 1/np.sqrt(2)],
                       [-np.sqrt(2), -np.sqrt(2), -np.sqrt(2)]]
        },
        'atominfo': [
            {
            'Z': 49,
            'LMXC': 2,
            'KFG': "4 4 3 0",
            'CLS': 1,
            'REFPOT': 1
            },
            {
            'Z': 7,
            'LMXC': 0,
            'KFG': "1 0 0 0",
            'CLS': 1,
            'REFPOT': 2
            },
            {
            'Z': 0,
            'LMXC': 0,
            'KFG': "0 0 0 0",
            'CLS': 1,
            'REFPOT': 1
            },
            {
            'Z': 0,
            'LMXC': 0,
            'KFG': "0 0 0 0",
            'CLS': 1,
            'REFPOT': 1
            }
        ]
    }

    inp = Inputcard(dict)
    #print(inp)
    path = pl.Path('calc/test')
    perform_voroni(inp, path)