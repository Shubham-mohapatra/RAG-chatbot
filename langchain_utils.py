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
    
    vectorstore: Any = None
    k: int = 6
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Any]:
        """Get relevant documents for a query with improved relevance filtering"""
        try:
            # Use regular similarity search (more compatible)
            results = self.vectorstore.similarity_search(query, k=self.k)
            return results
        except Exception as e:
            print(f"Retriever error: {e}")
            return []

# Initialize vector store and retriever
try:
    vectorstore = get_vector_store()
    retriever = ChromaRetriever(vectorstore=vectorstore, k=8)  # Retrieve more documents for better context
    print("✅ Retriever initialized successfully!")
except Exception as e:
    print(f"❌ Warning: Could not initialize retriever: {e}")
    # Create a dummy retriever that properly inherits from BaseRetriever
    class DummyRetriever(BaseRetriever):
        class Config:
            arbitrary_types_allowed = True
            
        def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None) -> List[Any]:
            # Create a simple document-like object
            class SimpleDoc:
                def __init__(self, content):
                    self.page_content = content
                    self.metadata = {}
            return [SimpleDoc("No documents available. Please upload documents first.")]
    
    retriever = DummyRetriever()

output_parser = StrOutputParser()

contextualize_q_system_prompt = (
    "You are helping reformulate user questions to make them clear and standalone. "
    "Given chat history and the latest user message:\n\n"
    
    "1. **For greetings/casual messages** (hi, hello, thanks, sorry, etc.): "
    "Return them unchanged - they don't need reformulation.\n\n"
    
    "2. **For follow-up questions**: "
    "Incorporate relevant context from chat history to make the question complete. "
    "Replace pronouns (it, that, he, she) with specific references.\n\n"
    
    "3. **For standalone questions**: "
    "Return them unchanged if they're already clear.\n\n"
    
    "Examples:\n"
    "- 'What about his education?' → 'What is his educational background?'\n"
    "- 'Tell me more about that' → 'Tell me more about [specific topic from history]'\n"
    "- 'Hello' → 'Hello' (no change)\n"
    "- 'Thanks!' → 'Thanks!' (no change)\n\n"
    
    "Remember: Only reformulate for clarity, don't answer the question."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly and intelligent AI assistant that helps users understand and analyze documents. You're conversational, helpful, and professional.

🎯 YOUR PERSONALITY:
- Warm and approachable - respond naturally to greetings (hi, hello, thank you, etc.)
- Patient and encouraging - make users feel comfortable asking questions
- Professional yet conversational - balance formality with friendliness
- Helpful and thorough - provide detailed answers when needed

📋 HANDLING DIFFERENT TYPES OF MESSAGES:

**Greetings & Social Messages (hi, hello, hey, good morning, etc.):**
- Respond warmly and briefly
- Mention you're here to help with their documents
- Example: "Hello! 👋 I'm here to help you understand your documents. Feel free to ask me anything about the files you've uploaded!"

**Thanks & Appreciation (thank you, thanks, appreciate it):**
- Acknowledge politely and offer continued help
- Example: "You're welcome! Happy to help. Let me know if you have any other questions! 😊"

**Apologies (sorry, my bad):**
- Be understanding and reassuring
- Example: "No worries at all! How can I help you?"

**Out-of-Context Questions (unrelated to documents):**
- Politely redirect to document-related queries
- Example: "I'm specifically designed to help analyze and answer questions about your uploaded documents. Is there something from your documents I can help you with?"

**Document-Related Questions:**
- Provide comprehensive, well-structured answers based on the context
- Use markdown formatting for clarity
- If info isn't in documents, say so clearly and suggest uploading relevant files

📄 CONTEXT FROM UPLOADED DOCUMENTS:
{context}

💡 RESPONSE GUIDELINES:
1. **For casual messages**: Keep responses brief and friendly (1-2 sentences)
2. **For document questions**: Provide detailed, structured answers with:
   - Clear overview
   - Specific details with bullet points
   - Relevant quotes or examples
   - Summary of key points

3. **When no context available**: 
   - Politely explain you need documents uploaded first
   - Suggest what types of documents would be helpful

4. **Formatting**: 
   - Use **bold** for important terms
   - Use bullet points for lists
   - Use ## for main sections in detailed answers
   - Keep it clean and easy to read

Remember: Be helpful, be human, and make the conversation enjoyable! 🌟"""),
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
                max_tokens=3072,   # Increased for more detailed responses
                convert_system_message_to_human=True  # Fix for SystemMessage compatibility
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
