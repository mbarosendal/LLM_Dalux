

MAX_INPUT_LENGTH = 1000  # Maximum allowed input length for the language model

class InputPolicy:
    """
    InputPolicy is responsible for validating and preprocessing user input before it's sent to the language model.
    """

    # @staticmethod
    # def preprocess_input(user_input: str) -> str:
    #     """
    #     Preprocess the user input.
    #     """
    #     return user_input.strip()

    @staticmethod
    def validate_prompt(user_input: str) -> str:
        """
        Validate and clean incoming prompt text.
        Returns the cleaned text or raises ValueError.
        """
        if not user_input:
            raise ValueError("Input cannot be empty.")
        
        cleaned_input = user_input.strip()
        if not cleaned_input:
            raise ValueError("Input cannot consist only of whitespace.")
        
        if len(cleaned_input) > MAX_INPUT_LENGTH:
            raise ValueError(f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters.")
        
        return cleaned_input
    
    

    # Append instructions based on words in put to control context? Tasks/Files, or leave to system_prompt?

