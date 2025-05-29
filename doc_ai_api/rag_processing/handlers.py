import os
import shutil
import traceback
import gradio as gr

from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from multifunctional_doc_ai import config
from core import models, utils
from rag_processing import graph as rag_graph_module

vectorstore_qgen = None
retriever_qgen = None

_last_processed_rag_files_checksum = None


def calculate_files_checksum(file_list):
    if not file_list:
        return None
    file_names = sorted([os.path.basename(f.name) for f in file_list])
    return hash(tuple(file_names))


def process_uploaded_files_rag(file_list):
    global _last_processed_rag_files_checksum

    rag_disabled_inputs_state = (
        gr.Textbox(interactive=False, placeholder="Upload and process files first."),
        gr.Button(interactive=False),
    )

    if not (models.llm and models.embeddings and rag_graph_module.rag_graph_compiled):
        status_message = "Error: Core models or RAG workflow failed to initialize. Cannot process. Check server logs."
        print(status_message)
        return status_message, [], *rag_disabled_inputs_state

    if not file_list:
        return "Please upload one or more text files.", [], *rag_disabled_inputs_state

    current_files_checksum = calculate_files_checksum(file_list)

    if (
        rag_graph_module.retriever_rag is not None
        and current_files_checksum == _last_processed_rag_files_checksum
    ):
        status_message = "Documents already processed. Ready for use!"
        rag_enabled_inputs_state = (
            gr.update(interactive=True, placeholder="Enter your question here..."),
            gr.update(interactive=True),
        )
        print(status_message)
        return status_message, [], *rag_enabled_inputs_state

    all_chunks = []
    processed_file_names = []
    print(f"\n--- RAG: Processing {len(file_list)} file(s) ---")
    try:
        for i, file_obj in enumerate(file_list):
            file_path = file_obj.name
            file_name = os.path.basename(file_path)
            processed_file_names.append(file_name)
            print(f"RAG: Processing file {i+1}/{len(file_list)}: {file_name}")

            with open(file_path, "r", encoding="utf-8") as f:
                document_content = f.read()
            cleaned_content = utils.clean_text(document_content)
            docs = [
                Document(page_content=chunk, metadata={"source": file_name})
                for chunk in RecursiveCharacterTextSplitter(
                    chunk_size=800, chunk_overlap=100
                ).split_text(cleaned_content)
            ]
            all_chunks.extend(docs)
            print(f"RAG: Chunked '{file_name}' into {len(docs)} chunks.")

        if not all_chunks:
            return (
                "Error: Uploaded documents resulted in no valid chunks. Please check content.",
                [],
                *rag_disabled_inputs_state,
            )

        print(f"RAG: Total chunks from all files: {len(all_chunks)}.")

        if os.path.exists(config.CHROMA_DB_DIR_RAG):
            try:
                import time

                time.sleep(0.1)
                shutil.rmtree(config.CHROMA_DB_DIR_RAG)
                print(f"RAG: Cleaned up old ChromaDB: {config.CHROMA_DB_DIR_RAG}")
                time.sleep(0.1)
            except Exception as e:
                print(
                    f"RAG: WARNING: Could not remove old ChromaDB: {e}. Attempting to proceed anyway."
                )

        if models.embeddings is None:
            return (
                "Error: Embedding model failed. Cannot create vector store.",
                [],
                *rag_disabled_inputs_state,
            )

        vectorstore_rag = Chroma.from_documents(
            documents=all_chunks,
            embedding=models.embeddings,
            persist_directory=config.CHROMA_DB_DIR_RAG,
        )
        rag_graph_module.retriever_rag = vectorstore_rag.as_retriever(
            search_kwargs={"k": 5}
        )
        print("RAG: Retriever created and set in RAG graph module.")

        _last_processed_rag_files_checksum = current_files_checksum

        status_message = f"RAG: Successfully processed {len(processed_file_names)} file(s): {', '.join(processed_file_names)}. Ready!"
        rag_enabled_inputs_state = (
            gr.update(interactive=True, placeholder="Enter your question here..."),
            gr.update(interactive=True),
        )
        return status_message, [], *rag_enabled_inputs_state

    except Exception as e:
        status_message = f"RAG: Error processing files: {e}\n{traceback.format_exc()}"
        print(status_message)
        rag_graph_module.retriever_rag = None
        return status_message, [], *rag_disabled_inputs_state


def answer_question_rag(question, chat_history):
    if rag_graph_module.rag_graph_compiled is None or models.llm is None:
        response = "Document(s) not processed or core models not configured. Upload files first. Check server logs for initialization errors."
        print(f"RAG: {response}")
        return chat_history + [{"role": "assistant", "content": response}], ""

    if not question.strip():
        response = "Please enter a question."
        return chat_history + [{"role": "assistant", "content": response}], ""

    print(f"\n--- RAG: Answering question: '{question}' ---")
    try:
        inputs = {
            "question": question,
            "query_rewrite_attempted": False,
            "attempt_count": 0,
            "documents": [],
            "summarized_context": None,
            "relevance_grade": "unknown",
            "query_classification": "unknown",
            "generation": None,
            "critique_status": "none",
        }
        final_state = rag_graph_module.rag_graph_compiled.invoke(inputs)
        response = final_state.get("generation", "Could not generate an answer.")
    except Exception as e:
        response = f"An error occurred: {e}\n{traceback.format_exc()}"
        print(f"RAG: Error during question answering: {e}")

    print("RAG: Question answering flow completed.")
    return chat_history + [{"role": "assistant", "content": response}], ""
