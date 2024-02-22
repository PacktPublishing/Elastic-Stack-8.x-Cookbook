from langchain_community.vectorstores import ElasticsearchStore
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.docstore.document import Document
from typing import Dict
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
st.set_page_config(page_title="90s Movies chatbot", page_icon=":cinema:")
st.image(
    'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6'
    '/elastic-logo-cluster.svg',
    width=50)

st.title("Vintage movie Chatbot")
st.write('Ask me anything about 90s movies')

# prompt template
LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(
    """Strictly Use ONLY the following pieces of retrieved context to answer the question. 
    If the answer is not in the provided context, just say that you don't know.. 

    context: {context}
    Question: "{question}"
    Answer:
    """
)


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
                    "query": query,
                    "boost": 0.1
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
            },
            "boost": 0.9
        },
        "rank": {
            "rrf": {
                "window_size": 100,
                "rank_constant": 60
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
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# init chat model
def setup_chat_model(base_url, selected_model, llm_temperature):
    chat = None
    if selected_model == 'Ollama/Mistral':
        chat = ChatOllama(base_url=base_url,
                          model="mistral",
                          temperature=llm_temperature)
    return chat


# Setup the rag chain
def setup_rag_chain(prompt_template, llm, retriever):
    rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
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


class SimpleMovieBot:
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

        # default query
        default_query = ('What movies feature a love story and a precious jewel on board a large ocean liner while '
                         'traveling across the Atlantic?')
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
                                           init_retriever(st.session_state.k, self.db, st.session_state.num_candidates)))

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


if __name__ == "__main__":
    chatbot = SimpleMovieBot()
    chatbot.main()
