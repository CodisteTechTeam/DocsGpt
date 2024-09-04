import os
import uuid
import shutil
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from utils import log_message, download_file, create_response
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain


###--------------------------------------------------------------------------###


llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4-1106-preview", temperature=0.3
)


###--------------------------------------------------------------------------###


def docs_embeddings(parameters):
    """Load text from a document URL."""
    required_params = ["docs_url"]
    if any(param not in parameters for param in required_params):
        return create_response(False, "Required parameters missing", {}, 400)

    batch_id = str(uuid.uuid4())
    output_dir = os.path.join("temp", batch_id)
    os.makedirs(output_dir, exist_ok=True)
    try:
        document_url = parameters.get("docs_url")
        log_message(f"Loading text from document: {document_url}", "info")
        doc_file = download_file(document_url, output_dir)
        if not doc_file.endswith(".pdf") and not doc_file.endswith(".docx"):
            return create_response(
                False,
                "Invalid document format, Supported formats are PDF and DOCX.",
                {},
                400,
            )

        if doc_file.endswith(".pdf"):
            pdf_loader = PyPDFLoader(doc_file)
            pages = pdf_loader.load_and_split()
        else:
            docx_loader = Docx2txtLoader(doc_file)
            pages = docx_loader.load_and_split()

        log_message("Text loaded from existing file", "debug")

        text_documents = [page for page in pages]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=0, separators=["\n\n", "\n"]
        )
        text_document_chunks = text_splitter.split_documents(text_documents)
        vector_store = Chroma.from_documents(
            text_document_chunks,
            OpenAIEmbeddings(model="text-embedding-ada-002"),
            persist_directory=f"rag_vector_db/{batch_id}_rag_vectors",
        )

        log_message(
            f"Embeddings generated and saved to vector store for {document_url}",
            "debug",
        )

        return create_response(
            True,
            "Embeddings generated successfully",
            {"document_url": document_url, "batch_id": batch_id},
            200,
        )
    except Exception as e:
        log_message(f"Error loading text: {e}", "error")
        return create_response(False, "An error occurred", {"error": e}, 500)
    finally:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


###--------------------------------------------------------------------------###


def get_context_retriever_chain(vector_store):
    """Create a retriever chain with context-aware retriever."""

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation",
            ),
        ]
    )

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain


###--------------------------------------------------------------------------###


def get_conversational_rag_chain(retriever_chain):
    """Create a retrieval chain for conversational RAG."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a PDF And DOCX content expert. Use the following instructions to guide your responses:

                    1. **Answer from provided context:**
                        - First check the context to see if an answer is available for question.
                        - If the answer is found in the provided context, provide the answer directly from that context.
                        - Make sure to generate small answer and it contains all the information user needed. Do not generate lengthy answer.

                    2. **Maintain Conversational Flow:**
                        - Ensure that the conversation is seamless and visually connected, mimicking a natural human interaction.

                    3. **Follow this formating rule to format the response**
                        - Do not mention answer types ["Answer from provided context", "Handle Questions Whom answer is not found in provided context", "Maintain Conversational Flow", "Follow this formating rule to format the response"] in the resposne.

                    Note:
                    ** If data is not available in the provided context, you can say "I don't have that information, would you like me to look it up for you?" and then use the search query generated by the user to look up the information.

                    \n\ncontext:\n\n{context}""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


###--------------------------------------------------------------------------###


def chat(parameters):
    required_params = ["query", "batch_id"]
    if any(param not in parameters for param in required_params):
        return create_response(False, "Required parameters missing", {}, 400)

    try:
        question = parameters.get("query")
        batch_id = parameters.get("batch_id")
        chat_history = parameters.get("chat_history", [])
        log_message(f"Processing question: {question}", "info")
        retriever = Chroma(
            persist_directory=f"rag_vector_db/{batch_id}_rag_vectors",
            embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
        )
        retriever_chain = get_context_retriever_chain(retriever)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

        response = conversation_rag_chain.invoke(
            {"chat_history": chat_history, "input": question}
        )

        log_message(f"Response generated: {response['answer']}", "info")

        return create_response(True, "Success", response["answer"], 200)
    except Exception as e:
        log_message(f"Error loading text: {e}", "error")
        return create_response(False, "An error occurred", {"error": e}, 500)
