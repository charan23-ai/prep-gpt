

from django.apps import AppConfig
import os 

class DocAiApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doc_ai_api'

    def ready(self):
        from .core import models
        from .rag_processing import graph
        
        from langchain_community.vectorstores import Chroma
        from django.conf import settings 

        print("Django app 'doc_ai_api' starting up. Initializing models and graph...")
        models_initialized_successfully = models.initialize_core_models_and_chains()

        if models_initialized_successfully:
            
            chroma_dir_rag = settings.CHROMA_DB_DIR_RAG
            if os.path.exists(chroma_dir_rag) and os.listdir(chroma_dir_rag): 
                try:
                    print(f"Django API: Loading existing ChromaDB from {chroma_dir_rag} on startup...")
                    
                    vectorstore_rag = Chroma(
                        persist_directory=chroma_dir_rag,
                        embedding_function=models.embeddings
                    )
                    graph.retriever_rag = vectorstore_rag.as_retriever(search_kwargs={"k": 3})
                    print("Django API: Existing ChromaDB loaded and retriever created on startup.")
                except Exception as e:
                    print(f"Django API: Error loading existing ChromaDB on startup: {e}")
                    graph.retriever_rag = None 
            else:
                print(f"Django API: No existing ChromaDB found at {chroma_dir_rag} or it's empty. Retriever will be None initially.")
                graph.retriever_rag = None 

            
            graph.compile_rag_workflow()
        else:
             print("Skipping RAG graph compilation due to model initialization failure.")

        print("Django app 'doc_ai_api' ready.")