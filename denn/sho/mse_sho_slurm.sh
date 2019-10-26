#!/bin/bash
#SBATCH -J mse_sho_experiment
#SBATCH -p shared
#SBATCH -n 10
#SBATCH -N 1
#SBATCH --mem 10000 # Memory request (10Gb)
#SBATCH -t 0-10:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python mse_sho_experiments.py
