"""
RAG with files
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def rag(docs: List[str]):
    """
    RAG function that processes and indexes documents for efficient retrieval in NLP tasks.
    """
    
    docs = [Document(page_content=doc) for doc in docs]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

    return vectorstore

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    from langchain import hub
    from langchain_openai import ChatOpenAI
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(model="gpt-4o-mini")
    
    docs = [
        "Restaurant: The Rustic Spoon\nCuisine: American\nRating: 4.5/5\nReview: The Rustic Spoon offers a cozy atmosphere with delicious comfort food. Their homemade apple pie is to die for!",
        "Restaurant: Sushi Haven\nCuisine: Japanese\nRating: 4.8/5\nReview: Sushi Haven is a hidden gem! The fish is incredibly fresh, and the chef's special rolls are innovative and flavorful.",
        "Restaurant: La Trattoria\nCuisine: Italian\nRating: 4.2/5\nReview: La Trattoria serves authentic Italian dishes. The homemade pasta is excellent, but the service can be a bit slow during peak hours.",
        "Restaurant: Spice Route\nCuisine: Indian\nRating: 4.6/5\nReview: Spice Route offers a wide variety of flavorful Indian dishes. The butter chicken and naan bread are particularly outstanding.",
        "Restaurant: Green Leaf Cafe\nCuisine: Vegetarian\nRating: 4.3/5\nReview: Green Leaf Cafe is a great spot for vegetarians and vegans. Their creative plant-based dishes are both nutritious and delicious."
    ]
    retriever = rag(docs).as_retriever()


    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(rag_chain.invoke("In which restaurant can I find the best apple pie?"))