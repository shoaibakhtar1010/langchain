from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
from third_parties.linkedin import scrape_linkedin_profile
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent
from agents.twitter_lookup_agent import lookup as twitter_lookup_agent
from third_parties.twitter import scrape_user_tweets
from typing import Optional


def ice_break_with(name: str) -> Optional[str]:
    """
    Generates an icebreaker summary using LinkedIn and Twitter data for a given person.

    Args:
        name (str): The full name of the person.

    Returns:
        Optional[str]: A generated summary with interesting facts, or None if an error occurs.

    Raises:
        ValueError: If the name is empty or invalid.
        RuntimeError: If any data fetching operation fails.
    """
    if not name.strip():
        raise ValueError("The name parameter cannot be empty or whitespace.")

    try:
        # Fetch LinkedIn profile and data
        linkedin_username = linkedin_lookup_agent(name=name)
        linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_username)

        # Fetch Twitter username and latest tweets
        twitter_username = twitter_lookup_agent(name=name)
        tweets = scrape_user_tweets(username=twitter_username)

        # Define the prompt template
        summary_template = """
        Given the information about a person from LinkedIn: {information},
        and their latest Twitter posts: {twitter_posts}, create:
        1. A short summary.
        2. Two interesting facts about them.

        Use both LinkedIn and Twitter data in your response.
        """
        summary_prompt_template = PromptTemplate(
            input_variables=["information", "twitter_posts"],
            template=summary_template.strip(),
        )

        # Initialize the language model
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

        # Create and execute the chain
        chain = summary_prompt_template | llm
        result = chain.invoke(input={"information": linkedin_data, "twitter_posts": tweets})

        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    load_dotenv()

    print("Ice Breaker Generator Initialized")
    try:
        icebreaker = ice_break_with(name="Harrison Chase")
        if icebreaker:
            print("Generated Icebreaker:")
            print(icebreaker)
        else:
            print("Failed to generate an icebreaker.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")
