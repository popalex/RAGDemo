# Workaround for sqlite version to low in ChromaDB !
__import__('pysqlite3')
import sys

import torch
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
# from langchain.vectorstores.utils import filter_complex_metadata
from langchain_community.vectorstores.utils import filter_complex_metadata


class ChatPDF:
    vector_store = None
    retriever = None
    chain = None

    def __init__(self):
        # self.model = ChatOllama(model="mistral", torch_dtype=torch.float16)
        self.model = ChatOllama(model="gemma2:2b")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context 
            to answer the question. If you don't know the answer, just say that you don't know. Use three sentences
             maximum and keep the answer concise. [/INST] </s> 
            [INST] Question: {question} 
            Context: {context} 
            Answer: [/INST]
            """
        )

    def ingest(self, pdf_file_path: str):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        vector_store = Chroma.from_documents(documents=chunks, 
                                             embedding=FastEmbedEmbeddings(),
                                             collection_name="rag_collection",
                                             persist_directory="./db/chromadb")
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())

    def ask(self, query: str):
        if not self.chain:
            # return "Please, add a PDF document first."
            vector_store = vector_store = Chroma(
                collection_name="rag_collection",
                embedding_function=FastEmbedEmbeddings(),
                persist_directory="./db/chromadb",  # Where to save data locally, remove if not neccesary
            )
            self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
                search_kwargs={
                    "k": 3,
                    "score_threshold": 0.5,
                },
            )

            self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                        | self.prompt
                        | self.model
                        | StrOutputParser())

        return self.chain.invoke(query)

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
