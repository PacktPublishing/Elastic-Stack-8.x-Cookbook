from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import ElasticsearchStore
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
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

# streamlit UI Config
st.set_page_config(page_title="90s Movies chatbot", page_icon=":cinema:")
st.image(
    'https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt601c406b0b5af740/620577381692951393fdf8d6/elastic-logo-cluster.svg',
    width=50)

st.title("Vintage movie Chatbot")
st.write('Ask me anything about 90s movies')

db = ElasticsearchStore(
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
        rrf={"window_size": 100, "rank_constant": 60}
    )
)

# init chat model
ollama = ChatOllama(base_url='http://localhost:11434', model='mistral', temperature=0)

LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(
    """Use the following pieces of retrieved context to answer the question. If the answer is not in the provided context, just say that you don't know. Be as verbose and educational in your response as possible. 

    context: {context}
    Question: "{question}"
    Answer:
    """
)


# TODO field and field name
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


# TODO custom_query
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,
        "doc_builder": custom_document_builder,
        "fields": ["title", "director", "plot", "release_year", "wiki_page"],
    }
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | LLM_CONTEXT_PROMPT
        | ollama
        | StrOutputParser()
)

rag_chain_with_source = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer=rag_chain_from_docs)


def ask(query: str):
    output = rag_chain_with_source.invoke(query)
    return {
        "response": output,
    }


# TODO change title
with st.sidebar:
    st.subheader('Choose LLM and parameters')
    st.write("Chatbot configuration")

# Main chat form
with st.form("chat_form"):
    user_query = st.text_input("Movie DB chatbot: ")
    submit_button = st.form_submit_button("Send")

# Generate and display response on form submission
if submit_button:
    with st.chat_message("MovieBot"):
        message_placeholder = st.empty()
        full_response = ""

        # Pass the user query to the chatbot
        resp = ask(user_query)

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
                st.markdown(link + " by Director: %s " % (docs_source.metadata["director"]), unsafe_allow_html=True)


