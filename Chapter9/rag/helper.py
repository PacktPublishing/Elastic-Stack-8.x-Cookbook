from typing import Optional

# langchain imports
from langchain.schema.runnable import RunnableMap
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
from langchain_community.chat_models import ChatOllama
from langchain.schema import format_document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.docstore.document import Document
from typing import Dict

# global for Elasticsearch RRF
rrf_window_size = 100
rrf_rank_constant = 60


def format_docs(docs):
    res = ""
    # res = str(docs)
    for doc in docs:
        escaped_page_content = doc.page_content.replace("\n", "\\n")
        res += "<doc>\n"
        res += f"  <content>{escaped_page_content}</content>\n"
        for m in doc.metadata:
            res += f"  <{m}>{doc.metadata[m]}</{m}>\n"
        res += "</doc>\n"
    return res


def convert_message(m):
    if m["role"] == "user":
        return HumanMessage(content=m["content"])
    elif m["role"] == "assistant":
        return AIMessage(content=m["content"])
    elif m["role"] == "system":
        return SystemMessage(content=m["content"])
    else:
        raise ValueError(f"Unknown role {m['role']}")


_condense_template = """Given the following conversation and a follow up question, 
                        rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {input}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_condense_template)

_rag_template = """Answer the question based only on the following context, 
                    If the answer is not in the provided context, just say that you don't know..
                    Ignore irrelevant information in the context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(_rag_template)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")


# Setup the rag chain
def setup_rag_chain(prompt_template, llm, retriever):
    rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: qa_format_docs(x["context"])))
            | prompt_template
            | llm
            | StrOutputParser()
    )
    rag_chain_with_source = RunnableParallel(
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }).assign(answer=rag_chain_from_docs)
    return rag_chain_with_source


# function to ask the chatbot and return output
def ask(query: str, rag_chain_with_source):
    output = rag_chain_with_source.invoke(query)
    return {
        "response": output,
    }


def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def _format_chat_history(chat_history):
    def format_single_chat_message(m):
        if type(m) is HumanMessage:
            return "Human: " + m.content
        elif type(m) is AIMessage:
            return "Assistant: " + m.content
        elif type(m) is SystemMessage:
            return "System: " + m.content
        else:
            raise ValueError(f"Unknown role {m['role']}")

    return "\n".join([format_single_chat_message(m) for m in chat_history])


def get_standalone_question_from_chat_history_chain(llm):
    _inputs = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
                            | CONDENSE_QUESTION_PROMPT
                            | llm
                            | StrOutputParser(),
    )
    return _inputs


def get_conversational_rag_chain(retriever, retrieval_cb=None, llm=None):
    if retrieval_cb is None:
        retrieval_cb = lambda x: x

    def context_update_fn(q):
        retrieval_cb([q])
        return q

    _inputs = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
                            | CONDENSE_QUESTION_PROMPT
                            | llm
                            | StrOutputParser(),
    )
    _context = {
        "context": itemgetter("standalone_question") | RunnablePassthrough(
            context_update_fn) | retriever | qa_format_docs,
        "question": lambda x: x["standalone_question"],
    }
    conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | llm
    return conversational_qa_chain


# init chat model
def setup_chat_model(base_url, selected_model, llm_temperature):
    chat = None
    if selected_model == 'Ollama/Mistral':
        chat = ChatOllama(base_url=base_url,
                          model="mistral",
                          temperature=llm_temperature)
    return chat


def get_rag_chain_with_sources(retriever, retrieval_cb=None, llm=None):
    if retrieval_cb is None:
        retrieval_cb = lambda x: x

    def context_update_fn(q):
        retrieval_cb([q])
        return q

    standalone_question = {
        "standalone_question": {
                                   "question": lambda x: x["question"],
                                   "chat_history": lambda x: _format_chat_history(x["chat_history"]),
                               }
                               | CONDENSE_QUESTION_PROMPT
                               | llm
                               | StrOutputParser(),
    }

    retrieved_documents = {
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"],
    }

    final_inputs = {
        "context": lambda x: _combine_documents(x["docs"]),
        "question": itemgetter("question"),
    }

    answer = {
        "answer": final_inputs | ANSWER_PROMPT | llm,
        "docs": itemgetter("docs"),
    }

    # Create the final chain by combining the steps
    final_chain = standalone_question | retrieved_documents | answer
    return final_chain


# custom doc_builder
def custom_document_builder(hit: Dict) -> Document:
    src = hit.get("_source", {})
    return Document(
        page_content=src.get("plot", "Missing content!"),
        metadata={
            "title": src.get("title", "Missing title!"),
            "director": src.get("director", "Missing director!"),
            "year": src.get("release_year", "Missing year!"),
            "wiki_page": src.get("wiki_page", "Missing wiki page!"),
            "release_year": src.get("release_year", "Missing release year!"),
        },
    )


# custom query builder to adjust the query at search
# num_candidates, rrf_window_size, rrf_rank_constant, boost_bm25, k, boost_knn
def custom_query_builder(query_body: dict, query: str):
    new_query_body: Dict = {
        "query": {
            "match": {
                "plot": {
                    "query": query
                }
            }
        },
        "knn": {
            "field": "plot_vector",
            "k": 5,
            "num_candidates": 50,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": ".multilingual-e5-small_linux-x86_64",
                    "model_text": query
                }
            }
        },
        "rank": {
            "rrf": {
                "window_size": rrf_window_size,
                "rank_constant": rrf_rank_constant
            }
        }
    }
    return new_query_body


# init retriever
def init_retriever(k, db, fetch_k):
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "doc_builder": custom_document_builder,
            "custom_query": custom_query_builder,
            "fields": ["title", "director", "plot", "release_year", "wiki_page"],
        }
    )
    return retriever


# format docs for chatbot
def qa_format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
