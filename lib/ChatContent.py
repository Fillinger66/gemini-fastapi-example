"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
class ChatContent:
    """
    This class serve to convert Gemini chat parts to List of object
"""
    role = None
    parts = None

    def __init__(self,role:str,parts:str):
        self.role = role
        self.parts = parts

    