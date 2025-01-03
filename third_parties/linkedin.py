import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# Constants
API_ENDPOINT = "https://nubela.co/proxycurl/api/v2/linkedin"
EXCLUDED_KEYS = ["people_also_viewed", "certifications"]

def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = False) -> Dict[str, Any]:
    """
    Scrape information from LinkedIn profiles.

    Args:
        linkedin_profile_url (str): The LinkedIn profile URL to scrape.
        mock (bool): If True, uses a mock URL for testing. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary of scraped profile data.

    Raises:
        ValueError: If the API key is not set in the environment variables.
        requests.RequestException: If the HTTP request fails.
    """
    if mock:
        linkedin_profile_url = (
            "https://gist.githubusercontent.com/emarco177/0d6a3f93dd06634d95e46a2782ed7490/"
            "raw/78233eb934aa9850b689471a604465b188e761a0/eden-marco.json"
        )

    if not mock:
        api_key = os.getenv("PROXYCURL_API_KEY")
        if not api_key:
            raise ValueError("PROXYCURL_API_KEY is not set in the environment variables.")
        
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(
                API_ENDPOINT,
                params={"url": linkedin_profile_url},
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Error during API request: {e}")
    else:
        try:
            response = requests.get(linkedin_profile_url, timeout=10)
        except requests.RequestException as e:
            raise RuntimeError(f"Error during mock request: {e}")

    response.raise_for_status()  # Ensure HTTP errors are raised
    data = response.json()

    # Filter data
    data = {k: v for k, v in data.items() if v not in ([], "", None) and k not in EXCLUDED_KEYS}
    if "groups" in data:
        for group in data["groups"]:
            group.pop("profile_pic_url", None)  # Safely remove the key

    return data


if __name__ == "__main__":
    try:
        profile_data = scrape_linkedin_profile(
            linkedin_profile_url="https://www.linkedin.com/in/eden-marco/"
        )
        print(profile_data)
    except Exception as e:
        print(f"An error occurred: {e}")
