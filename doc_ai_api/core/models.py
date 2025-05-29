import traceback
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings

from langchain.agents import Tool

from django.conf import settings as config

from . import utils 


llm = None
embeddings = None
document_grader_chain = None
query_rewriter_chain = None
rag_chain = None
question_generator_chain = None
query_classifier_chain = None
context_summarizer_chain = None
critique_chain = None
summarization_chain = None
web_search_tool = None 



def get_string_content(output):
    if hasattr(output, 'content'):
        return str(output.content)
    elif isinstance(output, str):
        return output
    else:
        print(f"Warning: Unexpected output type received: {type(output)}. Attempting str conversion.")
        return str(output)


def initialize_core_models_and_chains():
    global llm, embeddings, document_grader_chain, query_rewriter_chain, rag_chain, question_generator_chain, \
           query_classifier_chain, context_summarizer_chain, critique_chain, summarization_chain, web_search_tool

    print("--- Initializing Core Models and Chains ---")
    try:
        
        llm = ChatOllama(model=config.LLM_MODEL, temperature=0.1)
        test_llm_response_obj = llm.invoke("Quick self-introduction in one sentence.")
        test_llm_response_str = get_string_content(test_llm_response_obj)
        print(f"LLM ({config.LLM_MODEL}) Test response: {test_llm_response_str}")

        
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        embeddings.embed_query("test embedding functionality")  
        print(f"Embedding Model ({config.EMBEDDING_MODEL}) initialized.")
        
        grade_prompt = PromptTemplate(
            template="""You are a grader assessing the collective relevance of a set of retrieved documents to a user question.
            Answer 'yes' if at least one document contains keywords or semantic meaning directly related to the question.
            Answer 'no' if none of the documents appear relevant.
            Only output 'yes' or 'no'. Do not output anything else.

            Retrieved documents:
            {documents}

            User question: {question}
            """,
            input_variables=["documents", "question"],
        )
        document_grader_chain = grade_prompt | llm | StrOutputParser()
        print("RAG: Document grader chain created.")

        rewrite_prompt = PromptTemplate(
            template="""You are a query optimization assistant. Based on the user's original question,
            which failed to yield relevant documents from a local technical knowledge base, rephrase the question to improve retrieval.
            Consider alternative phrasings or technical terms related to the original question.
            Do not answer the original question. Just provide the rephrased question.

            Original question: {question}
            Rephrased question:""",
            input_variables=["question"],
        )
        query_rewriter_chain = rewrite_prompt | llm | StrOutputParser()
        print("RAG: Query rewriter chain created.")

        rag_prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks based on provided technical documents.
            Use the following pieces of retrieved context to answer the question.
            If the context does not contain enough information to answer the question, just state that you don't have enough information from the provided text.
            Keep the answer concise and directly address the question using the provided context.

            Question: {question}
            Context: {context}
            Answer:""",
            input_variables=["question", "context"],
        )
        rag_chain = rag_prompt | llm | StrOutputParser()
        print("RAG: Generation chain created.")

        
        query_classifier_prompt = PromptTemplate( 
            template="""You are a query classification assistant. Classify the user's question into one of the following categories:
            - 'document_based': The question can likely be answered by searching a provided set of technical documents.
            - 'requires_web_search': The question requires current, external, or general knowledge not likely found in a specific technical document set.
            - 'ambiguous_or_general': The question is too broad, unclear, or could fit multiple categories.

            Respond with ONLY one of the keywords: 'document_based', 'requires_web_search', 'ambiguous_or_general'.

            User question: {question}
            Classification:""",
            input_variables=["question"],
        )
        query_classifier_chain = query_classifier_prompt | llm | StrOutputParser()
        print("RAG: Query classifier chain created.")

        context_summarizer_prompt = PromptTemplate( 
            template="""You are a highly skilled summarization assistant. Summarize the following document excerpts.
            Focus on extracting the most relevant information, facts, and concepts that directly relate to the user's question.
            The summary should be concise and contain only information present in the excerpts.

            User Question: {question}

            Document Excerpts:
            {documents}

            Concise Summary:""",
            input_variables=["question", "documents"],
        )
        context_summarizer_chain = context_summarizer_prompt | llm | StrOutputParser()
        print("RAG: Context summarizer chain created.")

        critique_prompt = PromptTemplate( 
            template="""You are an impartial assistant critiquing a generated answer based *only* on the original question and the retrieved context.
            Evaluate the GENERATED ANSWER against the provided CONTEXT and ORIGINAL QUESTION.
            Your goal is to identify if the answer contains significant issues:
            - **Hallucination:** Does the answer include information NOT supported by the CONTEXT?
            - **Contradiction:** Does the answer directly contradict information in the CONTEXT?
            - **Irrelevance/Incompleteness:** Does the answer fail to directly address the core of the ORIGINAL QUESTION, or miss key information that IS present and relevant in the CONTEXT?

            If the GENERATED ANSWER is a reasonable attempt to answer the question using the context (even if not perfect), output 'PASS'.
            If the GENERATED ANSWER has significant issues (hallucination, contradiction, or completely fails to use available context to answer the question), output 'FAIL'.

            Only output 'PASS' or 'FAIL'. Do not output anything else.

            ---
            Original Question: {question}
            Retrieved Context: {context}
            Generated Answer: {generation}
            ---
            Critique Result:""",
            input_variables=["question", "context", "generation"],
        )
        critique_chain = critique_prompt | llm | StrOutputParser()
        print("RAG: Critique chain created.")

        
        question_generation_prompt = PromptTemplate(
            template="""You are a helpful study assistant. Your task is to generate study questions
            based *only* on the following text excerpt.
            The questions should test a student's understanding of the material, especially related to the topic: "{topic}".
            The questions should have a difficulty level corresponding to a {difficulty}/20 scale:
            - Difficulty 1-5: Focus on basic definitions, simple recall.
            - Difficulty 6-10: Focus on understanding concepts, simple explanations, direct application of formulas (if context allows).
            - Difficulty 11-15: Focus on comparing/contrasting ideas, explaining relationships, interpreting data or curves (if context allows).
            - Difficulty 16-20: Focus on analysis, problem-solving application, evaluating scenarios, connecting multiple concepts (if context allows and complexity is present in context).

            Generate {num_questions} distinct questions at the specified difficulty level.
            List the questions clearly, one per line, starting with a number.

            Text Excerpt:
            {context}

            Study Questions (on topic "{topic}", difficulty {difficulty}/20):
            """,
            input_variables=["context", "topic", "num_questions", "difficulty"],
        )
        question_generator_chain = question_generation_prompt | llm | StrOutputParser()
        print("QGen: Question generator chain created.")

        
        summarization_prompt = PromptTemplate(
            template="""You are a helpful assistant. Your task is to provide a concise and informative summary of the following text excerpts, focusing on the main points related to the topic: "{topic}".
            The summary should be presented as clear notes, ideally using bullet points or numbered lists where appropriate.
            Do not include any information not present in the provided text.

            Text Excerpts:
            {context}

            Summary Notes (on topic "{topic}"):
            """,
            input_variables=["context", "topic"],
        )
        summarization_chain = summarization_prompt | llm | StrOutputParser()
        print("Summarization: Summarization chain created.")

       
        
        try:
            
            
            web_search_tool = Tool(
                name="GoogleCustomSearch",
                description="Searches Google using a custom search engine for current events or general knowledge.",
                func=utils.google_custom_search_tool_wrapper 
            )
            print("Google Custom Search Tool (via .env) initialized successfully.")
        except Exception as e:
            
            
            print(f"WARNING: Could not initialize Google Custom Search Tool object. Error: {e}")
            web_search_tool = None

        if web_search_tool is None:
            print("WARNING: No web search tool initialized. External search functionality will be disabled.")


        return True

    except Exception as e:
        print(f"FATAL ERROR: Could not initialize core models or build chains: {e}")
        print(traceback.format_exc())
        
        if "Failed to connect to ollama" in str(e) or "pull" in str(e) or "model" in str(e):
             print("\n--- Ollama Connection/Model Error ---")
             print("Please ensure Ollama is running and the specified model is pulled.")
             print("Run 'ollama serve' in a separate terminal and 'ollama pull your_model_name'.")
             print("-------------------------------------\n")

        llm = None
        embeddings = None
        document_grader_chain = None
        query_rewriter_chain = None
        rag_chain = None
        question_generator_chain = None
        query_classifier_chain = None
        context_summarizer_chain = None
        critique_chain = None
        summarization_chain = None
        web_search_tool = None 
        return False