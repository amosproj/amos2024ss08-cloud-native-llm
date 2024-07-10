
## install NVIDIA Container Toolkit
# source: https://www.server-world.info/en/note?os=Ubuntu_22.04&p=nvidia&f=2
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
# result: OK
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu22.04/nvidia-docker.list > /etc/apt/sources.list.d/nvidia-docker.list
apt update
apt -y install nvidia-container-toolkit
systemctl restart docker
docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi # checks if NVIDIA Container Toolkit is installed


docker run -it --gpus all nvidia/cuda:12.5.0-base-ubuntu22.04 bash
docker run -p 8080:8080  --gpus all  --name local-ai  -ti localai/localai:latest-aio-gpu-nvidia-cuda-12

docker run -p 8080:8080 --gpus all --env-file .env localai/localai:v2.18.1-cublas-cuda12-ffmpeg-core https://raw.githubusercontent.com/amosproj/amos2024ss08-cloud-native-llm/110-implement-the-chat-bot-user-interface/src/scripts/GUI/model_configuration.yaml

# Run localai with model config from gist

docker run -p 8080:8080 --gpus all --env-file .env localai/localai:v2.18.1-cublas-cuda12-ffmpeg-core https://gist.githubusercontent.com/anosh-ar/91658012cccb8f74abb72ddc78bb71c8/raw/e00cca94739213ebf83e9074e3e9e3f74e55d7fb/model_config.yaml
