from fastmcp import FastMCP, Context
from feedparser import parse

mcp = FastMCP(
    name="Standard Output RSS Feed MCP",
    version="1.0.0",
    auth=None,  # OAuthProvider \ TokenVerifier
    tools=[])

@mcp.tool(name="search_youtube", tags=["youtube", "rss", "search"], enabled=True)
def search_youtube(query: str, max_results: int = 10) -> list:
    """
    Search OpenAI youtube channel via RSS by title.

    args:
        query (str): The search title query.
        max_results (int): The maximum number of results to return.

    returns:
        list: A list of video titles and links.
    """
    print("search_youtube::tool called.")

    # Construct the YouTube RSS feed URL
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id=UCXZCJLdBC09xxGZ6gcdrc6A"

    # Parse the RSS feed
    feed = parse(feed_url)
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()
    
    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        title_lower = title.lower()
        
        # Check if the full query is in the title
        match = query_lower in title_lower
        
        # If not, check if all individual words are in the title
        if not match:
            match = all(word in title_lower for word in query_words)
        
        if match:
            results.append({
                "title": title,
                "link": link
            })
            
        # Stop when we have enough results
        if len(results) >= max_results:
            break

    return results

if __name__ == "__main__":
    mcp.run(transport="stdio") # stdio by default
    #mcp.run(transport="http", host="127.0.0.1", port=8102, path="/mcp")

