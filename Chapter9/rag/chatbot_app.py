from langchain_community.vectorstores import ElasticsearchStore

from helper import convert_message, get_conversational_rag_chain, setup_chat_model
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

# load environment variables
load_dotenv()

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


class MovieChatbot:
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
            st.session_state.k = st.sidebar.slider('Number of documents to retrieve', min_value=1, max_value=10,
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

        # default query
        default_query = (
            'Which movie mentions "The ship breaks in half, lifting the stern into the air" and how the '
            'movies ends?')
        # create the message history state or clear it
        if "messages" not in st.session_state or st.sidebar.button("Clear chat history"):
            st.session_state.messages = []

        # render older messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask me anything about favorite 90s movies...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Render the user question
            with st.chat_message("user"):
                st.markdown(prompt)

            # render the assistant's response
            with st.chat_message("assistant"):
                retrival_container = st.container()
                message_placeholder = st.empty()

                retrieval_status = retrival_container.status("**Context Retrieval**")
                queried_questions = []
                rendered_questions = set()

                def update_retrieval_status():
                    for q in queried_questions:
                        if q in rendered_questions:
                            continue
                        rendered_questions.add(q)
                        retrieval_status.markdown(f"\n\n`- {q}`")

                def retrieval_cb(qs):
                    for q in qs:
                        if q not in queried_questions:
                            queried_questions.append(q)
                    return qs

                # get the chain with the retrieval callback
                custom_chain = get_conversational_rag_chain(init_retriever_chatbot(st.session_state.k, self.db,
                                                                                   st.session_state.num_candidates),
                                                            retrieval_cb,
                                                            setup_chat_model(st.session_state.llm_base_url,
                                                              st.session_state.llm_model,
                                                              st.session_state.llm_temperature)
                                                            )

                if "messages" in st.session_state:
                    chat_history = [convert_message(m) for m in st.session_state.messages[:-1]]
                else:
                    chat_history = []

                full_response = ""
                for response in custom_chain.stream(
                        {"input": prompt, "chat_history": chat_history}
                ):
                    if "output" in response:
                        full_response += response["output"]
                    else:
                        full_response += response.content

                    message_placeholder.markdown(full_response + "▌")
                    update_retrieval_status()

                retrieval_status.update(state="complete")
                message_placeholder.markdown(full_response)

                # add the full response to the message history
            st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    app = MovieChatbot()
    app.main()
