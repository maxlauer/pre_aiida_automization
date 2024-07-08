import subprocess
from subprocess import run
import pathlib as pl
import numpy as np
from copy import deepcopy
from inputcard_converter import Inputcard

_REFOPT_NAME = 'ref.pot'
_STARTPOT_NAME = 'start.pot'


def prepare_voronoi_inputcard(in_inputcard, voro_opts = {'DetermineWeights': 1}, weights = [], keep_empty_spheres = False):
    
    inputcard = deepcopy(in_inputcard)
    # give voroOpts as Testopt
    if voro_opts != {}:
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
        if atom['Z'] != 0 or keep_empty_spheres:
            new_atominfo.append(atom)
            new_atom_basis.append(basis)
    
    if weights == []:
        weights = [1 for atom in new_atominfo]
    elif len(weights) < len(new_atominfo):
        raise ValueError("Weights were not supplied for all atoms ")
    elif len(weights) > len(new_atominfo):
        raise ValueError('Too many weights supplied, the latter ones were ignored')
    
    for idx in range(len(new_atominfo)):
        new_atominfo[idx]['WEIGHT'] = weights[idx]

    inputcard.change_parameter('atominfo', new_atominfo, 'r')
    inputcard.change_parameter('lattice', {'atom-basis': new_atom_basis}, 'a')

    weight_atominfo = []
    for weight in weights:
        weight_atominfo.append({"WEIGHT": weight})
    
    return inputcard


def perform_voroni(inputcard, out_path):

    out_path = out_path / 'voro'
    if not out_path.exists():
        out_path.mkdir(parents = True)

    inputcard_path = out_path / 'inputcard.voro'
    documentation_path = out_path / 'voro.out'

    voro_cmd = f"voronoi {inputcard_path} {documentation_path}"
    voro_cmd += f" && mv GraphicalOutput.txt {out_path / 'GraphicalOutput.txt'}"

    voro_inputcard = prepare_voronoi_inputcard(inputcard)
    voro_inputcard.write_to(inputcard_path)

    output = run(voro_cmd, shell=True, capture_output=True, text=True)
    
    # test that voronoi finished successfully
    if output.stdout.split('\n')[-2] != ' Voronoi utility finished.':
        raise RuntimeError("Voronoi Utility did not finish successfully")
    
    num_atoms = len(voro_inputcard.get_parameter('atominfo'))
    # read out the voro
    with open(documentation_path, 'r') as f:
        voro_lines = f.readlines()[-(num_atoms):]

    weights = []
    mt_radii = []
    for atom in voro_lines:
        content = atom.strip('\n').split()
        
        weights.append(content[-2])
        mt_radii.append(content[-1])

    return weights, mt_radii

def perform_old_voronoi(inputcard, out_path, weights = []):
    
    out_path = out_path / 'voro'
    if not out_path.exists():
        out_path.mkdir(parents = True)

    inputcard_path = out_path / 'inputcard.voro_old'
    documentation_path = out_path / 'voro_old.out'

    voro_old_cmd = f"cd {out_path} &&"
    voro_old_cmd += f"old_voronoi {inputcard_path.name} {documentation_path.name}"
    voro_old_cmd += f"&& mv output.pot {_STARTPOT_NAME} && cd - /dev/null"

    voro_old_inputcard = prepare_voronoi_inputcard(inputcard, voro_opts={}, weights=weights, keep_empty_spheres=True)
    voro_old_inputcard.change_parameter('cluster', {"RCLUSTZ": 1.5, "RCLUSTXY": 1.5})
    voro_old_inputcard.write_to(inputcard_path)

    output = run(voro_old_cmd, shell=True, capture_output=True, text=True)
    
    with open(documentation_path, 'r') as f:
        lines = f.readlines()

    alat = voro_old_inputcard.get_parameter('lattice')['lattice-constant']

    radii = []
    for line in lines:
        content = line.split()
        if len(content) != 0 and content[0:2] == ['Atom', '..']:
            radii.append({'alat': alat, 'rmt': content[8], 'rmax': content[11]})
    
    return out_path / _STARTPOT_NAME, radii


def perform_const(atom_radii, out_path, verbosity = 0):
    const_cmd = "Const RMT "

    out_path = out_path / 'voro'
    if not out_path.exists():
        out_path.mkdir(parents = True)

    constant_pot = ""
    for idx, radii in enumerate(atom_radii):
        atom_const_cmd = f"cd {out_path} && "
        atom_const_cmd += f"{const_cmd} {radii['alat']} {radii['rmt']} {radii['rmax']}"
        
        # move the created constant.pot file into out_path
        atom_const_cmd += f" && mv Constant.pot Constant_{idx + 1}.pot && cd - > /dev/null"
        
        if verbosity == 0:
            run(atom_const_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open(out_path / f'Constant_{idx + 1}.pot', 'r') as f:
            constant_pot += "".join(f.readlines())

    with open(out_path / _REFOPT_NAME, 'w') as out_f:
        out_f.write(constant_pot)

    return out_path / _REFOPT_NAME, [{'REFPOT':idx+1} for idx in range(len(atom_radii))]




if __name__ == '__main__':
    
    norm = 1/np.sqrt(2)

    dict = {
        'testopt': ['VBCZERO'],
        'lattice': {
            'bravais-lattice': [[norm, norm, 0], [norm, 0, norm], [0, norm, norm]],
            'lattice-constant': 5.4,
            'CARTESIAN': 'T',
            'atom-basis': [[0, 0, 0],
                       [norm/2, norm/2, norm/2],
                       [norm, norm, norm],
                       [-norm/2, -norm/2, -norm/2]]
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
    weight, mt = perform_voroni(inp, path)
    
    weights = weight * 2

    start_pot_path, atom_radii = perform_old_voronoi(inp, path, weights)
    
    inp.set_startpot(start_pot_path.name)

    ref_pot_path, atominfo_change= perform_const(atom_radii, path)
    
    inp.change_parameter('atominfo', atominfo_change, 'c')
    inp.set_refpot(ref_pot_path.name)
    print(inp)
