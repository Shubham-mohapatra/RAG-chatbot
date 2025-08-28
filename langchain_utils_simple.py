from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import google.generativeai as genai

def get_rag_chain(retriever=None, model_name="gemini-1.5-flash"):
    """
    Create a simple RAG chain using Google Generative AI
    """
    try:
        # Configure the model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        # Create a simple prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer the user's question based on the context provided."),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])
        
        # Create a simple chain
        chain = prompt | llm | StrOutputParser()
        
        return chain
    
    except Exception as e:
        print(f"Error creating RAG chain: {e}")
        # Fallback to direct Google AI
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel(model_name)
        return model

def get_response_from_query(rag_chain, query: str, retriever=None):
    """
    Get response from the RAG chain
    """
    try:
        # If we have a retriever, get context
        if retriever:
            docs = retriever.get_relevant_documents(query)
            context = "\n".join([doc.page_content for doc in docs])
        else:
            context = "No additional context available."
        
        # If it's a langchain chain
        if hasattr(rag_chain, 'invoke'):
            response = rag_chain.invoke({
                "context": context,
                "question": query
            })
        else:
            # Fallback for direct Google AI model
            prompt = f"Context: {context}\n\nQuestion: {query}"
            response = rag_chain.generate_content(prompt)
            response = response.text
            
        return response
    
    except Exception as e:
        print(f"Error getting response: {e}")
        # Ultimate fallback - direct Google AI call
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(query)
        return response.text
