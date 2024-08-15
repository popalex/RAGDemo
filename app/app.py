from flask import Flask, request, jsonify, render_template
from chromadb import Client
from pypdf import PdfFileReader

app = Flask(__name__)

# ChromaDB client
# client = Client(host="localhost", port=8080)
client = chromadb.Client()

# Index endpoint
@app.route("/index", methods=["POST"])
def index_pdf():
    # Get the uploaded PDF file
    file = request.files["file"]
    pdf_file = PdfFileReader(file)

    # Extract text from the PDF file
    text = ""
    for page in pdf_file.pages:
        text += page.extractText()

    # Index the text using ChromaDB
    client.index(text, {"filename": file.filename})

    return jsonify({"message": "PDF file indexed successfully"})

# Search endpoint
@app.route("/search", methods=["GET"])
def search_phrase():
    # Get the search phrase from the query parameter
    phrase = request.args.get("phrase")

    # Search for the phrase using ChromaDB
    results = client.search(phrase)

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
    return search_phrase()

if __name__ == "__main__":
    app.run(debug=True)