import json
import os
import shutil
import traceback
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .core import models
from .core import utils
from .rag_processing import graph as rag_graph_module 

from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def handle_uploaded_files(uploaded_files):
    temp_dir = settings.PDF_TEMP_DIR
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_paths = []
    fs = FileSystemStorage(location=temp_dir)
    for file in uploaded_files:
        filename = file.name
        safe_filename = os.path.basename(filename)
        saved_path = fs.save(safe_filename, file)
        temp_file_paths.append(fs.path(saved_path))
    return temp_file_paths

def process_text_files_logic(file_paths):
    all_chunks = []
    processed_file_names = []
    print(f"\n--- Django API: Ingesting {len(file_paths)} file(s) into persistent DB ---")
    try:
        for file_path in file_paths:
             file_name = os.path.basename(file_path)
             processed_file_names.append(file_name)
             print(f"Django API: Ingesting file: {file_name}")

             with open(file_path, 'r', encoding='utf-8') as f:
                 document_content = f.read()
             cleaned_content = utils.clean_text(document_content)
             docs = [Document(page_content=chunk, metadata={"source": file_name})
                     for chunk in RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_text(cleaned_content)]
             all_chunks.extend(docs)
             print(f"Django API: Chunked '{file_name}' into {len(docs)} chunks.")

        if not all_chunks:
             raise Exception("Error: Uploaded documents resulted in no valid chunks for ingestion.")

        print(f"Django API: Total chunks for ingestion: {len(all_chunks)}.")

        if models.embeddings is None:
             raise Exception("Embedding model failed to initialize.")

        chroma_dir_rag = settings.CHROMA_DB_DIR_RAG
        pdf_temp_dir = settings.PDF_TEMP_DIR 

        try:
            if os.path.exists(chroma_dir_rag) and os.listdir(chroma_dir_rag): 
                print(f"Django API: Attempting graceful ChromaDB reset at {chroma_dir_rag}.")
                temp_chroma_client_rag = Chroma(
                    persist_directory=chroma_dir_rag,
                    embedding_function=models.embeddings
                )
                temp_chroma_client_rag.delete_collection(name=None) 
                temp_chroma_client_rag.reset() 
                print(f"Django API: Successfully reset ChromaDB at {chroma_dir_rag}.")
        except Exception as e:
            print(f"Django API: Warning: Graceful ChromaDB reset failed for {chroma_dir_rag}: {e}. Falling back to forceful deletion.")

        for db_dir in [chroma_dir_rag, pdf_temp_dir]: 
            if os.path.exists(db_dir):
                print(f"Django API: Deleting directory (force fallback): {db_dir}")
                try:
                    shutil.rmtree(db_dir)
                    print(f"Django API: Cleaned up {db_dir} using shutil.rmtree.")
                except Exception as e:
                    print(f"Django API: shutil.rmtree failed for {db_dir}: {e}. Attempting shell command.")
                    import time
                    time.sleep(0.5)
                    os.system(f'rm -rf "{db_dir}"')
                    print(f"Django API: Attempted force cleanup via shell for: {db_dir}.")
                    if os.path.exists(db_dir):
                        print(f"Django API: WARNING: Directory {db_dir} still exists after shell cleanup!")
                        raise PermissionError(f"Failed to clean directory: {db_dir}. Please delete manually.") from e

        os.makedirs(chroma_dir_rag, exist_ok=True)
        os.makedirs(pdf_temp_dir, exist_ok=True)

        print(f"Django API: Loading/Creating ChromaDB at: {chroma_dir_rag}")
        vectorstore_rag = Chroma(
            persist_directory=chroma_dir_rag,
            embedding_function=models.embeddings
        )

        print(f"Django API: Adding {len(all_chunks)} chunks to ChromaDB.")
        vectorstore_rag.add_documents(all_chunks)
        print(f"Django API: Documents added to ChromaDB.")

        rag_graph_module.retriever_rag = vectorstore_rag.as_retriever(search_kwargs={"k": 3})
        print("Django API: Retriever updated.")

        return f"Successfully ingested {len(processed_file_names)} file(s). Documents are ready!", processed_file_names

    except Exception as e:
        print(f"Django API: Error during document ingestion: {e}\n{traceback.format_exc()}")
        raise e


