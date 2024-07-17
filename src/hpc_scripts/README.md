These script were deigned to be run 


# Executing the qa generation:

To execute the qa generation you need to be logged in to the HPC and need to setup a Python environment with the name amos_env. This should include all libraries from the requirements.txt.

Then you need to setup your HF_Token either in an environment file or in the script.

Then copy the necessary training files to HPC and run 

`sbatch  gpu_job_multi.sbatch`

to run the qa generation on multiple gpus.
