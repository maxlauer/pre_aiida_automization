import json
import numpy as np
import pathlib as pl

from hardcoded import interface, zperiodl, linpol, mmin, decimation, ewald, constant_block

# default values for Inputcard
with open("default_parameter.json", 'r') as jfile:
    default = json.load(jfile)


class Inputcard:

    _DEFAULT_REFPOT = 'Constant.pot'
    _DEFAULT_STARTPOT = 'output.pot'

    _DEFAULT_JELLPATH = pl.Path('/home/agHeiliger/shared/atomic-start-potentials/')

    ALAT_PREC = 4
    ATOMINFO_TERMS = ['Z', 'LMXC', 'KFG', 'CLS', 'REFPOT', 'NTC', 'FAC', 'IRNS', 'SCALD', 'WEIGHT']

    def __init__(self, dict = {}):
        
        # default settings
        self.cluster_prec = 1
        self.alat_prec = 4
        self.lat_prec = 10

        # deafult files
        self.refpot = Inputcard._DEFAULT_REFPOT
        self.startpot = Inputcard._DEFAULT_STARTPOT
        self.shapefun = ""
        self.scoef = ""

        # default option parameters
        self.runopts = default['runopt']
        self.testopts = default['testopt']

        # default general parameters - "general"
        self.gen_parameters = default['general']

        self.cluster = default['cluster']
        self.energy_contour = default['energy-contour']
        self.scf_cyc = default['scf-cycle']

        # this is temporary - need to exchange this with real functionality
        self.lattice = default['lattice']
        self.atominfo = []

        # Voronoi options
        self.voro_opts = default['voro-opts']

        # read in the input supplied
        for key in dict.keys():
            self.change_parameter(key, dict[key])


        # until here


    def write_to(self, out_filepath):
        with open(out_filepath, 'w') as out_file:
            out_file.write(self.__str__())

    ## write to file
    def __str__(self):
        output_string = f"{"":<9}***** Input file for TB-KKR code *****\n***** Generated using the Aiida Inputcard-parser *****\n"
        
        # write out run opts preamble
        output_string += f"{"":<15}***Running options***\nRUNOPT\n"
        # run options
        for option in self.runopts:
            output_string += f"{option:<8} "        
        output_string += f"\n{"+-------" * 7}+\n"

        # write test opts preamble
        output_string += f"{"":<15}***test options*** (2 lines)\nTESTOPT\n"
        counter = 0
        for option in self.testopts:
            output_string += f"{option:<8} "
            counter += 1
            if counter == 6:
                output_string += "\n"
        if counter < 4:
            output_string += "\n"
        output_string += f"\n{"+-------" * 7}+\n"

        # write LMAX Line
        output_string += f"{"":<7}LMAX={self.gen_parameters['LMAX']}{"":<5}NSPIN={self.gen_parameters['NSPIN']}{"":<5}NATYP={len(self.atominfo)}{"":<5}KMT={self.gen_parameters['KMT']}"
        output_string += f"\n{"+-------" * 7}+\n"
        # Write the jellpath
        output_string += f"JELLPATH='{Inputcard._DEFAULT_JELLPATH}/'\n"
        
        # Write New Voronoi Options (If VoroOpts in the Testoptions)
        if "voroOpts" in self.testopts:
            if self.voro_opts == {}:
                print(ValueError("No Options were supplied for the new Voronoi"))
            for option, value in self.voro_opts.items():
                output_string += f"\n{option}={value}"
        
        output_string += f"\n{"+-------" * 7}+\n"


        # only temporary lattice as a dictionary object .. myb not as temporary
        output_string += f"{"":<12}** Description of lattice **\n"
        
        #lattice constants
        output_string += f"ALATBASIS= {self.lattice['lattice-constant']:<9.{self.alat_prec}f} {1.0:<9.{self.alat_prec}f} {1.0:<9.{self.alat_prec}f} lattice constant\n"
        
        #scaling factors
        output_string += f"BASISCALE= {self.lattice['lattice-scaling'][0]:<9.{self.alat_prec}f} {self.lattice['lattice-scaling'][0]:<9.{self.alat_prec}f} {self.lattice['lattice-scaling'][0]:<9.{self.alat_prec}f} scaling factor\n"
        
        #Bravais lattice
        # idk what LATTICE does so it is hard coded for now
        output_string += "LATTICE=1\nBRAVAIS"
        for vector in self.lattice['bravais-lattice']:
            output_string += f"\n{"":<5}"
            first = True
            for component in vector:
                if not component < 0 and first:
                    output_string += " "
                    first = False
                output_string += f"{"":<2}{component:<13.{self.lat_prec}f}"
        
        output_string += f"\n{"+-------" * 7}+\n"

        # write the basis
        output_string += f"{"":<3}{'NAEZ':>6}={len(self.atominfo):<7}"
        for para in ['NEMB', 'NEMBZ', 'KAOEZ']:
            output_string += f"{para:>6}={self.lattice[para]:<7}"
        output_string += f'\nCARTESIAN= {self.lattice['CARTESIAN']}{"":<5}//T - Cartesian Basis | F - Direct Basis\nRBASIS'
        
        for vector in self.lattice['atom-basis']:
            output_string += f"\n{"":<5}"
            first = True
            for component in vector:
                if not component < 0 and first:
                    output_string += " "
                    first = False
                output_string += f"{"":<4}{component:<13.{self.lat_prec}f}"
        output_string += f"\nSCALING=  {self.lattice["basis-scaling"][0]:<16.{self.alat_prec}f} {self.lattice["basis-scaling"][1]:<16.{self.alat_prec}f} {self.lattice["basis-scaling"][2]:<16.{self.alat_prec}f}"
        output_string += f"\n{"+-------" * 7}+\n"
        # until here

        # atominfo
        output_string += f"ATOMINFO\n"
        atominfo_terms = [term for term in Inputcard.ATOMINFO_TERMS if term in self.atominfo[0].keys()] 


        for term in atominfo_terms:
            output_string += f"{term:<7}{"":<2}"
        output_string += '\n'

        for atom in self.atominfo:
            for term in atominfo_terms:
                output_string += f"{atom[term]:<7}{"":<2}"
            output_string += "\n"
        output_string += f"{"+-------" * 7}+\n"    
        
        # Energy contoure
        output_string += f"{"EMIN":<5}{"":<3}{"EMAX":<5}{"":<3}{"TEMPR":<5}{"":<3}{"NPOL":<5}{"":<3}{"NPT1":<5}{"":<3}{"NPT2":<5}{"":<3}{"NPT3":<5}{"":<3}\n"
        output_string += f"{self.energy_contour['EMIN']:<5.2f}{"":<3}{self.energy_contour['EMAX']:<5.2f}{"":<3}{int(self.energy_contour['TEMPR']):<5}{"":<3}{int(self.energy_contour['NPOL']):<5}{"":<3}{int(self.energy_contour['NPTS'][0]):<5}{"":<3}{int(self.energy_contour['NPTS'][0]):<5}{"":<3}{int(self.energy_contour['NPTS'][0]):<5}{"":<3}\n"
        output_string += f"{"+-------" * 7}+\n"

        # scf-cycle
        output_string += f"{"NSTEPS":<6}{"":<2}{"IMIX":<6}{"":<2}{"STRMIX":<6}{"":<2}{"FCM":<5}{"":<2}{"QBOUND":<7}{"":<2}{"BRYMIX":<6}{"":<2}{"ITDBRY":<6}{"":<2}\n"
        output_string += f"{int(self.scf_cyc['NSTEPS']):<6}{"":<2}{int(self.scf_cyc['IMIX']):<6}{"":<2}{self.scf_cyc['STRMIX']:<6.1f}{"":<2}{self.scf_cyc['FCM']:<5.1f}{"":<2}{format(self.scf_cyc['QBOUND'], ".1E").replace("E", "d"):<7}{"":<2}{self.scf_cyc['BRYMIX']:<6.1f}{"":<2}{int(self.scf_cyc['ITDBRY']):<6}{"":<2}\n"
        output_string += f"{"+-------" * 7}+\n"

        # print cluster information
        output_string += f"Parameters for the clusters (same: spherical else cylindical)\n"
        # need to find out how to convert the python format into something that fortran needs -- [TODO]
        #output_string += f"RCLUSTZ={format(self.cluster['RCLUSTZ'], f".{self.cluster_prec}E").replace('E', 'd')}"
        for clus in self.cluster.keys():
            output_string += f"{clus}={self.cluster[clus]:.{self.cluster_prec}f}d0     "
        output_string += f"\n{"+-------" * 7}+\n"

        ## This part is hardcoded for now
        output_string += constant_block
        output_string += f"\n{"+-------" * 7}+\n"
        output_string += interface
        output_string += f"\n{"+-------" * 7}+\n"
        output_string += zperiodl
        output_string += f"\n{"+-------" * 7}+\n"
        output_string += linpol
        output_string += f"\n{"+-------" * 7}+\n"
        output_string += mmin
        output_string += f"\n{"+-------" * 7}+\n"
        # until here

        # Files
        output_string += f"FILES\n{self.refpot:<54}I12\n{self.startpot:<54}I13\n{"-----":<54}I40\n{self.shapefun:<54}I19\n{self.scoef:<54}I25"
        output_string += f"\n{"+-------" * 7}+\n"

        ## This part is hardcoded for now
        output_string += f"\n{"*" * 57}\n"
        output_string += decimation
        output_string += f"\n{"+-------" * 7}+\n"
        output_string += ewald
        output_string += f"\n{"+-------" * 7}+\n"

        return output_string


    # setting meta settings (precision, files)
    def set_refpot(self, file_path):
        self.refpot = file_path
    def set_startpot(self, file_path):
        self.startpot = file_path
    def set_shapefunc(self, file_path):
        self.shapefunc = file_path
    def set_scoef(self, file_path):
        self.scoef = file_path

    # adding and changing options
    def get_runopts(self):
        return self.runopts
    def add_runopt(self, option):       #maybe it would be better to do this with a dict containing all possible options? and a bool if they should be used?
        self.runopts.append(option)
    def add_runopts(self, options):
        self.runopts += options
    def remove_runopt(self, option):
        self.runopts.remove(option)

    def get_testopts(self):
        return self.testopts
    def add_testopt(self, option):
        self.testopts.append(option)
    def add_testopts(self, options):
        self.testopts += options
    def remove_testopt(self,option):
        self.testopts.remove(option)

    def change_atominfo(self, new_atominfo, mode = 'a'):
        """            
        For Atominfo: has to supply dict as list of dicts (even if it is only 1)
                    'r' - replace - replaces the current atominfo with the value supplied (uses default paramters from <defualt_parameters.json>)
                    'a' - appends the dict supplied as new atom (!IF a key is not supplied a default is chosen)
                    'c' - changes the parameters of the atoms - either a dict, or a list of dicts with num_atoms as length (other will give error)
                          if a dict is supplied the keys in the dict will be used as default values, changing it for all atoms in atominfo
                          if a list of dicts is used the keys in the dicts will be changed for the respective atom in atominfo
                          Attention: afterwards a check will be made that all atoms have the same paramters, otherwise an error will be raised 
        """
        def append_atominfo(atominfo, new_atoms):
            for atom in new_atoms:
                atominfo.append(default['atominfo'].copy())
                for key in atom.keys():
                    atominfo[-1][key] = atom[key]
            
            return atominfo

        if mode == 'r':
            atominfo = []
        else:
            atominfo = self.atominfo


        if mode != 'c':
            self.atominfo = append_atominfo(atominfo, new_atominfo)
        else:
            if len(new_atominfo) == 1:
                for atom in self.atominfo:
                    for key in new_atominfo[0].keys():
                        atom[key] = new_atominfo[0][key]
            elif len(new_atominfo) == len(self.atominfo):
                for atom, new_atom in zip(self.atominfo, new_atominfo):
                    for key in new_atom:
                        atom[key] = new_atom[key]
            else:
                raise ValueError("The supplied atominfo for change mode has to either be of lenght 1 or of the length of atominfo")

            # check that all atoms have the same info
            ## Not implemented yet .. still needs to be done 
            # keys = [list(atom.keys()) for atom in self.atominfo]
            # comparison
            # for key in keys[1:]:
            #     if key 
        
        
    def change_parameter(self, key, value, mode = 'a'):
        """
        Function to change the paramters
        --> Input: a dictionary specifiying the new paramters you wish to change (except for atominfo there it is dependent on the mode chosen)
        --> Modes:
                    'a' - append - takes the original attribute of the class and changes only the keys supplied
                    'c' - change - replaces the old attribute dictionary completely with the one supplied
                    'r' - remove - removes the values of the keys supplied (the values of the dict don't matter)

        --> if atominfo is supplied it will call change_atominfo instead
        """
        def change_dictionary(old_dir, new_dir, mode= 'a'):
            output_dir = old_dir
            
            if mode == 'a':
                for key in new_dir.keys():
                    output_dir[key] = new_dir[key]
            
            if mode == 'c':
                output_dir = new_dir
            
            if mode == 'r':
                for key in new_dir.keys():
                    del output_dir[key]

            return output_dir

        if key == 'general':
            self.gen_parameters = change_dictionary(self.gen_parameters, value, mode)
        
        elif key == 'lattice':
            self.lattice = change_dictionary(self.lattice, value, mode)

        elif key == 'atominfo':  
            self.change_atominfo(value, mode)

        elif key == 'cluster':
            self.cluster = change_dictionary(self.cluster, value, mode)
        
        elif key == 'energy-contour':
            self.energy_contour = change_dictionary(self.energy_contour, value, mode)
    
        elif key == 'scf-cycle':
            self.scf_cyc = change_dictionary(self.scf_cyc, value, mode)

        elif key == 'voro-opts':
            self.voro_opts = change_dictionary(self.voro_opts, value, mode)
        
        else:
            raise KeyError(f'There is no Parameter associated with key: {key}')

    def get_parameter(self, key):  
        para_dict = {'general': self.gen_parameters,
         'lattice': self.lattice,
         'atominfo': self.atominfo,
         'cluster': self.cluster,
         'energy-contour': self.energy_contour,
         'scf-cycle':self.scf_cyc,
         'voro-opts': self.voro_opts}
        
        return para_dict[key]

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
        'atominfo': 
        [
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
            'REFPOT': 3
            }
        ]
    }

    inp = Inputcard(dict)

    # inp.add_runopt('asb')
    # inp.remove_runopt('asb')
    # print(inp.get_testopts())
    print(inp)
