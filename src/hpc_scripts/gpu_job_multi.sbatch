#!/bin/bash -l
#SBATCH --job-name=amos_qa_generation
#SBATCH --ntasks=1
#SBATCH --gres=gpu:rtx2080ti:4
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH --mail-type=end,fail 
#SBATCH --time=20:00:00
#SBATCH --export=NONE
unset SLURM_EXPORT_ENV
echo "Exported Slurm env"

# Set proxy to access internet from the node
export http_proxy=http://proxy:80
export https_proxy=http://proxy:80
echo "Set proxy to access internet from the node"

module purge
module load python
module load cuda
module load cudnn

# Conda
conda activate amos_env # replace with the name of your conda env
echo "activated conda env"

cd "$TMPDIR"
echo "created tmp"

# copy input file from location where job was submitted, and run 
cp -r ${SLURM_SUBMIT_DIR}/qa_generation_multi_gpu.py .
echo "copied file"

#mkdir -p output/logs/
#mkdir -p output/checkpoints/
mkdir -p output/
echo "Create output"

torchrun qa_generation_multi_gpu.py 
echo "Run Torch"

# Create a directory on $HOME and copy the results from our training
mkdir ${HOME}/$SLURM_JOB_ID
cp -r output ${HOME}/$SLURM_JOB_ID
echo "Job finished"

