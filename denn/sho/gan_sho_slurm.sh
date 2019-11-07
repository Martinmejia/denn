#!/bin/bash
#SBATCH -J gan_sho_experiment
#SBATCH -p shared
#SBATCH -n 32
#SBATCH --mem 12000 # Memory request (12Gb)
#SBATCH -t 0-24:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python gan_sho_experiment.py
