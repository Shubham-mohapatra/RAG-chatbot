from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List, Any
import os
from chroma_utils import get_vector_store

# Custom retriever class that inherits from BaseRetriever
class ChromaRetriever(BaseRetriever):
    """Custom retriever that works with LangChain's pipeline operators"""
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, vectorstore, k=6, **kwargs):
        super().__init__(**kwargs)
        self._vectorstore = vectorstore
        self._k = k
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Any]:
        """Get relevant documents for a query with improved relevance filtering"""
        try:
            # Use regular similarity search (more compatible)
            results = self._vectorstore.similarity_search(query, k=self._k)
            return results
        except Exception as e:
            print(f"Retriever error: {e}")
            return []

# Initialize vector store and retriever
try:
    vectorstore = get_vector_store()
    retriever = ChromaRetriever(vectorstore, k=8)  # Retrieve more documents for better context
    print("Retriever initialized successfully!")
except Exception as e:
    print(f"Warning: Could not initialize retriever: {e}")
    # Create a dummy retriever with the same interface
    class DummyRetriever:
        def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> List[Any]:
            # Create a simple document-like object
            class SimpleDoc:
                def __init__(self, content):
                    self.page_content = content
                    self.metadata = {}
            return [SimpleDoc("No documents available. Please upload documents first.")]
    
    retriever = DummyRetriever()

output_parser = StrOutputParser()

contextualize_q_system_prompt = (
    "You are an expert at reformulating questions to make them standalone and clear. "
    "Given a chat history and the latest user question, create a standalone question that:"
    "1. Preserves the original intent and all specific details"
    "2. Incorporates relevant context from chat history when needed"
    "3. Replaces pronouns (it, this, that, etc.) with specific references"
    "4. Maintains technical terms and proper nouns exactly as mentioned"
    "5. Is clear and unambiguous without requiring chat history"
    ""
    "If the question is already standalone and clear, return it unchanged. "
    "If it references previous context, incorporate that context into a complete question. "
    "Do NOT answer the question - only reformulate it for clarity."
    "Do NOT answer the question if asked  Who are you"
    "Do NOT mention that you are trained by Google"
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI assistant specialized in document analysis and information extraction. You excel at providing accurate, detailed, and well-structured responses based on document content.

CORE PRINCIPLES:
1. **Accuracy First**: Base your response strictly on the provided context
2. **Be Comprehensive**: Provide detailed, specific information with examples
3. **Clear Structure**: Use markdown formatting, bullet points, and clear organization
4. **Cite Sources**: Reference specific document sections when available
5. **Admit Limitations**: If information is not in the context, say so clearly

RESPONSE STRUCTURE - Always organize your response with:
## Overview
Brief summary of what you found

## Key Details
- **Main Point 1**: Explanation with specifics
- **Main Point 2**: Explanation with specifics  
- **Main Point 3**: Explanation with specifics

## Specific Information
- Relevant quotes or data points
- Technical details or specifications
- Important dates, numbers, or facts

## Summary
Brief conclusion highlighting the most important information

FORMATTING GUIDELINES:
- Use **bold** for key terms and important concepts
- Use bullet points (-) for lists and details
- Use ## for main section headers
- Use ### for subsection headers when needed
- Include relevant quotes in "quotation marks"
- Use *italic* for emphasis on important details
- Structure information logically from general to specific

CONTEXT FROM DOCUMENTS:
{context}

Instructions: Answer the user's question based ONLY on the provided context. If the context doesn't contain enough information to fully answer the question, clearly state what information is missing and provide what you can based on the available content."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def get_rag_chain(model="gemini-2.0-flash-exp"):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "your_google_api_key_here":
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.3,  # Slightly higher for more creative responses
                max_tokens=3072   # Increased for more detailed responses
            )
            print(" Gemini LLM initialized successfully!")
        else:
            raise ValueError("No valid API key found")
    except Exception as e:
        print(f"Warning: Could not initialize Gemini model: {e}")
        print("Please set a valid GOOGLE_API_KEY in your .env file")
        # Create a simple fallback response
        class SimpleLLM:
            def invoke(self, prompt):
                return "I apologize, but I need a valid Google API key to function properly. Please set your GOOGLE_API_KEY in the .env file."
        
        class SimpleChain:
            def __init__(self):
                self.llm = SimpleLLM()
            
            def invoke(self, inputs):
                return {"answer": self.llm.invoke(inputs.get("input", ""))}
        
        return SimpleChain()
    
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain
