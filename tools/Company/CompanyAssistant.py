import secrets
import logging
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.agents import Tool, AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChatOpenAI
chat = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a company-specific assistant. Provide very brutally honest feedback on the users query. "
     "Prioritize using company-related data when available."),
    ("human", "{query}"),
    ("assistant", "{agent_scratchpad}")
])

# Function to dynamically generate tools
def generate_dynamic_tools(company_overview, company_linkedin, glassdoor_summary):
    return [
        Tool(name="CompanyOverview", func=lambda _: company_overview, description="Get the company's overview including mission, culture, and values"),
        Tool(name="CompanyLinkedin", func=lambda _: company_linkedin, description="Get all of the company's LinkedIn data"),
        Tool(name="GlassdoorSummary", func=lambda _: glassdoor_summary, description="Get a summary of the pro and con Glassdoor reviews."),
    ]

def generate_company_response(query: str, chat_session_token: str, company_overview: str, company_linkedin: str, glassdoor_summary: str):
    try:
        # Dynamically generate tools
        tools = generate_dynamic_tools(company_overview, company_linkedin, glassdoor_summary)

        # Create a new agent and executor with the updated tools
        agent = create_openai_tools_agent(chat, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

        # Handle chat history
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="query",
            history_messages_key="chat_history",
        )

        # Generate response
        response = agent_with_chat_history.invoke(
            {
                "query": query,
                "agent_scratchpad": ""  # Add an empty string for `agent_scratchpad`
            },
            config={"configurable": {"session_id": chat_session_token}}
        )
        return response.get("output", "Sorry, I couldn't find relevant information.")
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"An error occurred: {str(e)}"

# Function to get session history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = {}
    if session_id not in st.session_state["chat_sessions"]:
        st.session_state["chat_sessions"][session_id] = ChatMessageHistory()
    return st.session_state["chat_sessions"][session_id]