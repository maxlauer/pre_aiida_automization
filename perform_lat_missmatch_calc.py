import pathlib as pl
import argparse
import numpy as np
from subprocess import run

from inputcard_converter import Inputcard
from lattice_missmatch_calc import prepare_lattice_missmatch_relaxation


def main():

    parser = argparse.ArgumentParser("Automated Convergence Tests for the Giessen KKR code")

    parser.add_argument('-p', '--path', dest='path', default='test',
                        help='path where the calculation is supposed to be performed. Will create subdirectories path/voro and path/scf')
    parser.add_argument('-i', '--json_input_path', dest='json_inp_path', default='inputcard_InN.json',
                        help='path to the json input to be used as the template for the inputcard. - The lattice constant of this inputcard is taken as the inital guess of the lat-con calculation')
    
    parser.add_argument('--max_dev', dest='max_dev', default = 0.2,
                        help='maximal deviation of the lattice constant from the supplied equilibrium value, (if > 1) treated as %')
    parser.add_argument('--lattice_points', dest='lat_points', default=10,
                        help='number of lattice constants calculated')
    
    parser.add_argument('--min_missmatch_ratio', dest='min_missmatch_ratio', default=0.5,
                        help='The minimum missmatch ratio calculated')
    parser.add_argument('--max_missmatch_ratio', dest='max_missmatch_ratio', default=2,
                        help='The maximum missmatch ratio calculated')
    parser.add_argument('--missmatch_points', dest='missmatch_points', default=10,
                        help='The amount of missmatch point-calculations performed')
    
    
    args = parser.parse_args()

    base_path = pl.Path(args.path)

    max_dev = args.max_dev
    if max_dev > 1:
       max_dev = max_dev / 100 


    inputcard = Inputcard()
    inputcard.read_in_json(args.json_inp_path) 

    init_lat_const = inputcard.get_parameter('lattice')['lattice-constant']
    deviations = np.linspace(-max_dev, max_dev, args.lat_points)

    for dev in deviations:
        
        lat_const = init_lat_const * (1 + dev)
        lat_path = base_path / f"{lat_const:.2f}"

        lat_path.mkdir(parents=True, exist_ok=True)

        prepare_lattice_missmatch_relaxation(
            relax_path      = lat_path, 
            inputcard       = inputcard, 
            min_ratio       = args.min_missmatch_ratio,
            max_ratio       = args.max_missmatch_ratio,
            en_points       = args.missmatch_points,
            lattice_constant= lat_const
            )

if __name__ == '__main__':
    main()