



def format_dalux_query(prompt: str) -> str:
    """
    Formats the user's query for the AI with Dalux context.
    
    Args:
        prompt: Raw user input
    
    Returns:
        Formatted query with guidance
    """
    return f"""
User question: {prompt}

Please analyze this question and determine:
1. What Dalux data is needed (files, folders, users, project info)
2. Which API method(s) to call based on tools available
3. How to navigate the hierarchy (file areas → folders → files)
4. How to present the results clearly to the user

Remember:
- Use find_folder_by_name() when user mentions a folder name
- Use find_files_by_name() when searching for specific files
- Look up user details when questions involve "who"
- Sort/filter appropriately for chronological or size-based queries
- Inform user if results are limited due to token management

Respond with the necessary function calls, then provide a natural language answer with the data.
"""