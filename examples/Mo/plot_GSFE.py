import argparse
import warnings
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from ase import Atoms
from ase.io import read
from ase.constraints import FixAtoms, UnitCellFilter
from ase.optimize.sciopt import SciPyFminCG
from ase.lattice.cubic import BodyCenteredCubic as bcc
from mace.calculators import MACECalculator
from ase.optimize import LBFGS, FIRE

def view_structure(atoms, atom_size=0.6, bond_thickness=0.1):
    import nglview as nv
    view_widget = nv.show_ase(atoms)
    view_widget.clear_representations()
    view_widget.add_representation('ball+stick', radius=atom_size, stick_radius=bond_thickness)
    view_widget.add_representation('unitcell', color='black')
    return view_widget

def get_gsf_structures(super_cell, b, gsfe_resolution=13):
    shift_inc = b / gsfe_resolution
    lattice_vectors = super_cell.get_cell()
    gsf_structures = [Atoms(super_cell)]
    
    for i in range(1, gsfe_resolution + 1):
        lattice_vectors[2] += np.array([0, shift_inc, 0])
        gsf_atoms = Atoms(
            symbols=super_cell.get_chemical_symbols(),
            positions=super_cell.get_positions(),
            cell=lattice_vectors,
            pbc=super_cell.get_pbc()
        )
        gsf_structures.append(gsf_atoms)
    
    return gsf_structures

def GSFE(super_cell, energies, gsf_structures):
    xdim = super_cell.get_cell()[0][0]
    ydim = super_cell.get_cell()[1][1]
    S = xdim * ydim
    gsfe = (np.array(energies) - energies[0]) / S * 16.022
    x = [stru.get_cell()[2][1] for stru in gsf_structures]
    x = x / x[-1]
    return gsfe, x

def main():
    parser = argparse.ArgumentParser(description='GSFE calculation using MACE')
    parser.add_argument('--model_path', type=str, required=True, help='Path to MACE model')
    parser.add_argument('--use_ucf', default=False, action="store_true", help='Path to MACE model')
    parser.add_argument('--output_path', type=str, required=True, help='Output path for the GFSE figure')
    parser.add_argument('--surface_type', type=str, required=True, help='Output path for the GFSE figure')
    
    args = parser.parse_args()
    
    warnings.filterwarnings("ignore")
    if args.surface_type == "110":
        super_cell = bcc(directions=[[1,-2,1], [1,1,1], [-1,0,1]],
                      size=(1,1,10), symbol='Mo', pbc=(1,1,1),
                      latticeconstant=3.16)
    elif args.surface_type =="121":
        super_cell = bcc(directions=[[-1,0,1], [1,1,1], [1,-2,1]],
                      size=(1,1,10), symbol='Mo', pbc=(1,1,1),
                      latticeconstant=3.16)
        
    lc = 3.16
    b = (lc / 2) * sqrt(3)
    
    gsf_structures = get_gsf_structures(super_cell, b)
    
    mace_calc = MACECalculator(model_paths=[args.model_path], device='cuda:0', default_dtype="float64")
    
    energies = []
    for atoms in gsf_structures:
        atoms.set_calculator(mace_calc)
        constraint = FixAtoms(mask=[atom.position[0] == atom.position[0] and atom.position[1] == atom.position[1] for atom in atoms])
        atoms.set_constraint(constraint)
        if args.use_ucf:
            ucf = UnitCellFilter(atoms)
            optimizer = SciPyFminCG(ucf)
        else:
            optimizer = SciPyFminCG(atoms)        
        optimizer.run(fmax=0.0005)
        energies.append(atoms.get_total_energy())
    
    gsfe, x = GSFE(super_cell, energies, gsf_structures)
    
    
    # Reference data
    reference_data = {
        "121": [0, 0.221139833556484, 0.735393384708885, 1.20993167795083, 1.46581764121049, 1.50960183714045, 1.41185824983712, 1.25573715981607, 1.02978782014436
                ,0.662387301585089,0.212737761584638,-0.004251363260626 ],
        "110":  [0, 0.182939718897349 ,0.60310681875523 ,1.02832984664399 ,1.32198262278198 ,1.47287619618024 ,1.47404915173445
                ,1.32382824839329 ,1.02987595922794 ,0.603310779721223 ,0.183697141264471 ,0.002640487108605]
                }
    
    x_dft = [0, 0.090909090909091, 0.181818181818182, 0.272727272727273, 0.363636363636364, 0.454545454545455, 0.545454545454545
            ,0.636363636363636, 0.727272727272727, 0.818181818181818, 0.909090909090909, 1]
    # Define line styles
    line_styles = {
        "mace": {"color": "blue", "linestyle": "-", "linewidth": 2.5, "marker": "o", "markersize": 4},
        "dft": {"color": "black", "linestyle": "-", "linewidth": 2.5, "marker": "d", "markersize": 4},
    }
    # Plot GSFE curve
    plt.figure(figsize=(6, 4))
    plt.plot(x, gsfe, label="MACE", **line_styles["mace"])
    plt.plot(x_dft, reference_data[args.surface_type], label="DFT", **line_styles["dft"])

    plt.xlabel("Normalized Path", fontsize=12)
    plt.ylabel("GSFE (J/m²)", fontsize=12)
    plt.title("Generalized Stacking Fault Energy", fontsize=14)
    plt.legend(fontsize=10, loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(args.output_path)
    print(f"plot saved at {args.output_path}")
    
if __name__ == "__main__":
    main()
