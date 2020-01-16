#!/bin/bash
#SBATCH -J sho_GAN_hypertune_test
#SBATCH -p test
#SBATCH -n 20
#SBATCH --mem 4000 # Memory request (in MB)
#SBATCH -t 0-01:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python hypertune.py --ncpu 1 --fname sho_GAN_niters_test2.csv --gan
