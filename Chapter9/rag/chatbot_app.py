import os
import time
from typing import Dict

import streamlit as st
from dotenv import load_dotenv
from langchain.globals import set_debug
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models.ollama import ChatOllama
from langchain_elasticsearch import ElasticsearchStore

from helper import get_conversational_rag_chain

set_debug(False)

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
ES_VECTOR_INDEX = os.getenv('LANGCHAIN_INDEX')
query_model_id = ".multilingual-e5-small_linux-x86_64"
OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT')

# load environment variables
load_dotenv()

# chat prompt
custom_template = """Given the following conversation and a follow-up message, \
    rephrase the follow-up message to a stand-alone question or instruction that \
    represents the user's intent, add all context needed if necessary to generate a complete and \
    unambiguous question or instruction, only based on the history, don't make up messages. \
    Maintain the same language as the follow up input message.
    Use only the provided context to answer the question, if you don't know, simply answer that you don't know.

    Chat History:
    {chat_history}

    Follow Up Input: {question}
    Standalone question or instruction:"""

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


class AdvancedMovieChatbot:
    def __init__(self):
        self.db = ElasticsearchStore(
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

    def main(self):
        with st.sidebar:
            st.subheader('Choose LLM and parameters')
            st.write("Chatbot configuration")
            st.session_state.llm_model = st.sidebar.selectbox('Choose your LLM',
                                                              ['Ollama/Mistral', 'gpt-3.5-turbo-16k'],
                                                              key='selected_model')
            st.session_state.llm_base_url = st.sidebar.text_input('Ollama base url', OLLAMA_ENDPOINT)
            st.session_state.llm_temperature = st.sidebar.slider('Temperature', min_value=0.0, max_value=1.0,
                                                                 value=0.0,
                                                                 step=0.1, key='llm_temp',
                                                                 help='Control the creativity of the model')
            st.subheader('Configure Retrieval parameters')
            st.session_state.k = st.sidebar.slider('Number of documents to retrieve', min_value=1, max_value=20,
                                                   value=10,
                                                   step=1, key='k_results',
                                                   help='Number of documents to retrieve')
            st.session_state.num_candidates = st.sidebar.slider('Number of candidates', min_value=20, max_value=200,
                                                                value=50,
                                                                step=1, key='num_of_candidates',
                                                                help='Number of candidates to use for vector search')
            st.session_state.rrf_window_size = st.sidebar.slider('RRF window size', min_value=50, max_value=200,
                                                                 value=60,
                                                                 step=10,
                                                                 help='RRF window size')
            st.session_state.rrf_rank_constant = st.sidebar.slider('RRF rank constant', min_value=10, max_value=70,
                                                                   value=10,
                                                                   step=10,
                                                                   help='RRF rank constant')
            st.session_state.display_sources = st.sidebar.checkbox('Display sources', value=False)

        # set up the retriever
        ollama = ChatOllama(base_url=st.session_state.llm_base_url,
                            model='mistral',
                            temperature=st.session_state.llm_temperature)

        chain = get_conversational_rag_chain(llm=ollama,
                                             retriever=init_retriever_chatbot(st.session_state.k,
                                                                              self.db,
                                                                              st.session_state.num_candidates),
                                             prompt_template=custom_template)

        msgs = StreamlitChatMessageHistory()

        if len(msgs.messages) == 0 or st.sidebar.button("Clear message history"):
            msgs.clear()
            msgs.add_ai_message("Hello! How can I help you ?")

        avatars = {"human": "user", "ai": "assistant"}
        for msg in msgs.messages:
            st.chat_message(avatars[msg.type]).write(msg.content)

        if user_query := st.chat_input(placeholder="Ask me anything about favorite 90s movies..."):
            st.chat_message("user").write(user_query)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    response = chain({"question": user_query, "chat_history": msgs})
                    for chunk in response['answer'].split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.write(full_response)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    print(response['answer'])

                    # print sources
                    if st.session_state.display_sources and response['source_documents']:
                        st.markdown(""" ##### Sources documents from the context: """)
                        for docs_source in response['source_documents']:
                            link = f'<a href="{docs_source.metadata["wiki"]}" target="_blank">{docs_source.metadata["title"]}</a>'
                            st.markdown(link, unsafe_allow_html=True)

                except Exception as e:
                    st.write("Oops! Error occurred while processing your request. Please try again later.")
                    print(e)
                    return


if __name__ == "__main__":
    chatbot = AdvancedMovieChatbot()
    chatbot.main()
