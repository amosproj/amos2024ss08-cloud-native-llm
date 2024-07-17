# pull the local-ai image from docker hub and run it
# model configuration is stored in github gist file. It can be edited with your needs 
# deploying DeepCNCF using CPU
docker run -p 8080:8080 localai/localai:v2.18.1-ffmpeg-core https://gist.githubusercontent.com/anosh-ar/91658012cccb8f74abb72ddc78bb71c8/raw/5124bde0f59b4c499f9fc0ecdf8ed4ecae7f797a/model_config.yaml

#optional: deploying DeepCNCF using GPU
## install NVIDIA Container Toolkit in case you want to use GPU to inference
# source: https://www.server-world.info/en/note?os=Ubuntu_22.04&p=nvidia&f=2
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
# result: OK
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu22.04/nvidia-docker.list > /etc/apt/sources.list.d/nvidia-docker.list
apt update
apt -y install nvidia-container-toolkit
systemctl restart docker
docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi # checks if NVIDIA Container Toolkit is installed
# pull the local-ai image from docker hub and run it
# model configuration is stored in github gist file. It can be edited with your needs 
docker run -p 8080:8080 --gpus all localai/localai:v2.18.1-cublas-cuda12-ffmpeg-core https://gist.githubusercontent.com/anosh-ar/91658012cccb8f74abb72ddc78bb71c8/raw/e00cca94739213ebf83e9074e3e9e3f74e55d7fb/model_config.yaml
