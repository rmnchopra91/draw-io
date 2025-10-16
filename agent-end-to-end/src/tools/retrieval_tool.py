import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document


class RetrievalTool:
    def __init__(self, docs_dir: str = "data/docs"):
        self.docs_dir = docs_dir
        self.index = None

    def load_docs(self):
        """Load all text files in docs_dir."""
        docs = []
        for filename in os.listdir(self.docs_dir):
            if filename.endswith(".txt") or filename.endswith(".md"):
                path = os.path.join(self.docs_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    docs.append(Document(page_content=content, metadata={"source": filename}))
        return docs

    def build_index(self):
        """Create FAISS index with OpenAI embeddings."""
        docs = self.load_docs()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.index = FAISS.from_documents(chunks, embedding=embeddings)

    def retrieve(self, query: str, k: int = 3):
        if not self.index:
            self.build_index()
        results = self.index.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
