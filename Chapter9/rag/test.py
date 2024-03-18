from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.chat_models.ollama import ChatOllama
from langchain_elasticsearch import ElasticsearchStore
from langchain.globals import set_debug
from typing import Dict

import os
import streamlit as st
from dotenv import load_dotenv

set_debug(False)

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
ES_VECTOR_INDEX = os.getenv('LANGCHAIN_INDEX')
query_model_id = ".multilingual-e5-small_linux-x86_64"
OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT')


# streamlit UI Config
st.set_page_config(page_title="Chatbot 90's movies", page_icon=":cinema:", initial_sidebar_state="collapsed")
st.image(
    'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6'
    '/elastic-logo-cluster.svg',
    width=50)

st.header("Advanced Vintage movie Chatbot")
st.write('Ask me anything about your favorite movies')


# test with streamlit context variables:
if 'rrf_window_size' not in st.session_state:
    st.session_state['rrf_window_size'] = 200
if 'rrf_rank_constant' not in st.session_state:
    st.session_state['rrf_rank_constant'] = 60

# global
rrf_window_size = st.session_state['rrf_window_size']
rrf_rank_constant = st.session_state['rrf_rank_constant']



def custom_query_builder(query_body: dict, query: str):
    new_query_body: Dict = {
        "query": {
            "match": {
                "text_field": {
                    "query": query
                }
            }
        },
        "knn": {
            "field": "vector_query_field.predicted_value",
            "k": 10,
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


def init_retriever_chatbot(k, db, fetch_k):
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "custom_query": custom_query_builder,
        }
    )
    return retriever

db = ElasticsearchStore(
    es_cloud_id=ES_CID,
    index_name=ES_VECTOR_INDEX,
    es_user=ES_USER,
    es_password=ES_PWD,
    query_field="text_field",
    vector_query_field="vector_query_field.predicted_value",
    distance_strategy="DOT_PRODUCT",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy(
        hybrid=True,
        query_model_id=query_model_id,
    )
)

ollama = ChatOllama(base_url='http://localhost:11434', model='mistral',temperature=0)


def get_conversation_chain(query, chat_history):
    # ConversationalRetrievalChain
    qa = ConversationalRetrievalChain.from_llm(
        llm=ollama,
        retriever=init_retriever_chatbot(10, db,50)
    )

    return qa({"question": query, "chat_history": chat_history})


if __name__ == '__main__':

    # ChatInput
    prompt = st.chat_input("Enter your questions here")

    if "user_prompt_history" not in st.session_state:
       st.session_state["user_prompt_history"]=[]
    if "chat_answers_history" not in st.session_state:
       st.session_state["chat_answers_history"]=[]
    if "chat_history" not in st.session_state:
       st.session_state["chat_history"]=[]

    if prompt:
       with st.spinner("Generating......"):
           output=get_conversation_chain(query=prompt, chat_history = st.session_state["chat_history"])

          # Storing the questions, answers and chat history

           st.session_state["chat_answers_history"].append(output['answer'])
           st.session_state["user_prompt_history"].append(prompt)
           st.session_state["chat_history"].append((prompt,output['answer']))

    # Displaying the chat history

    if st.session_state["chat_answers_history"]:
       for i, j in zip(st.session_state["chat_answers_history"],st.session_state["user_prompt_history"]):
          message1 = st.chat_message("user")
          message1.write(j)
          message2 = st.chat_message("assistant")
          message2.write(i)

