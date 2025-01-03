from langchain_community.tools.tavily_search import TavilySearchResults


def get_profile_url_tavily(name: str) -> str:
    """
    Searches for a LinkedIn or Twitter profile page based on the provided name.

    Args:
        name (str): The name of the person or entity to search for.

    Returns:
        str: The search result, which could be a URL or a message indicating no results.

    Raises:
        ValueError: If the name parameter is empty or invalid.
    """
    if not name.strip():
        raise ValueError("The name parameter cannot be empty or whitespace.")

    search_query = f"{name}"  # Future flexibility for additional query parameters
    try:
        search = TavilySearchResults()
        result = search.run(search_query)
        if not result:
            return "No results found."
        return result
    except Exception as e:
        return f"An error occurred while searching: {str(e)}"
