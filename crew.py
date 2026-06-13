import os
import logging

logger = logging.getLogger(__name__)

# Try to import CrewAI. If not installed (or compiling), we fall back to a simulation.
try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI is not yet installed in the virtual environment. A mock fallback will be used.")

def kickoff_crew(message_text: str, sender_name: str, space_display_name: str) -> str:
    """
    Kicksoff the CrewAI agent to draft a reply to the Google Chat message.
    
    Args:
        message_text (str): The body of the chat message.
        sender_name (str): The display name of the message sender.
        space_display_name (str): The user-friendly display name of the space/group.
        
    Returns:
        str: The response drafted by the agent.
    """
    if CREWAI_AVAILABLE:
        # Optional: You can specify custom LLM configurations here
        # e.g., from langchain_google_genai import ChatGoogleGenerativeAI
        # llm = ChatGoogleGenerativeAI(model="gemini-pro")
        
        # 1. Define the Google Chat Responder Agent
        chat_responder = Agent(
            role="Google Chat Responder",
            goal="Provide helpful, concise, and polite responses to incoming chat messages.",
            backstory=(
                "You are a professional assistant integrated with Google Chat. "
                "Your job is to draft high-quality, friendly, and context-aware replies "
                "to messages in chat rooms and direct messages."
            ),
            verbose=True
        )
        
        # 2. Define the task
        reply_task = Task(
            description=(
                f"Draft a response to the following chat message: '{message_text}'.\n"
                f"The message was sent by '{sender_name}' in the space '{space_display_name}'."
            ),
            expected_output="A helpful, concise, and context-aware reply message ready to send.",
            agent=chat_responder
        )
        
        # 3. Instantiate the Crew
        crew = Crew(
            agents=[chat_responder],
            tasks=[reply_task],
            verbose=True
        )
        
        # 4. Kickoff the agent workflow
        result = crew.kickoff()
        return str(result)
    else:
        logger.info(f"[CrewAI Simulation] Processing message from {sender_name} in {space_display_name}: {message_text}")
        # Return a simulated agent response
        simulated_response = (
            f"🤖 [CrewAI Agent Response]\n"
            f"Hello {sender_name}! I am an agent drafted by CrewAI.\n"
            f"I analyzed your message: '{message_text}' from '{space_display_name}'.\n"
            f"Please configure your API keys (e.g., OPENAI_API_KEY or GEMINI_API_KEY) and "
            f"ensure CrewAI is fully installed to use live LLM responses."
        )
        return simulated_response
