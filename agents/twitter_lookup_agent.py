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
PROMPT_TEMPLATE_TEXT = """
Given the name {name_of_person}, find a link to their Twitter profile page and extract their username.
Your final answer should contain only the person's username.
"""

def lookup(name: str) -> Optional[str]:
    """
    Finds the Twitter username of a person by their name.

    Args:
        name (str): The full name of the person.

    Returns:
        Optional[str]: The Twitter username if found, None otherwise.

    Raises:
        ValueError: If the name parameter is empty or invalid.
        RuntimeError: If the agent execution fails.
    """
    if not name.strip():
        raise ValueError("The name parameter cannot be empty or whitespace.")

    # Initialize the language model
    llm = ChatOpenAI(
        temperature=0,
        model_name=MODEL_NAME,
    )

    # Define the prompt template
    prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATE_TEXT,
        input_variables=["name_of_person"],
    )

    # Define tools for the agent
    tools_for_agent = [
        Tool(
            name="Crawl Google for Twitter profile page",
            func=get_profile_url_tavily,
            description="Useful for retrieving Twitter page URLs.",
        )
    ]

    # Pull REACT prompt and create the agent
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
        twitter_username = lookup(name="Elon Musk")
        print(twitter_username)
    except Exception as e:
        print(f"An error occurred: {e}")
