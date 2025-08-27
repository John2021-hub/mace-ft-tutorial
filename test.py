
# # installation
# module avail cuda
# conda activate mace
# pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu12
# cd mace
# pip install .

# use
from ase import build
from mace.calculators import MACECalculator

mace_calc = MACECalculator(model_paths="/scratch/projects/CFP01/CFP01-CF-069/mace-ft-tutorial/models/mace-mp-0b3-medium.model", enable_cueq=True, device="cuda")

atoms = build.molecule('H2O')
atoms.calc = mace_calc
atoms.get_forces()