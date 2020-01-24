#!/bin/bash
#SBATCH -J nlo_L2_hypertune
#SBATCH -p shared
#SBATCH -n 20
#SBATCH -N 1
#SBATCH --mem 10000 # Memory request (in MB)
#SBATCH -t 0-20:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python hypertune.py --fname nlo_L2_niters_expdecay.csv
