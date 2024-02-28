from langchain_community.vectorstores import ElasticsearchStore
from langchain.prompts import ChatPromptTemplate

from helper import setup_chat_model, init_retriever, ask, setup_rag_chain
import time

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
ES_VECTOR_INDEX = os.getenv('VECTOR_INDEX')
query_model_id = ".multilingual-e5-small_linux-x86_64"
OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT')

# load environment variables
load_dotenv()

# streamlit UI Config
st.set_page_config(page_title="Question answering on 90's movies", page_icon=":cinema:")
st.image(
    'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6'
    '/elastic-logo-cluster.svg',
    width=50)

st.header("Movie QA Bot")
st.write('Ask me anything about 90s movies')

# test with streamlit context variables:
if 'rrf_window_size' not in st.session_state:
    st.session_state['rrf_window_size'] = 200
if 'rrf_rank_constant' not in st.session_state:
    st.session_state['rrf_rank_constant'] = 60

# global
rrf_window_size = st.session_state['rrf_window_size']
rrf_rank_constant = st.session_state['rrf_rank_constant']

# prompt template
LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(
    """Strictly Use ONLY the following pieces of retrieved context to answer the question. 
    If the answer is not in the provided context, just say that you don't know.. 

    {context}
    Question: "{question}"
    Answer:
    """
)


class QAMovieBot:
    def __init__(self):

        self.db = ElasticsearchStore(
            es_cloud_id=ES_CID,
            index_name=ES_VECTOR_INDEX,
            es_user=ES_USER,
            es_password=ES_PWD,
            query_field="plot",
            vector_query_field="plot_vector",
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
            st.session_state.k = st.sidebar.slider('Number of documents to retrieve', min_value=5, max_value=10,
                                                   value=5,
                                                   step=1, key='k_results',
                                                   help='Number of documents to retrieve')
            st.session_state.num_candidates = st.sidebar.slider('Number of candidates', min_value=20, max_value=200,
                                                                value=50,
                                                                step=1, key='num_of_candidates',
                                                                help='Number of candidates to use for vector search')
            st.session_state.rrf_window_size = st.sidebar.slider('RRF window size', min_value=50, max_value=200,
                                                                 value=100,
                                                                 step=10,
                                                                 help='RRF window size')
            st.session_state.rrf_rank_constant = st.sidebar.slider('RRF rank constant', min_value=10, max_value=70,
                                                                   value=20,
                                                                   step=10,
                                                                   help='RRF rank constant')
        #

        # default query
        default_query = ('Which film talks about a love story and a jewel on a large ocean liner travelling across '
                         'the Atlantic? ')
        # Main chat form
        with st.form("chat_form"):

            user_query = st.text_input("Movie DB chatbot: ", value=default_query)
            submit_button = st.form_submit_button("Send")

        # Generate and display response on form submission
        if submit_button:
            with st.chat_message("Assistant"):

                message_placeholder = st.empty()
                full_response = ""

                # Pass the user query to the chatbot
                resp = ask(user_query,
                           setup_rag_chain(LLM_CONTEXT_PROMPT,
                                           setup_chat_model(st.session_state.llm_base_url,
                                                            st.session_state.llm_model,
                                                            st.session_state.llm_temperature),
                                           init_retriever(st.session_state.k, self.db,
                                                          st.session_state.num_candidates)))

                # Display the response from the chatbot
                for chunk in resp['response']['answer'].split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.text(full_response)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + ". ")

                # Printing sources used for the answer
                st.markdown(""" ##### Movies from the context used for the answer: """)
                with st.container():
                    for docs_source in resp['response']['context']:
                        link = f'<a href="{docs_source.metadata["wiki_page"]}" target="_blank">{docs_source.metadata["title"]}</a>'
                        st.markdown(link + " by Director: %s " % (docs_source.metadata["director"]),
                                    unsafe_allow_html=True)

            with st.expander("RRF Parameters", expanded=False):
                st.write("RRF window size: ", rrf_window_size)
                st.write("RRF rank constant: ", rrf_rank_constant)


if __name__ == "__main__":
    chatbot = QAMovieBot()
    chatbot.main()
