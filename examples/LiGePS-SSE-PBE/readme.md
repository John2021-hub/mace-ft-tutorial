# Example 1 – Fine-Tuning of LiGePS-SSE-PBE

This repository contains the **first example** from our tutorial paper.

## Contents

- A script for **fine-tuning foundation models** on your target dataset.
- A script for **computing the Generalized Stacking Fault Energy (GSFE)**.
**Original Data**  
   - `data.init`: Initial DeepMD format dataset  
   - `iter.000000`, `iter.000001`: DeepMD format iteration files  

**Conversion Tools**  
   - `deepmd2mace.py`: Script to convert DeepMD → MACE `extxyz` format using dpdata 

**Generated Files**  
   - `total_mace.xyz`: Combined MACE format dataset.  
   - `mace_train.xyz` (90%): Training dataset  
   - `mace_test.xyz` (10%): Validation dataset  
   - Note: Due to file size restrictions, the full dataset is hosted externally. Please download it via the provided link:https://drive.google.com/drive/folders/1ShwL7qdrCu4NkhkWCL9zHn_pntKr0W54?usp=sharing
## Usage

Please refer to the comments in each script for instructions on how to run them.  
Make sure all required dependencies are installed before running the scripts.

## Notes

This example demonstrates how to adapt pretrained models to specific tasks and how to evaluate material properties using machine-learned interatomic potentials.


