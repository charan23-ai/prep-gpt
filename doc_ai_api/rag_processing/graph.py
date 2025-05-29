import traceback
from typing import List, TypedDict, Optional
from langgraph.graph import START, END, StateGraph

from ..core import (
    models,
)

retriever_rag = None
rag_graph_compiled = None


class GraphState(TypedDict):
    question: str
    documents: List[str] 
    summarized_context: Optional[str]
    relevance_grade: str
    query_rewrite_attempted: bool
    query_classification: str
    generation: str
    critique_status: str
    attempt_count: int


def classify_query_node_rag(state: GraphState):
    print("\n---NODE: RAG CLASSIFY QUERY---")
    question = state["question"]

    if models.query_classifier_chain is None:
        print("Error: RAG Query classifier chain not initialized.")
        return {**state, "query_classification": "document_based"}

    print(f"Classifying query: '{question}'")
    try:
        raw_classification_output = models.query_classifier_chain.invoke(
            {"question": question}
        )
        classification = (
            models.get_string_content(raw_classification_output)
            .strip()
            .lower()
            .strip("'")
            .strip('"')
        )

        if classification not in [
            "document_based",
            "requires_web_search",
            "ambiguous_or_general",
        ]:
            print(
                f"Warning: Classifier returned unexpected output: '{classification}'. Defaulting to 'document_based'."
            )
            classification = "document_based"
    except Exception as e:
        print(f"Error during RAG query classification: {e}\n{traceback.format_exc()}")
        classification = "document_based"
    print(f"Query classified as: '{classification}'")
    return {**state, "query_classification": classification}


def web_search_tool_node_rag(state: GraphState):
    print("\n---NODE: RAG WEB SEARCH---")
    question = state["question"]
    print(f"Performing web search for: '{question}'")

    if models.web_search_tool is None:
        print("Error: Web Search Tool not initialized. Cannot perform web search.")
        return {
            **state,
            "documents": ["Error: Web search tool not available."],
            "relevance_grade": "no",
            "query_rewrite_attempted": True,
        }

    try:
        search_results_raw = models.web_search_tool.run(question)
        search_results_doc = [f"Web Search Results:\n{search_results_raw}"]
        print(f"Web search executed. Results length: {len(search_results_raw)} chars.")

        return {
            **state,
            "documents": search_results_doc,
            "relevance_grade": "yes",
            "query_rewrite_attempted": True,
            "summarized_context": None,
            "generation": None,
            "critique_status": "none",
        }
    except Exception as e:
        print(f"Error during RAG web search: {e}\n{traceback.format_exc()}")
        return {
            **state,
            "documents": [f"Error during web search: {e}"],
            "relevance_grade": "no",
            "query_rewrite_attempted": True,
        }


def retrieve_node_rag(state: GraphState):
    print("\n---NODE: RAG RETRIEVE DOCUMENTS---")
    question = state["question"]
    print(f"Retrieving for question: '{question}'")

    global retriever_rag
    if retriever_rag is None:
        print("Error: RAG Retriever not initialized.")
        return {
            **state,
            "documents": [],
            "relevance_grade": "no",
            "generation": None,
            "critique_status": "none",
        }

    try:
        documents_obj = retriever_rag.invoke(question)
        doc_contents = [doc.page_content for doc in documents_obj]
        print(f"Retrieved {len(doc_contents)} documents.")
    except Exception as e:
        print(f"Error during RAG retrieval: {e}\n{traceback.format_exc()}")
        doc_contents = []
    return {
        **state,
        "documents": doc_contents,
        "relevance_grade": "unknown",
        "summarized_context": None,
        "generation": None,
        "critique_status": "none",
    }


def grade_documents_node_rag(state: GraphState):
    print("\n---NODE: RAG GRADE DOCUMENTS---")
    question = state["question"]
    documents = state["documents"]

    if models.document_grader_chain is None:
        print("Error: RAG Document grader chain not initialized (LLM failed?).")
        return {**state, "relevance_grade": "no"}

    if not documents:
        print("No documents to grade.")
        return {**state, "relevance_grade": "no"}

    documents_str = "\n---\n".join(documents)
    print("Asking LLM to grade RAG document relevance...")
    try:
        raw_grade_output = models.document_grader_chain.invoke(
            {"question": question, "documents": documents_str}
        )
        grade = models.get_string_content(raw_grade_output).strip().lower()

        if grade not in ["yes", "no"]:
            print(
                f"Warning: RAG Grader returned unexpected output: '{grade}'. Defaulting to 'no'."
            )
            grade = "no"
    except Exception as e:
        print(f"Error during RAG document grading: {e}\n{traceback.format_exc()}")
        grade = "no"
    print(f"RAG LLM Grade: {grade}")
    return {**state, "relevance_grade": grade}


