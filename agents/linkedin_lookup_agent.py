from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from tools.tools import get_profile_url_tavily
from typing import Optional

# Load environment variables
load_dotenv()

# Constants
MODEL_NAME = "gpt-4o-mini"
PROMPT_TEMPLATE_TEXT = (
    "Given the full name {name_of_person}, I want you to provide a link to their LinkedIn profile page. "
    "Your answer should contain only a URL."
)

def lookup(name: str) -> Optional[str]:
    """
    Fetches the LinkedIn profile URL for the given name using LangChain agents.

    Args:
        name (str): Full name of the person to look up.

    Returns:
        Optional[str]: LinkedIn profile URL if found, None otherwise.

    Raises:
        ValueError: If the name is empty.
        RuntimeError: If the agent execution fails.
    """
    if not name.strip():
        raise ValueError("The name parameter cannot be empty or whitespace.")

    # Initialize ChatOpenAI with specified parameters
    llm = ChatOpenAI(
        temperature=0,
        model_name=MODEL_NAME,
    )

    # Create prompt template
    prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE_TEXT,
        input_variables=["name_of_person"],
    )

    # Define tools for the agent
    tools_for_agent = [
        Tool(
            name="Crawl Google for LinkedIn profile page",
            func=get_profile_url_tavily,
            description="Useful for retrieving LinkedIn page URLs.",
        )
    ]

    # Pull REACT prompt and create agent
    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    try:
        # Execute the agent with formatted input
        result = agent_executor.invoke(
            input={"input": prompt_template.format_prompt(name_of_person=name)}
        )
        return result.get("output", None)
    except Exception as e:
        raise RuntimeError(f"Agent execution failed: {e}")

if __name__ == "__main__":
    try:
        profile_url = lookup(name="Eden Marco Udemy")
        print(profile_url)
    except Exception as e:
        print(f"An error occurred: {e}")
