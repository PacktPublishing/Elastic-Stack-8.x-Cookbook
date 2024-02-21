from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import ElasticsearchStore
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.docstore.document import Document
from typing import Dict

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
embedding = HuggingFaceEmbeddings(model_name='elastic/multilingual-e5-small-optimized')

db = ElasticsearchStore(
    es_cloud_id=ES_CID,
    index_name="movies-dense-vector",
    embedding=embedding,
    es_user=ES_USER,
    es_password=ES_PWD,
    query_field="plot",
    vector_query_field="plot_vector",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy(
        query_model_id=".multilingual-e5-small_linux-x86_64",
        hybrid=True,
    )
)

ollama = ChatOllama(base_url='http://localhost:11434', model='mistral', temperature=0)

LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(
    """Use the following pieces of retrieved context to answer the question. If the answer is not in the provided context, just say that you don't know. Be as verbose and educational in your response as possible. 

    context: {context}
    Question: "{question}"
    Answer:
    """
)

#TODO field and field name
def custom_document_builder(hit: Dict) -> Document:
    src = hit.get("_source", {})
    return Document(
        page_content=src.get("plot", "Missing content!"),
        metadata={
            "title": src.get("title", "Missing title!"),
            "director": src.get("director", "Missing director!"),
            "year": src.get("releaseyear", "Missing year!"),
        },
    )

#TODO custom_query
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,
        "doc_builder":custom_document_builder,
        "fields":["title","director","plot","release_year"]
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


#TODO change title
st.title("Moviebot unchunked")

# Main chat form
with st.form("chat_form"):
    querytest = st.text_input("Movie DB chatbot: ")
    submit_button = st.form_submit_button("Send")

# Generate and display response on form submission
if submit_button:
    resp = ask(querytest)
    st.write("Answer:")
    st.write(f"{resp['response']['answer']}")
    st.write("Context:")

    n=0
    for document in resp['response']['context']:
        # "document" is an instance of Document class, assuming you have such a class defined.
        n = n + 1
        page_content = document.page_content  # Access the page_content attribute
        title = document.metadata['title']  # Access the title from metadata dictionary
        director = document.metadata['director']  # Access the director from metadata dictionary
        year = document.metadata['year']  # Access the year from metadata dictionary

        st.write(f"Document {n}")
        # Print page_content and title
        st.write(f"Title: {title}\nDirector: {director}\nYear: {year}\n")
        st.write(f"Title: {title}\nPage Content: {page_content}\n")


