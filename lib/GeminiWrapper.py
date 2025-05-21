"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
import google.generativeai as genai


class GeminiWrapper:
    """
    This is a simple helper class to interect with Gemini

    Example:
        
        >>> gwrapper = GeminiWrapper("Gemini_Api_Key","gemini-2.0-flash")
        >>> gwrapper.generateContent("Hello")
    """


    def __init__(self,API_KEY,model_name="gemini-2.0-flash"):
        """
        Ctor 

        Args:
            API_KEY (str): Gemini key api   
            model_name (str): Model name to use, default is "gemini-2.0-flash"     
        """
        try:
            self.MODEL_NAME = model_name
            self.FULL_MODEL_NAME = "models/"+self.MODEL_NAME
            self.model = None
            self.chat_session = None
            genai.configure(api_key=API_KEY, transport='rest')
            
        except Exception as e:
            print(f"GeminiWrapper::__init__ -> Exception: {e}")
            return f"Error {e}"

    def reset(self) -> None:
        """
        Reset model and chat session
        """
        self.model = None
        self.chat_session = None

    def createGenerationConfig(self,**kwargs):
        """
        Create an GenerationConfig based on argument in kwargs
        **kwargs (Keyword argumets) in a form of key-value
            
        Args:
            kwargs (dict[str,any]): 
        candidate_count: int | None = None,
        stop_sequences: Iterable[str] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        response_mime_type: str | None = None,
        response_schema: Schema | Mapping[str, Any] | type | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None
                                    
        Return:
            response (GenerationConfig): GenerationConfig type object
        """
        try:
            return genai.types.GenerationConfig(**kwargs)
        except Exception as e:
            print(f"GeminiWrapper::createGenerationConfig -> Exception: {e}")
    
    def generateContent(self,prompt:str,sys_instruction=None):
        """
        Send a prompt to Gemini

        Args:
            prompt (str): User prompt
            config (dict[str,any]): optionnal: -> Config to pass to Gemini
                                    candidate_count: int | None = None,
                                    stop_sequences: Iterable[str] | None = None,
                                    max_output_tokens: int | None = None,
                                    temperature: float | None = None,
                                    top_p: float | None = None,
                                    top_k: int | None = None,
                                    response_mime_type: str | None = None,
                                    response_schema: Schema | Mapping[str, Any] | type | None = None,
                                    presence_penalty: float | None = None,
                                    frequency_penalty: float | None = None

        Return:
            response (GenerateContentResponse): Full response of Gemini or None
        """
        response = None
        try:
            print(f"GeminiWrapper::prompt -> {prompt}")
            if self.model== None or self.model.model_name!=self.FULL_MODEL_NAME:
                if sys_instruction!= None:
                    self.model = genai.GenerativeModel(self.MODEL_NAME,
                                                       system_instruction=sys_instruction)
                else:
                    self.model = genai.GenerativeModel(self.MODEL_NAME)
            if prompt != None and len(prompt)>0:
                response = self.model.generate_content(prompt)
            else:
                print("GeminiWrapper::Invalid or empty prompt")

        except Exception as e:
            print(f"GeminiWrapper::generateContent -> Exception: {e}")
        return response

    def initChat(self,user_history_prompt:list=None):
        """
        Initialize the model "gemini-pro" if needed and start a chat with history if provided

        Args:
            user_history_prompt(list(dict)): History of the chat 
                                            [
                                                {"role": "user", "parts": "Hello"},
                                                {"role": "model", "parts": "Great to meet you. What would you like to know?"},
                                            ]
        Return
            True if chat is init, False otherwise
        """
        try:
            if self.model == None or self.model.model_name != self.FULL_MODEL_NAME:
                self.model = genai.GenerativeModel(self.MODEL_NAME)

            if user_history_prompt !=None and len(user_history_prompt)>0:
                self.chat_session = self.model.start_chat(
                    history=user_history_prompt
                    #history=[
                    #    {"role": "user", "parts": "Hello"},
                    #    {"role": "model", "parts": "Great to meet you. What would you like to know?"},
                    #]
                )
                print("init chat with history")
            else : 
                self.chat_session = self.model.start_chat()

                print("init chat without history")
            return True
        except Exception as e:
            print(f"GeminiWrapper::chat -> Exception : {e}")
           
            return False

    def chat(self,prompt:str):
        """
        Send a prompt to current chat session

        Args:
            prompt(str): user prompt to send

        Return:
            response(GenerateContentResponse): Gemini response

        """   
        response = None
        try:

            response = self.chat_session.send_message(prompt, stream=False)

        except Exception as e:
            print(f"GeminiWrapper::chat -> Exception : {e}")

        return response
    
    def getChatHistory(self):
        """
        Return the history of the current chat session

        Return:
            List(Content):  chat session history 
                            or None if not chat session exist
        """
        if self.chat_session !=None:
            return self.chat_session.history
        else:
            return None

