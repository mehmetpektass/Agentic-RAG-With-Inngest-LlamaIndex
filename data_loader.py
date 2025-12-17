from dotenv import load_dotenv
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
import cohere
import os

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path:str):
    docs = PDFReader().load_data(file=path)
    text = [i.text for i in docs if getattr(i, "text", None)]
    chunks = []
    for t in text:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_text(texts: list[str]) -> list[list[float]]:
    response = co.embed(
        texts=texts,
        model="embed-multilingual-v3.0",
        input_type="search_document"
    )
    return response.embeddings
    