def transform_query_node_rag(state: GraphState):
    print("\n---NODE: RAG TRANSFORM QUERY---")
    question = state["question"]

    if models.query_rewriter_chain is None:
        print("Error: RAG Query rewriter chain not initialized (LLM failed?).")
        return {**state, "query_rewrite_attempted": True}

    print(f"Attempting to rewrite question: '{question}'")
    try:
        raw_better_question_output = models.query_rewriter_chain.invoke(
            {"question": question}
        )
        better_question = models.get_string_content(raw_better_question_output).strip()
        print(f"Rewritten question: '{better_question}'")
        return {**state, "question": better_question, "query_rewrite_attempted": True}
    except Exception as e:
        print(f"Error during RAG query transformation: {e}\n{traceback.format_exc()}")
        return {**state, "query_rewrite_attempted": True}


def summarize_context_node_rag(state: GraphState):
    print("\n---NODE: RAG SUMMARIZE CONTEXT---")
    question = state["question"]
    documents = state["documents"]

    if models.context_summarizer_chain is None:
        print("Error: Context summarizer chain not initialized.")
        return {
            **state,
            "summarized_context": "\n\n---\n\n".join(documents) if documents else None,
        }

    if not documents:
        print("No documents to summarize.")
        return {**state, "summarized_context": None}

    documents_str = "\n\n---\n\n".join(documents)
    print(f"Summarizing {len(documents)} documents for question: '{question}'")
    try:
        raw_summarized_context_output = models.context_summarizer_chain.invoke(
            {"question": question, "documents": documents_str}
        )
        summarized_context = models.get_string_content(raw_summarized_context_output)
        print(f"Context summarized (length: {len(summarized_context)} chars).")
        return {**state, "summarized_context": summarized_context}
    except Exception as e:
        print(f"Error during context summarization: {e}\n{traceback.format_exc()}")
        return {
            **state,
            "summarized_context": "\n\n---\n\n".join(documents) if documents else None,
        }


def generate_node_rag(state: GraphState):
    print("\n---NODE: RAG GENERATE ANSWER---")
    question = state["question"]
    documents = state["documents"]
    context_for_generation = state["summarized_context"]
    relevance_grade = state["relevance_grade"]

    if models.rag_chain is None or models.llm is None:
        print("Error: RAG chain or LLM not initialized.")
        generation = "Error: LLM or RAG chain not configured."
    elif relevance_grade == "no" or not documents:
        print(
            "No relevant documents found for RAG. Generating a response indicating lack of information."
        )
        try:
            raw_generation_output = models.llm.invoke(
                f"Based on the provided documents, I was unable to find information to answer the question: '{question}'. Please try rephrasing or asking about a different topic."
            )
            generation = models.get_string_content(raw_generation_output)
        except Exception as e:
            print(
                f"Error generating 'don't know' RAG response: {e}\n{traceback.format_exc()}"
            )
            generation = (
                "I cannot answer this question based on the provided documents."
            )
    else:
        print(
            f"Generating RAG answer using summarized context (length: {len(context_for_generation)} chars) for question: '{question}'..."
        )
        try:
            raw_generation_output = models.rag_chain.invoke(
                {"context": context_for_generation, "question": question}
            )
            generation = models.get_string_content(raw_generation_output)
        except Exception as e:
            print(f"Error during RAG generation: {e}\n{traceback.format_exc()}")
            generation = "An error occurred during answer generation."
    print(f"Generated RAG response: {generation}")
    return {**state, "generation": generation}


