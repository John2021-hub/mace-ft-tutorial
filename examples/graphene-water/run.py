
# # installation
# module avail cuda
# conda activate mace
# pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu12
# cd mace
# pip install .

import os
import json
import time
from ase.io import read, write
from ase import units
from ase.io.trajectory import Trajectory
from ase.md.langevin import Langevin
from ase.optimize import LBFGS
from mace.calculators import MACECalculator

# two MACE models
mace_models = {
    "mace-ft": MACECalculator(model_paths="mace-ft-tutorial-main-3.model", enable_cueq=True, device="cuda"),
    "mace-mp-0b3": MACECalculator(model_paths="mace-ft-tutorial-main-3.model", enable_cueq=False, device="cuda")
}

# three configurations
config_files = {
    "graphene-128": "graphene-128.xyz",
    "graphene-372": "graphene-372.xyz",
    "graphene-1038": "graphene-1038.xyz"
}

Temp = 300
friction = 0.01
time_step = 1  # fs
steps = 10000
seed = "results"
timing_result = {}

# main loop
for mace_name, mace_calculator in mace_models.items():
    for config_name, config_file in config_files.items():
        print(f"Running MD for {config_name} with {mace_name}...")

        # path
        res_path = os.path.join(seed)
        if not os.path.exists(res_path):
            os.makedirs(res_path)
        traj_name_traj = os.path.join(res_path, f"{config_name}_{mace_name}_{Temp}_{steps}.traj")
        traj_name_xyz = os.path.join(res_path, f"{config_name}_{mace_name}_{Temp}_{steps}.xyz")

        # read configuration
        at = read(config_file)
        at.calc = mace_calculator

        # geometry optimization
        gr = LBFGS(atoms=at)
        gr.run(fmax=0.01, steps=100)

        # set up MD
        dyn = Langevin(at, time_step * units.fs, Temp * units.kB, friction)

        def printenergy(a=at):
            epot = a.get_potential_energy() / len(a)
            ekin = a.get_kinetic_energy() / len(a)
            print(f"Energy per atom: Epot = {epot:.3f} eV  Ekin = {ekin:.3f} eV "
                  f"(T = {ekin / (1.5 * units.kB):.0f} K)  Etot = {epot + ekin:.3f} eV")

        dyn.attach(printenergy, interval=100)
        traj = Trajectory(traj_name_traj, 'w', at)
        dyn.attach(traj.write, interval=100)

        # record time
        start_time = time.time()
        dyn.run(steps)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # write trajectory to xyz
        ats = read(traj_name_traj, index=":")
        write(traj_name_xyz, ats)

        # record timing result
        timing_result[f"{config_name}_{mace_name}"] = elapsed_time
        print(f"Finished {config_name} with {mace_name} in {elapsed_time:.2f} seconds.\n")

# save all timing to JSON file
json_file = os.path.join(seed, f"timing_results_{Temp}_{steps}.json")
with open(json_file, "w") as f:
    json.dump(timing_result, f, indent=2)

print("All simulations completed. Timing results saved to", json_file)

