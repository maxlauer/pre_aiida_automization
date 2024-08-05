import pathlib as pl
import numpy as np
import shutil
import sys
import json

import pandas as pd
import argparse

from inputcard_converter import Inputcard
import voronoi as voro


def extract_scf_data(inputcard, calc_path, output_file):
    # extracts energy (in e.v and the lattice constant and writes them, as well as the version of the code into a file)
    out_file_path = calc_path / output_file

    with open(out_file_path, 'r') as out_file:
        lines = out_file.readlines()
    
    lattice_constant = inputcard.get_parameter('lattice')['lattice-constant']

    fermi_energy = None
    last_threshold = 1
    total_energy = None
    for line in lines:
        content = line.strip('\n').split()
        if 'FERMI' in content:
            fermi_energy = content[3]

        if len(content) > 1 and content[0:3] == ['total', 'energy', 'in']:
            total_energy = float(content[-1])
        
        if 'rms-error' in content and "no.:" in content:
            last_threshold = float(content[-1].replace('D', 'e'))

    bound = inputcard.get_parameter('scf-cycle')['QBOUND']
    if last_threshold < bound:
        if pl.Path(calc_path / 'NOT_CONVERGED').exists():
            pl.Path(calc_path / 'NOT_CONVERGED').rename(calc_path / 'CONVERGED')
        with open(calc_path / 'CONVERGED', 'w') as f:
            f.write(f'The calculation converged with a threshold of {last_threshold} < {bound}')
    else:
        with open(calc_path / 'NOT_CONVERGED', 'w') as f:
            f.write(f'The calculation did not converge with a threshold of {last_threshold} > {bound}')
        
        print(1, file=sys.stdout)
    
    out_df = pd.DataFrame([[lattice_constant, 'a0'], [fermi_energy, 'Ry'], [total_energy, 'Ry']], index=['lat_const', 'e_fermi', 'e_tot'], columns = ['value', 'unit'])
    out_df.to_csv(calc_path.parent / 'output.csv')


def main():

    parser = argparse.ArgumentParser("Postprocessing of a single point calculation using the Giessen-KKR code")

    parser.add_argument('-p', '--path', dest='path', 
                        help='path where the calculation is supposed to be performed. Will create subdirectories <path>/voro and <path>/scf')
    parser.add_argument('-i', '--json_input_path', dest='json_inp_path',
                        help='path to the json input to be used as the template for the inputcard')
    parser.add_argument('-w', '--weight_relation', dest='weight_rel', nargs='*', default=[],
                        help='The indices of the atoms, from which the empty spheres should take the weights (amount = # of empty spheres). The default behaviour is all weights =1')


    parser.add_argument('--kkr_output_name', dest='kkr_out_file', default='kkr.out',
                        help='name of the files created by the kkr code. Default is <kkr.out>')    

    parser.add_argument('--parallel', dest='para_bool', action='store_true', 
                        help='flag, enabeling the use of parallel kkr')

    args = parser.parse_args()

    inputcard = Inputcard()
    inputcard.read_in_json(args.json_inp_path)

    calc_path = pl.Path(args.path)
    extract_scf_data(inputcard, calc_path, args.kkr_out_file)

    print(0, file=sys.stdout)


if __name__ == '__main__':
    main()