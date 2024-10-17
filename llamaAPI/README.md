# Server setup

https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md

```
sudo docker run -p 8880:8880 -v /home/ender/Models_AI:/Models_AI --gpus all ghcr.io/ggerganov/llama.cpp:server-cuda -m /Models_AI/Llama-3.2-3B-Instruct-f16.gguf -c 2048 --host 0.0.0.0 --port 8880 --n-gpu-layers 120
```

# API Calls

```
curl --request POST --url https://api.enderphan.info/completion --header "Content-Type: application/json" --user 'admin:password' --data '{"prompt": "Building a website can be done in 10 simple steps:","n_predict": 128}'
```

# As Service

```
sudo docker run -p --name=llamaapi 8880:8880 -v /home/ender/Models_AI:/Models_AI --gpus all ghcr.io/ggerganov/llama.cpp:server-cuda -m /Models_AI/Llama-3.2-3B-Instruct-f16.gguf -c 2048 --host 0.0.0.0 --port 8880 --n-gpu-layers 120

```

```
vim /etc/systemd/system/docker-llamaapi.service
```

```
[Unit]
Description=LlamaApi container
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a llamaapi
ExecStop=/usr/bin/docker stop -t 2 llamaapi

[Install]
WantedBy=default.target 
```

```
sudo systemctl enable docker-llamaapi.service
```