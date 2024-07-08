import pathlib as pl
import numpy as np
import shutil
import sys
import json

import pandas as pd
import argparse

from inputcard_converter import Inputcard
import voronoi as voro


def preprocess_scf_calc(inputcard, calc_path, weight_relation=[], write_json=False):
    # since the voronoi program can't handle empty sphere weights yet it has to be supplied how the empty sphere weights are to be handled
    # weight relation is supposed to be a list of length num_vac
    # e.g weight_relation = [0,0,1, -1] - specifies 3 empty spheres (in the order of atominfo - they have to be at the end) where the first 
    # two empty spheres will get the same weight calculated for atom with index 0, the third with the weight
    # of atom 2 and the fourth will default to 1.0
    # if weight relation is not supplied all of them will default to 1.0

    scf_path = calc_path / 'scf-calc'
    scf_path.mkdir(parents=True, exist_ok=True)

    atom_weights, _ = voro.perform_voroni(inputcard, calc_path)
    
    weights = [float(w) for w in atom_weights]
    if weight_relation == []:
        weights += [1.0 for idx in range(inputcard.get_atomnum() - len(atom_weights))]

    elif len(weight_relation) == (inputcard.get_atomnum() - len(atom_weights)):
        for idx in weight_relation:
            idx = int(idx)
            if idx == -1:
                weights.append(1.0)
                continue
            weights.append(float(atom_weights[idx]))

    else:
        raise ValueError("The length of weight relation is wrong")


    start_pot_path, atom_radii = voro.perform_old_voronoi(inputcard, calc_path, weights)
    
    ref_pot_path, atominfo_change= voro.perform_const(atom_radii, calc_path)
    
    # set weight here as well .. idk probably not important anymore after voro .. but good for doc
    for idx, weight in enumerate(weights):
        atominfo_change[idx]['WEIGHT'] = weight

    inputcard.change_parameter('atominfo', atominfo_change, 'c')

    inputcard.set_startpot(start_pot_path.name)
    inputcard.set_refpot(ref_pot_path.name)
    
    # copy the start and refpot to the scf_path
    shutil.copyfile(start_pot_path, scf_path / inputcard.get_startpot())
    shutil.copyfile(ref_pot_path, scf_path / inputcard.get_refpot())

    inputcard.write_to(scf_path / 'inputcard.scf')
    
    if write_json == True:
        inputcard.write_to_json(scf_path / inputcard.json)
    
    return scf_path
    


def main():

    parser = argparse.ArgumentParser("Preprocessing of a single point calculation using the Giessen-KKR code")

    parser.add_argument('-p', '--path', dest='path', 
                        help='path where the calculation is supposed to be performed. Will create subdirectories <path>/voro and <path>/scf')
    parser.add_argument('-i', '--json_input_path', dest='json_inp_path',
                        help='path to the json input to be used as the template for the inputcard')
    parser.add_argument('-w', '--weight_relation', dest='weight_rel', nargs='*', default=[],
                        help='The indices of the atoms, from which the empty spheres should take the weights (amount = # of empty spheres). The default behaviour is all weights =1')


    parser.add_argument('--write_json_inputcard', dest='write_json', action='store_true',
                        help='flag to determine whether a json representation of the inputcard should be stored in the calculation dir or not (default is false)')
    parser.add_argument('--kkr_output_name', dest='kkr_out_file', default='kkr.out',
                        help='name of the files created by the kkr code. Default is <kkr.out>')    

    args = parser.parse_args()

    global kkr_file
    kkr_file = args.kkr_out_file

    inputcard = Inputcard()
    inputcard.read_in_json(args.json_inp_path)

    calc_path = pl.Path(args.path)
    scf_path = preprocess_scf_calc(inputcard, calc_path, args.weight_rel, args.write_json)

    print(scf_path, file=sys.stdout)


if __name__ == '__main__':
    main()
