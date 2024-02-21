from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import ElasticsearchStore
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import format_document


import os
import streamlit as st
import openai

from dotenv import load_dotenv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
embedding = HuggingFaceEmbeddings(model_name='elastic/multilingual-e5-small-optimized')

db = ElasticsearchStore(
    es_cloud_id=ES_CID,
    index_name="movies-langchain-generated",
    embedding=embedding,
    es_user=ES_USER,
    es_password=ES_PWD,
    query_field="text",
    vector_query_field="vector",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy(
        query_model_id=".multilingual-e5-small_linux-x86_64",
        hybrid=True,
    )
)

ollama = ChatOllama(base_url='http://localhost:11434', model='mistral',temperature=0)

LLM_CONTEXT_PROMPT = ChatPromptTemplate.from_template(
    """Use the following pieces of retrieved context to answer the question. If the answer is not in the provided context, just say that you don't know. Be as verbose and educational in your response as possible. 

    context: {context}
    Question: "{question}"
    Answer:
    """
)
LLM_DOCUMENT_PROMPT = PromptTemplate.from_template(
    """
---
TITLE: {title}
DIRECTOR: {director}
YEAR: {release_year}
GENRE: {genre} 
PLOT PASSAGE:
{page_content}
---
"""
)

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# def _combine_documents(
#     docs, document_prompt=LLM_DOCUMENT_PROMPT, document_separator="\n\n"
# ):
#     doc_strings = [format_document(doc, document_prompt) for doc in docs]
#     return document_separator.join(doc_strings)
#
# _context = RunnableParallel(
#     context=retriever | _combine_documents,
#     question=RunnablePassthrough(),
# )
#
#
# chain = _context | LLM_CONTEXT_PROMPT | ollama | StrOutputParser()

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


#Main chat form
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
        st.write(f"Chunk {n}")
        # Print page_content and title
        st.write(f"Title: {title}")
        st.write(f"Page Content: {page_content}")