
# langchain imports
from langchain.prompts.prompt import PromptTemplate
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.docstore.document import Document
from typing import Dict
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

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


# init chat model
def setup_chat_model(base_url, selected_model, llm_temperature):
    chat = None
    if selected_model == 'Ollama/Mistral':
        chat = ChatOllama(base_url=base_url,
                          model="mistral",
                          temperature=llm_temperature)
    return chat


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


# Conversation chain for chatbot application
def get_conversational_rag_chain(llm, retriever, prompt_template):
    chat = llm
    # memory for chat history
    msgs = StreamlitChatMessageHistory()
    memory = ConversationBufferMemory(memory_key="chat_history",
                                      chat_memory=msgs,
                                      return_messages=True,
                                      max_history=5,
                                      output_key="answer")

    # prompt template
    qa_chain_prompt = PromptTemplate(input_variables=["chat_history", "question"], template=prompt_template)

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        memory=memory,
        verbose=True,
        retriever=retriever,
        condense_question_prompt=PromptTemplate.from_template(prompt_template),
        return_source_documents=True,
    )
    return chain