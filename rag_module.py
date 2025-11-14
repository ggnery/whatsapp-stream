import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

# Usar HuggingFaceEmbeddings da nova versão
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

# LCEL (substitui 'chains')
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


class RAGLocal:
    def __init__(self, pdf_name: str, pdf_path: str, silent_mode: bool = True):
        """
        Args:
            pdf_name: Name identifier for the PDF (used for index naming)
            pdf_path: Full path to the PDF file
            silent_mode: If True, skip interactive prompts (default: True)
        """
        self.pdf_name = pdf_name
        self.pdf_path = pdf_path
        self.silent_mode = silent_mode

        # Paths locais - tudo dentro de whatsapp-stream/
        self.indexes_dir = os.path.join(os.path.dirname(__file__), "indexes")
        os.makedirs(self.indexes_dir, exist_ok=True)

        # Embeddings Qwen3
        self.embeddings = HuggingFaceEmbeddings(
            model_name="Qwen/Qwen3-Embedding-0.6B",
            encode_kwargs={"normalize_embeddings": True},
            # model_kwargs={"device": "cuda"}  # opcional se tiver GPU
        )

        # LLM (garante PT-BR via prompt)
        self.llm = ChatOpenAI(model="gpt-4o-mini")  # ou outro modelo de LLM

        self.vectorstore = None
        self.rag_chain = None

    def create_index(self):
        """Create FAISS index from PDF."""
        index_path = os.path.join(self.indexes_dir, f"faiss_{self.pdf_name}")

        if os.path.exists(index_path):
            if not self.silent_mode:
                should_create = input(
                    "Index já existe. Recriar? (y/n): ") == "y"
                if not should_create:
                    return
            else:
                print(f"Index {self.pdf_name} já existe. Pulando criação.")
                return

        print(f"Criando índice para {self.pdf_name}...")
        docs = PyPDFLoader(self.pdf_path).load()
        docs = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=30, separator="\n"
        ).split_documents(docs)

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.vectorstore.save_local(index_path)
        print(f"Índice {self.pdf_name} criado com sucesso.")

    def load_index(self):
        """Load existing FAISS index and setup RAG chain. Creates index if it doesn't exist."""
        index_path = os.path.join(self.indexes_dir, f"faiss_{self.pdf_name}")

        # Se o índice não existe, criar automaticamente
        if not os.path.exists(index_path):
            print(f"⚠ Índice não encontrado em {index_path}")
            print(f"→ Criando índice automaticamente...")
            self.create_index()

        print(f"Carregando índice {self.pdf_name}...")
        self.vectorstore = FAISS.load_local(
            index_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        retriever = self.vectorstore.as_retriever()

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Você é um assistente que responde SEMPRE em português do Brasil, de forma direta e objetiva. "
             "Responda usando somente o contexto recuperado; se não souber, diga que não encontrou a informação e solicite melhorar a pergunta."),
            ("human", "Pergunta: {input}\n\nContexto:\n{context}")
        ])

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        # LCEL pipeline: retriever -> prompt -> llm -> string
        self.rag_chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print(f"Índice {self.pdf_name} carregado com sucesso.")

    def ask_question(self, question: str):
        """
        Returns:
            dict with 'answer' key containing the response
        Raises:
            RuntimeError: If load_index() hasn't been called yet
        """
        if not self.rag_chain:
            raise RuntimeError("Chamou ask_question antes de load_index()")

        answer = self.rag_chain.invoke(question)
        return {"answer": answer}
