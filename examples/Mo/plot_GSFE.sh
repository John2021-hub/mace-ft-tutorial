#!/bin/bash

MODEL_PATH=/home/coder/project/run_jerry_al/results/Amir_Mo-17Jan1120-3/Amir_Mo-17Jan1120-3_run-3_stagetwo.model
SURFACE_TYPE=110 # 110 or 121
OUTPUT_FILE=/home/coder/project/run_jerry_al/results/Amir_Mo-17Jan1120-3/gsfe_ft_medium_${SURFACE_TYPE}_noucf.png

# Run the Python script
python /home/coder/project/mylib/Amir_Mo/plot_GSFE.py --model_path "$MODEL_PATH" --output_path "$OUTPUT_FILE" --surface_type "$SURFACE_TYPE"
