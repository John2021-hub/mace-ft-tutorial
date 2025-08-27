#!/bin/bash
#SBTACH -p cpu-5218
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40

module load lammps/28Mar2023

lmp -k on g 1 -sf kk -in mace-lmp.in  
