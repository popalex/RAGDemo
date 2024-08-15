# Workaround for sqlite version to low in ChromaDB !
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from flask import Flask, request, jsonify, render_template
from pypdf import PdfReader
import chromadb

app = Flask(__name__)



# ChromaDB client
# client = chromadb.Client(host="localhost", port=8080)
# client = chromadb.Client()
client = chromadb.PersistentClient(path="./db/chromadb")
collection = client.get_or_create_collection(name="rag_collection")

# Index endpoint
@app.route("/index", methods=["POST"])
def index_pdf():
    # Get the uploaded PDF file
    file = request.files["file"]
    pdf_file = PdfReader(file)

    # Extract text from the PDF file
    text = ""
    for page in pdf_file.pages:
        text = page.extract_text()
        collection.upsert(
            documents=[
                text
            ],
            ids=[f"file:{file.filename},page:{page.page_number}"]
        )
        print(f"Indexing file:{file.filename},page:{page.page_number}")

    print(f"Done indexing {file.filename}")
    # Index the text using ChromaDB
    # client.index(text, {"filename": file.filename})
    

    return jsonify({"message": "PDF file indexed successfully"})

# Search endpoint
@app.route("/search", methods=["GET"])
def search_phrase(phrase):
    # Get the search phrase from the query parameter
    # phrase = request.args.get("phrase")

    # Search for the phrase using ChromaDB
    # results = client.search(phrase)
    results = collection.query(
        query_texts=[phrase], # Chroma will embed this for you
        n_results=10 # how many results to return
    )

    # Return the search results as a JSON response
    return jsonify({"results": results})

# Upload HTML page
@app.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")

# Search HTML page
@app.route("/search_page", methods=["GET"])
def search_page():
    return render_template("search.html")

# Handle file upload
@app.route("/upload_file", methods=["POST"])
def upload_file():
    file = request.files["file"]
    return index_pdf()

# Handle search query
@app.route("/search_query", methods=["POST"])
def search_query():
    phrase = request.form["phrase"]
    return search_phrase(phrase)

if __name__ == "__main__":
    app.run(debug=True)