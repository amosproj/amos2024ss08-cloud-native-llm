#!/bin/bash -l
#SBATCH --job-name=christian
#SBATCH --ntasks=1
#SBATCH --gres=gpu:rtx2080ti:4
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH --mail-type=end,fail 
#SBATCH --time=24:00:00
#SBATCH --export=NONE
unset SLURM_EXPORT_ENV

# Set proxy to access internet from the node
export http_proxy=http://proxy:80
export https_proxy=http://proxy:80

module purge
module load python
module load cuda
module load cudnn

# Conda
conda activate amos_env # replace with the name of your conda env

# Copy data to `$TMPDIR` to have faster access, recommended esp. for long trainings
#cp -r "/home/janus/iwb6-datasets/FRAGMENTS" "$TMPDIR"
# in case you have to extract an archive, e.g. a dataset use:
cd "$TMPDIR"

# create a temporary job dir on $WORK
mkdir ${WORK}/$SLURM_JOB_ID

# copy input file from location where job was submitted, and run 
cp -r ${SLURM_SUBMIT_DIR}/benchmark_results_gemma.py .
mkdir -p output/

# Run training script (with data copied to node)
torchrun benchmark_results_gemma.py 

# Create a directory on $HOME and copy the results from our training
mkdir ${HOME}/$SLURM_JOB_ID
cp -r output ${HOME}/$SLURM_JOB_ID

