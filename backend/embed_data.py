import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

def embed_json(input_file, output_folder):
    with open(input_file, "r") as f:
        data = json.load(f)

    text = "\n".join([p["content"] for p in data])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    print(f"🔹 Splitting into {len(chunks)} chunks...")

    embeddings = OpenAIEmbeddings()
    Chroma.from_texts(chunks, embeddings, persist_directory=output_folder)
    print(f"✅ Embedded {len(chunks)} chunks into {output_folder}")

embed_json("data/as3000.json", "embeddings/as3000_db")
