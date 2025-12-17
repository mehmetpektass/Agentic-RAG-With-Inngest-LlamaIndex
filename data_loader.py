from groq import Groq
from dotenv import load_dotenv
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()

client = Groq()
EMBED_MODEL = "nomic-embed-text-v1_5"

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_pdf(path:str):
    docs = PDFReader().load_data(file=path)
    text = [i.text for i in docs if getattr(i, "text", None)]
    chunks = []
    for t in text:
        chunks.extend(splitter.split_text(t))
    return chunks


    