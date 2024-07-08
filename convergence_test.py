import pathlib as pl
import argparse
import numpy as np
from subprocess import run

from inputcard_converter import Inputcard
from lattice_relaxation import prepare_lattice_relaxation


def main():

    parser = argparse.ArgumentParser("Automated Convergence Tests for the Giessen KKR code")

    parser.add_argument('-p', '--path', dest='path', 
                        help='path where the calculation is supposed to be performed. Will create subdirectories <path>/voro and <path>/scf')
    parser.add_argument('-i', '--json_input_path', dest='json_inp_path',
                        help='path to the json input to be used as the template for the inputcard. [The lattice constant of this inputcard is taken as the inital guess of the lat-con calculation]')
    parser.add_argument('-w', '--weight_relation', dest='weight_rel', nargs='*', default=[],
                        help='The indices of the atoms, from which the empty spheres should take the weights [amount = # of empty spheres]. The default behaviour is all weights =1')


    parser.add_argument('-c','--convergence_parameter', dest='conv_paras', nargs='*',
                        help='list of parameters of the format <dict:parameter> [e.g <lattice:lattice-constant>] to be converged in this run [! they will have the same values!]')
    parser.add_argument('-r', '--convergence_range', dest='conv_range', nargs=3,
                        help='list of <Min_value Max_value Step_size>')
    
    parser.add_argument('--convergence_criterion', dest='conv_crit', default='lat-const',
                        help='the criterion on which the convergence of the calculation is to be evaluated # so far only lat-const implemented for now only 2 option <lat-const> and <energy>')
    
    parser.add_argument('--perform_lat_relaxation', dest='lat_bool', action='store_true',
                        help='flag for calculating the lattice constant, while not taking the convergence on lattice constant as the convergence criterion')
    parser.add_argument('--max_deviation', dest='max_dev', default=5,
                        help='max deviation of the lattice constant if > 1 in %')
    parser.add_argument('--num_energy_points', dest='en_points', type=int, default=5,
                        help='number of energy points to be calculated for the lattice relaxation')

    parser.add_argument('--slurm_script', dest='slurm_script', default='/home/agHeiliger/lauerm/bin/kkr_workflows/inputcard-converter/slurm_conv_s1.job',
                        help='path to the slurm script to be started at the end of the directory creation')

    args = parser.parse_args()

    inputcard = Inputcard()
    inputcard.read_in_json(args.json_inp_path) 

    path = pl.Path(args.path)

    conv_check = np.arange(int(args.conv_range[0]), int(args.conv_range[1]), int(args.conv_range[2]))
    conv_para_keys = [conv_para.split(':')[0] for conv_para in args.conv_paras]
    conv_para_vals = [conv_para.split(':')[1] for conv_para in args.conv_paras]
    
    proto_change_dict = {key: {} for key in set(conv_para_keys)}

    if args.conv_crit == 'lat-const' or args.lat_bool:

        change_dict = proto_change_dict.copy()

        for para in conv_check:
            for key, val in zip(conv_para_keys, conv_para_vals):
                if (val == 'KMIN' or val == 'KMAX') and type(para) != list:
                    change_dict[key][val] = [int(para)] * 3
                else:
                    change_dict[key][val] = int(para)
                
                inputcard.change_parameter(key, change_dict[key])

            para_path = path / f"conv_{para}"
            prepare_lattice_relaxation(para_path, inputcard, args.max_dev, args.en_points)

    slurm_path = pl.Path(args.slurm_script)
    task_num = int(args.en_points) * len(conv_check) - 1
    #change the array size of the slurm script and save it in the specified path
    change_slurm_script_cmd = f"sed 's/CHANGE/{task_num}/g' {args.slurm_script} > {path.parent / slurm_path.name}"
    run(change_slurm_script_cmd, shell=True)
    sbatch_cmd = f"sbatch {path.parent / slurm_path.name} -p {path} -w {",".join(args.weight_rel)} -e {args.en_points}"
    run(sbatch_cmd, shell=True)


if __name__ == '__main__':
    main()
