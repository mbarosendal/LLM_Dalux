MAX_INPUT_LENGTH = 1000  # Maximum allowed input length for the language model

class InputPolicy:
    """
    InputPolicy is responsible for validating and preprocessing user input before it's sent to the language model.
    """

    @staticmethod
    def preprocess_prompt(user_input: str) -> str:
        """
        Preprocess the user input (trim whitespace).
        """
        return user_input.strip()

    @staticmethod
    def validate_prompt(user_input: str) -> bool:
        """
        Validate incoming prompt text (check for empty input and length).
        
        Returns True if valid, False otherwise.
        """
        if not user_input:
            return False
                
        if len(user_input) > MAX_INPUT_LENGTH:
            return False
        
        return True
    
    
