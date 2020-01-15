#!/bin/bash
#SBATCH -J nlo_L2_hypertune
#SBATCH -p shared
#SBATCH -n 6
#SBATCH --mem 6000 # Memory request (in MB)
#SBATCH -t 0-48:00 # Maximum execution time (D-HH:MM)
#SBATCH -o logs.out # Standard output
#SBATCH -e logs.err # Standard error
module load Anaconda3/5.0.1-fasrc01
source activate denn
python hypertune.py --ncpu 6 --fname nlo_L2_niters_5reps.csv
