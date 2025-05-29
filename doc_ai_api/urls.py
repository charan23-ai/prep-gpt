from django.urls import path
from . import views

urlpatterns = [
    path('ingest_documents/', views.ingest_documents, name='ingest_documents'),
    path('clear_documents_db/', views.clear_documents_db, name='clear_documents_db'),
    path('rag_chat/', views.rag_chat, name='rag_chat'),
    path('qgen/', views.qgen_questions, name='qgen_questions'),
    path('summarize/', views.summarize_content, name='summarize_content'),
]