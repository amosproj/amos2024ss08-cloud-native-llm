#!/bin/bash -l
#SBATCH --job-name=christian
#SBATCH --ntasks=1
#SBATCH --gres=gpu:a100:1 -p a100
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH --mail-type=end,fail 
#SBATCH --time=01:15:00
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
cp -r ${SLURM_SUBMIT_DIR}/benchmark_prometheus.py .
cp -r ${SLURM_SUBMIT_DIR}/cncf_results.csv .
cp -r ${SLURM_SUBMIT_DIR}/gemma_results.csv .
mkdir -p output/

(
  while true; do
    nvidia-smi > ${SLURM_SUBMIT_DIR}/gpu_usage_${SLURM_JOB_ID}.log
    sleep 60
  done
) &

# Run training script (with data copied to node)
python benchmark_prometheus.py

# Create a directory on $HOME and copy the results from our training
mkdir ${HOME}/$SLURM_JOB_ID
cp -r output ${HOME}/$SLURM_JOB_ID

