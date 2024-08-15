# Run Ollama in Docker

```shell
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

Next, pull mistral:

```shell
docker exec -it ollama ollama pull mistral
```

# Run the app:

```shell
streamlit run ./streamlit/app.py
```