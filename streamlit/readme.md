# Run Ollama in Docker

```shell
docker run -d -v ollama:/root/.ollama -p 11434:11434 --memory=8G --name ollama ollama/ollama
```

To Check the memory used by the container see:

```shell
docker container stats <containerID>
```

Next, pull mistral:

```shell
docker exec -it ollama ollama pull mistral
```

# Run the app:

```shell
streamlit run ./streamlit/app.py
```