def critique_answer_node_rag(state: GraphState):
    print("\n---NODE: RAG CRITIQUE ANSWER---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    if models.critique_chain is None:
        print("Error: Critique chain not initialized.")
        return {**state, "critique_status": "PASS"}

    if not generation or not documents:
        print("No generation or documents to critique.")
        return {
            **state,
            "critique_status": "FAIL",
            "attempt_count": state["attempt_count"] + 1,
        }

    documents_str = "\n\n---\n\n".join(documents)
    print("Asking LLM to critique the generated answer...")
    try:
        raw_critique_output = models.critique_chain.invoke(
            {"question": question, "context": documents_str, "generation": generation}
        )
        critique_result = models.get_string_content(raw_critique_output).strip().upper()

        if critique_result not in ["PASS", "FAIL"]:
            print(
                f"Warning: Critique returned unexpected output: '{critique_result}'. Defaulting to 'FAIL'."
            )
            critique_result = "FAIL"
    except Exception as e:
        print(f"Error during RAG critique: {e}\n{traceback.format_exc()}")
        critique_result = "FAIL"
    print(f"Critique Result: {critique_result}")
    return {
        **state,
        "critique_status": critique_result,
        "attempt_count": state["attempt_count"] + 1,
    }


def decide_route_on_query_classification(state: GraphState):
    print("\n---RAG DECISION NODE (Query Classification)---")
    classification = state["query_classification"]
    print(f"Query Classification: {classification}")

    if classification == "document_based":
        print(
            "---RAG DECISION: Query is document-based, proceed to retrieve from internal DB.---"
        )
        return "retrieve_internal"
    elif classification == "requires_web_search":
        
        if models.web_search_tool:
            print(
                "---RAG DECISION: Query requires web search. Proceed to web search tool.---"
            )
            return "web_search"
        else:
            print(
                "---RAG DECISION: Query requires web search, but tool not available. Defaulting to internal retrieval.---"
            )
            return "retrieve_internal"
    else:  
        print(
            "---RAG DECISION: Query is ambiguous/general, defaulting to internal document retrieval.---"
        )
        return "retrieve_internal"



def decide_to_summarize_or_transform_rag(state: GraphState):
    print("\n---RAG DECISION NODE (Document Grade Check)---")
    relevance_grade = state["relevance_grade"]
    query_rewrite_attempted = state.get("query_rewrite_attempted", False)
    print(f"RAG Grade: {relevance_grade}, Rewrite Attempted: {query_rewrite_attempted}")

    if relevance_grade == "yes":
        print(
            "---RAG DECISION: Documents relevant, proceed to context summarization.---"
        )
        return "summarize_context"
    else:  
        if not query_rewrite_attempted:
            print(
                "---RAG DECISION: No relevant documents, attempting query transformation.---"
            )
            return "transform_query"
        else:
            print(
                "---RAG DECISION: Query transformation already attempted, no relevant documents found, proceed to generation (failure).---"
            )
            return "generate"



MAX_ATTEMPTS = 2 


def decide_to_loop_or_end_rag(state: GraphState):
    print("\n---RAG DECISION NODE (Critique Check)---")
    critique_status = state["critique_status"]
    attempt_count = state["attempt_count"]
    print(f"Critique Status: {critique_status}, Attempt Count: {attempt_count}")

    if critique_status == "PASS":
        print("---RAG DECISION: Critique passed, ending workflow.---")
        return "end"
    elif attempt_count < MAX_ATTEMPTS:
        print(
            f"---RAG DECISION: Critique failed (Attempt {attempt_count}/{MAX_ATTEMPTS}). Retrying retrieval.---"
        )
        
        state["generation"] = None
        state["summarized_context"] = None
        state["documents"] = []  
        state["relevance_grade"] = "unknown"
        return "retry"  
    else:
        print(
            f"---RAG DECISION: Critique failed and max attempts ({MAX_ATTEMPTS}) reached. Ending workflow.---"
        )
        return "end"


def compile_rag_workflow():
    global rag_graph_compiled
    
    if not (
        models.document_grader_chain
        and models.query_rewriter_chain
        and models.rag_chain
        and models.query_classifier_chain
        and models.context_summarizer_chain
        and models.critique_chain
    ):
        print(
            "RAG LangGraph workflow compilation skipped due to chain initialization failure."
        )
        rag_graph_compiled = None
        return False

    workflow_rag = StateGraph(GraphState)

    
    workflow_rag.add_node("classify_query", classify_query_node_rag)
    workflow_rag.add_node("web_search", web_search_tool_node_rag)
    workflow_rag.add_node("retrieve", retrieve_node_rag)
    workflow_rag.add_node("grade_documents", grade_documents_node_rag)
    workflow_rag.add_node("transform_query", transform_query_node_rag)
    workflow_rag.add_node("summarize_context", summarize_context_node_rag)
    workflow_rag.add_node("generate", generate_node_rag)
    workflow_rag.add_node("critique_answer", critique_answer_node_rag)

   
    workflow_rag.set_entry_point("classify_query")

    
    workflow_rag.add_conditional_edges(
        "classify_query",
        decide_route_on_query_classification,
        {
            "retrieve_internal": "retrieve",
            "web_search": "web_search",
        },
    )

    
    workflow_rag.add_edge("web_search", "grade_documents")

    
    workflow_rag.add_edge("retrieve", "grade_documents")

    
    workflow_rag.add_conditional_edges(
        "grade_documents",
        decide_to_summarize_or_transform_rag,
        {
            "transform_query": "transform_query",
            "summarize_context": "summarize_context",
            "generate": "generate",   
        },
    )

    
    workflow_rag.add_edge("transform_query", "retrieve")

    
    workflow_rag.add_edge("summarize_context", "generate")

    
    workflow_rag.add_edge("generate", "critique_answer")

    
    workflow_rag.add_conditional_edges(
        "critique_answer",
        decide_to_loop_or_end_rag,
        {
            "retry": "retrieve",
            "end": END,
        },
    )

    try:
        rag_graph_compiled = workflow_rag.compile()
        print("RAG LangGraph workflow compiled successfully.")
        
        try:
            rag_graph_compiled.get_graph().draw_png("rag_workflow.png")
            print("RAG workflow graph saved as rag_workflow.png")
        except Exception as e:
            print(
                f"Warning: Could not draw PNG graph. Ensure graphviz and pygraphviz are installed. Error: {e}"
            )

        
        try:
            mermaid_syntax = rag_graph_compiled.get_graph().draw_mermaid()
            with open("rag_workflow.mermaid", "w") as f:
                f.write(mermaid_syntax)
            print(
                "RAG workflow Mermaid syntax saved to rag_workflow.mermaid. Paste into Mermaid Live Editor (https://mermaid.live)."
            )
        except Exception as e:
            print(f"Warning: Could not generate Mermaid graph. Error: {e}")

        return True
    except Exception as e:
        print(f"FATAL ERROR: Error compiling RAG LangGraph workflow: {e}")
        print(traceback.format_exc())
        rag_graph_compiled = None
        return False