@csrf_exempt
def clear_documents_db(request):
    if request.method == 'POST':
        print("\n--- Django API: Clearing all document data ---")
        try:
            chroma_dir_rag = settings.CHROMA_DB_DIR_RAG
            
            if os.path.exists(chroma_dir_rag) and os.listdir(chroma_dir_rag):
                try:
                    temp_chroma_client = Chroma(persist_directory=chroma_dir_rag, embedding_function=models.embeddings)
                    temp_chroma_client.delete_collection(name=None)
                    temp_chroma_client.reset()
                    print(f"Django API: Gracefully reset ChromaDB at {chroma_dir_rag}.")
                except Exception as e:
                    print(f"Django API: Warning: Graceful reset failed for {chroma_dir_rag}: {e}. Falling back to forceful deletion.")
            
            for db_dir in [chroma_dir_rag, settings.PDF_TEMP_DIR, settings.MEDIA_ROOT]:
                if os.path.exists(db_dir):
                    try:
                        shutil.rmtree(db_dir)
                        print(f"Django API: Forcefully deleted {db_dir}.")
                    except Exception as e:
                        print(f"Django API: Error forcefully deleting {db_dir}: {e}. Try manual deletion if issue persists.")
                        return JsonResponse({'status': 'error', 'message': f'Failed to clear: {e}. Please delete {db_dir} manually.'}, status=500)
            
            os.makedirs(chroma_dir_rag, exist_ok=True)
            os.makedirs(settings.PDF_TEMP_DIR, exist_ok=True)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            rag_graph_module.retriever_rag = None
            print("Django API: All document data cleared and retriever reset.")
            return JsonResponse({'status': 'success', 'message': 'All documents and associated data cleared.'})
        except Exception as e:
            print(f"Django API: Error clearing documents DB: {e}\n{traceback.format_exc()}")
            return JsonResponse({'status': 'error', 'message': f'Failed to clear documents: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)



def ingest_documents_logic(file_paths):
    all_chunks = []
    processed_file_names = []
    print(f"\n--- Django API: Ingesting {len(file_paths)} file(s) into persistent DB ---")
    try:
        for file_path in file_paths:
             file_name = os.path.basename(file_path)
             processed_file_names.append(file_name)
             print(f"Django API: Ingesting file: {file_name}")

             with open(file_path, 'r', encoding='utf-8') as f:
                 document_content = f.read()
             cleaned_content = utils.clean_text(document_content)
             docs = [Document(page_content=chunk, metadata={"source": file_name})
                     for chunk in RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_text(cleaned_content)]
             all_chunks.extend(docs)
             print(f"Django API: Chunked '{file_name}' into {len(docs)} chunks.")

        if not all_chunks:
             raise Exception("Error: Uploaded documents resulted in no valid chunks for ingestion.")

        print(f"Django API: Total chunks for ingestion: {len(all_chunks)}.")

        
        if models.embeddings is None:
             raise Exception("Embedding model failed to initialize.")

        
        
        print(f"Django API: Loading/Creating ChromaDB at: {settings.CHROMA_DB_DIR_RAG}")
        vectorstore_rag = Chroma(
            persist_directory=settings.CHROMA_DB_DIR_RAG,
            embedding_function=models.embeddings 
        )

        
        print(f"Django API: Adding {len(all_chunks)} chunks to ChromaDB.")
        vectorstore_rag.add_documents(all_chunks)
        print(f"Django API: Documents added to ChromaDB.")

        
        rag_graph_module.retriever_rag = vectorstore_rag.as_retriever(search_kwargs={"k": 3})
        print("Django API: Retriever updated.")

        return f"Successfully ingested {len(processed_file_names)} file(s). Documents are ready!", processed_file_names

    except Exception as e:
        print(f"Django API: Error during document ingestion: {e}\n{traceback.format_exc()}")
        
        
        raise e


@csrf_exempt
def ingest_documents(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')
        if not uploaded_files:
            return JsonResponse({'status': 'error', 'message': 'No files uploaded.'}, status=400)

        temp_file_paths = handle_uploaded_files(uploaded_files)

        try:
            status_message, processed_file_names = ingest_documents_logic(temp_file_paths)
            return JsonResponse({'status': 'success', 'message': status_message, 'processed_files': processed_file_names})
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': f'Ingestion failed: {e}'}, status=500)
        finally:
            for path in temp_file_paths:
                if os.path.exists(path):
                    os.remove(path)

    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@csrf_exempt
def clear_documents_db(request):
    if request.method == 'POST':
        print("\n--- Django API: Clearing ChromaDB ---")
        try:
            chroma_dir_rag = settings.CHROMA_DB_DIR_RAG
            chroma_dir_qgen = settings.CHROMA_DB_DIR_QGEN 

            if os.path.exists(chroma_dir_rag) and os.listdir(chroma_dir_rag):
                try:
                    temp_chroma_client = Chroma(persist_directory=chroma_dir_rag, embedding_function=models.embeddings)
                    temp_chroma_client.delete_collection(name=None)
                    temp_chroma_client.reset() 
                    print(f"Django API: Gracefully reset ChromaDB at {chroma_dir_rag}.")
                except Exception as e:
                    print(f"Django API: Warning: Graceful reset failed for {chroma_dir_rag}: {e}. Falling back to forceful deletion.")
            
            for db_dir in [chroma_dir_rag, chroma_dir_qgen, settings.PDF_TEMP_DIR, settings.MEDIA_ROOT]:
                if os.path.exists(db_dir):
                    try:
                        shutil.rmtree(db_dir)
                        print(f"Django API: Forcefully deleted {db_dir}.")
                    except Exception as e:
                        print(f"Django API: Error forcefully deleting {db_dir}: {e}. Try manual deletion if issue persists.")
                        return JsonResponse({'status': 'error', 'message': f'Failed to clear: {e}. Please delete {db_dir} manually.'}, status=500)
            
            os.makedirs(chroma_dir_rag, exist_ok=True)
            os.makedirs(chroma_dir_qgen, exist_ok=True)
            os.makedirs(settings.PDF_TEMP_DIR, exist_ok=True)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            rag_graph_module.retriever_rag = None
            print("Django API: All document data cleared and retriever reset.")
            return JsonResponse({'status': 'success', 'message': 'All documents and associated data cleared.'})
        except Exception as e:
            print(f"Django API: Error clearing documents DB: {e}\n{traceback.format_exc()}")
            return JsonResponse({'status': 'error', 'message': f'Failed to clear documents: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@csrf_exempt
def rag_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')

            if not question:
                return JsonResponse({'status': 'error', 'message': 'No question provided.'}, status=400)

            if rag_graph_module.retriever_rag is None:
                 return JsonResponse({'status': 'error', 'message': 'No documents processed. Please ingest documents first.'}, status=400)
            if rag_graph_module.rag_graph_compiled is None:
                 return JsonResponse({'status': 'error', 'message': 'RAG workflow not initialized. Check server logs.'}, status=500)


            print(f"\n--- Django API: Answering question: '{question}' ---")
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
                    "critique_status": "none"
                }
                final_state = rag_graph_module.rag_graph_compiled.invoke(inputs)
                response = final_state.get("generation", "Could not generate an answer.")

                print("--- Django API: RAG flow completed. ---")
                return JsonResponse({'status': 'success', 'answer': response})

            except Exception as e:
                print(f"--- Django API: Error during RAG chat: {e} ---")
                print(traceback.format_exc())
                return JsonResponse({'status': 'error', 'message': f'An error occurred: {e}'}, status=500)

        except json.JSONDecodeError:
             return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)
        except Exception as e:
             print(f"--- Django API: Unexpected Error in rag_chat view: {e} ---")
             print(traceback.format_exc())
             return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {e}'}, status=500)


    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@csrf_exempt
def qgen_questions(request):
     if request.method == 'POST':
         try:
             data = json.loads(request.body)
             topic = data.get('topic')
             num_questions = int(data.get('num_questions', 5))
             difficulty = int(data.get('difficulty', 10))

             if not topic.strip():
                 return JsonResponse({'status': 'error', 'message': 'Please enter a topic for question generation.'}, status=400)

             if rag_graph_module.retriever_rag is None:
                 return JsonResponse({"status": "error", "message": "No documents processed for QGen. Please ingest documents first."}, status=400)
             if models.question_generator_chain is None:
                  return JsonResponse({"status": "error", "message": "LLM or QGen chain not configured. Check backend initialization."}, status=500)

             print(f"\n--- Django API: Generating {num_questions} QGen questions for topic: '{topic}', difficulty {difficulty}/20 ---")
             try:
                 topic_relevant_chunks = rag_graph_module.retriever_rag.invoke(topic)
                 if not topic_relevant_chunks:
                     return JsonResponse({"status": "error", "message": f"Could not find info about '{topic}' in the ingested documents to generate questions."}, status=404)

                 topic_context_str = "\n\n---\n\n".join([doc.page_content for doc in topic_relevant_chunks])

                 raw_questions_output = models.question_generator_chain.invoke({
                     "context": topic_context_str, "topic": topic,
                     "num_questions": num_questions, "difficulty": difficulty
                 })
                 generated_questions = models.get_string_content(raw_questions_output)
                 print(f"--- Django API: Generated QGen questions (raw output):\n{generated_questions}\n---")

                 print("--- Django API: QGen questions generated. ---")
                 return JsonResponse({'status': 'success', 'questions': generated_questions})

             except Exception as e:
                 print(f"--- Django API: Error during QGen: {e} ---")
                 print(traceback.format_exc())
                 return JsonResponse({'status': 'error', 'message': f'An error occurred during question generation: {e}'}, status=500)

         except json.JSONDecodeError:
             return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)
         except Exception as e:
             print(f"--- Django API: Unexpected Error in qgen_questions view: {e} ---")
             print(traceback.format_exc())
             return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {e}'}, status=500)

     return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@csrf_exempt
def summarize_content(request):
    if request.method == 'POST':
        try:
             data = json.loads(request.body)
             topic = data.get('topic')
             generate_handwriting = data.get('generate_handwriting', False)

             if not topic.strip():
                 return JsonResponse({'status': 'error', 'message': 'Please enter a topic for summarization.'}, status=400)

             if rag_graph_module.retriever_rag is None:
                 return JsonResponse({"status": "error", "message": "No documents processed for Summarization. Please ingest documents first."}, status=400)
             if models.summarization_chain is None:
                  return JsonResponse({"status": "error", "message": "LLM or Summarization chain not configured."}, status=500)

             print(f"\n--- Django API: Generating summary for topic: '{topic}' ---")
             handwriting_url = None
             try:
                  topic_relevant_chunks = rag_graph_module.retriever_rag.invoke(topic)
                  if not topic_relevant_chunks:
                      return JsonResponse({"status": "error", "message": f"Could not find information about '{topic}' in the ingested documents to summarize."}, status=404)

                  topic_context_str = "\n\n---\n\n".join([doc.page_content for doc in topic_relevant_chunks])

                  raw_summary_output = models.summarization_chain.invoke({
                      "context": topic_context_str, "topic": topic
                  })
                  generated_summary_text = models.get_string_content(raw_summary_output)
                  print("--- Django API: Summary generated. ---")

                  if generate_handwriting:
                      print("--- Django API: Generating handwriting image... ---")
                      try:
                          os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                          safe_topic_name = "".join(c for c in topic if c.isalnum() or c in [' ', '_']).replace(' ', '_')
                          handwriting_filename = f"summary_{safe_topic_name}_handwriting.png"
                          handwriting_full_path = os.path.join(settings.MEDIA_ROOT, handwriting_filename)

                          render_success = utils.render_text_with_custom_handwriting(
                              text_content=generated_summary_text,
                              output_image_path=handwriting_full_path,
                              custom_font_path=settings.CUSTOM_HANDWRITING_FONT_PATH,
                              font_size=35,
                              text_color=(0, 0, 128),
                              background_color=(255, 255, 240),
                              max_width_pixels=700,
                              padding=50
                          )

                          if render_success:
                              handwriting_url = f"{settings.MEDIA_URL}{handwriting_filename}"
                              print(f"--- Django API: Handwriting image saved, URL: {handwriting_url} ---")
                          else:
                              print("--- Django API: Custom handwriting rendering failed. ---")
                              generated_summary_text += "\n\n(Error: Custom handwriting image generation failed.)"

                      except Exception as e:
                          print(f"--- Django API: Error generating handwriting image: {e} ---")
                          print(traceback.format_exc())
                          generated_summary_text += "\n\n(Error: An unexpected error occurred during handwriting image generation.)"


                  return JsonResponse({'status': 'success', 'summary': generated_summary_text, 'handwriting_url': handwriting_url})


             except Exception as e:
                  print(f"--- Django API: Error during summarization: {e} ---")
                  print(traceback.format_exc())
                  return JsonResponse({'status': 'error', 'message': f'An error occurred: {e}'}, status=500)

        except json.JSONDecodeError:
             return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)
        except Exception as e:
             print(f"--- Django API: Unexpected Error in summarize_content view: {e} ---")
             print(traceback.format_exc())
             return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {e}'}, status=500)


    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)

