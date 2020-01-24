#!/bin/bash
#SBATCH -J nlo_gan
#SBATCH -p test
#SBATCH -n 1
#SBATCH --mem 1000 # Memory request (in MB)
#SBATCH -t 0-04:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python experiments.py --pkey nlo --gan --fname gan_nlo_50k_exp09999_D64by16_G64by12.png
