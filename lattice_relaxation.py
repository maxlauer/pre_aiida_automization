import numpy as np
import pandas as pd
import pathlib as pl
import matplotlib.pyplot as plt

from copy import deepcopy
from scipy.optimize import curve_fit, minimize
from matplotlib.ticker import StrMethodFormatter

from inputcard_converter import Inputcard

_CSV_PATH = 'output.csv'

def polynom(x, a0, a1, a2, a3):
    return a0 + a1 * x + a2 * x**2 + a3 * x**3

def plot_fit(data, params, out_path, func=polynom, eq_lat_const = None):
    fig, ax = plt.subplots(figsize=(7,5))

    lat_unit = data.lat_const_unit[0]
    data.plot.scatter(x='lat_const', y='e_tot', ax=ax)
    
    x_fit = np.linspace(data.lat_const.min(), data.lat_const.max(), 100)
    y_fit = func(x_fit, *params)
    ax.plot(x_fit,y_fit)

    if eq_lat_const:
        ax.axvline(x=eq_lat_const, color = 'grey', linestyle='--', label = '$a_{eq}$'+f' {eq_lat_const:.3f} {lat_unit}')

    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.3f}'))
    
    ax.set_xlabel('Lattice constant $a$ /' + f' [{lat_unit}]')
    ax.set_ylabel('$E_{tot}$' + f' [{data.e_tot_unit[0]}]')
    ax.legend()

    if out_path.exists():
        out_path.unlink()
    fig.savefig(out_path)
    plt.close()


def fit_rel_data(data, func=polynom):
    """
    takes output data as DataFrame with two columns 'lat_const', 'e_tot', then fits it with a callable function
    """
    x0_guess = data.loc[int(data.lat_const.size/2), 'lat_const']
    
    params, conv = curve_fit(func, data.lat_const, data.e_tot)
    eq_lat_const = minimize(fun=func, x0=x0_guess, args=tuple(params))
    return [eq_lat_const.x[0], data.lat_const_unit.iloc[0]], params


def lattice_relax_postprocessing(calc_path):
    lat_rel = []

    # read out the data and save it in calc_path
    for path in calc_path.iterdir():
        if not path.is_dir():
            continue
        data_path = path / _CSV_PATH
        data_df = pd.read_csv(data_path, index_col= 0)
        data = data_df.loc['lat_const'].to_list() + data_df.loc['e_tot'].to_list()

        lat_rel.append(data)        
    lat_rel_df = pd.DataFrame(lat_rel, columns=['lat_const', 'lat_const_unit', 'e_tot', 'e_tot_unit'])
    # save in calc_path/lat_rel.csv
    lat_rel_df.to_csv(calc_path/'lat_rel.csv', index=False)

    # fit the data to the polynomial function
    eq_lat_data, params = fit_rel_data(lat_rel_df)

    # plot the data
    plot_fit(lat_rel_df, params, calc_path/'lat_plot.png', eq_lat_const=eq_lat_data[0])

    # wrtie the equilibrium data
    eq_lat_df = pd.DataFrame([eq_lat_data], index=['eq_lat_const'], columns = ['value', 'unit'])
    eq_lat_df.to_csv(calc_path/'lat_const_out.csv')
    
    return eq_lat_df.loc['eq_lat_const']


    
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
