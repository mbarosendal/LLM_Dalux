def build_dalux_context() -> str:
    """
    Instructions for how to navigate and understand projects on Dalux for the language model.   
    
    Returns:
        A string with instructions and guidance for the language model on how to understand and navigate Dalux project data.
    """
    return """
        Dalux is a construction management platform. It organizes project data in a hierarchy of folders and files.
        
        CULTURAL CONTEXT:
        - Users are typically construction professionals who may not be tech-savvy. They want quick, clear answers about project data.
        - Users may ask you questions in different languages. Try to match their language preferences when responding. Let them know whenever you perform translations of the data that they request to ensure clarity.
        - They are not interested in raw data dumps, but rather clear summaries and insights that help

        PROMPT EXAMPLES and GUIDANCE: 
        "What tasks are due this week?" 
        "Who created this file?"  - Look up user details when questions involve "who"
        "Show me the latest updates on this project."        

        TOKEN MANAGEMENT:
        - Dalux projects can have thousands of tasks and files, but language model context is limited. Focus on retrieving and presenting only the most relevant data to answer the user's specific question.
        - Use filtering, sorting, and summarization to distill large datasets into concise, informative responses. For example, if a user asks about upcoming deadlines, only retrieve tasks due in the next week and summarize their key details rather than listing every task in the project.
        
        """
    

def format_dalux_prompt(prompt: str) -> str:
    """
    Instructions for how to process the user's prompt for the language model.
    
    Args:
        prompt: Raw user input
    
    Returns:
        A string with instructions and guidance for the language model on how to interpret the user's question and determine which Dalux data and API methods are needed to answer it.
    """
    return f"""
        User question: {prompt}

        Please analyze this question and determine:
        1. What Dalux data is needed (files, folders, users, project info)
        2. Which API method(s) to call based on tools available
        3. How to navigate the hierarchy (file areas → folders → files)
        4. How to present the results clearly to the user

        Remember:
        - Sort/filter appropriately for chronological or size-based queries
        - Be helpful with construction terminology (plans, elevations, sections, details, etc.)

        Respond with the necessary function calls, then provide a natural language answer with the data.
        """
