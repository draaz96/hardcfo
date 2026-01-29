import os
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from PIL import Image
from opik import track
from tools.models import AgentResponse
from dotenv import load_dotenv

load_dotenv()

class GeminiBrain:
    def __init__(self, model_name: str = "gemini-flash-latest"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.vision_model = genai.GenerativeModel("gemini-flash-latest") # or pro for vision too

    @track(name="gemini_brain.think")
    def think(
        self, 
        character: str, 
        context: str, 
        question: str, 
        response_format: str = "text"
    ) -> AgentResponse:
        """
        This is how agents THINK.
        """
        prompt = f"""
{character}

CURRENT SITUATION:
{context}

QUESTION FOR YOU:
{question}

Think through this step by step, then give your answer.
"""
        if response_format == "json":
            prompt += "\nYour final answer MUST be a valid JSON object."

        response = self.model.generate_content(prompt)
        full_text = response.text

        # Try to split thinking and final response
        thinking, final_answer = self._split_response(full_text)

        return AgentResponse(
            agent_name="GeminiBrain", # This will be overridden by the calling agent usually
            query=question,
            thinking=thinking,
            response=final_answer,
            confidence=0.9, # Placeholder, LLM doesn't natively return confidence unless asked
            needs_human_review=False,
            timestamp=datetime.now()
        )

    @track(name="gemini_brain.see_and_think")
    def see_and_think(
        self, 
        character: str, 
        image_path: str, 
        question: str
    ) -> AgentResponse:
        """
        For agents that need to look at images/documents.
        """
        try:
            img = Image.open(image_path)
            prompt = f"{character}\n\nQUESTION: {question}\n\nAnalyze this document and think step-by-step."
            
            # Using flash for faster vision processing if preferred, but pro is also good
            response = self.vision_model.generate_content([prompt, img])
            full_text = response.text
            
            thinking, final_answer = self._split_response(full_text)
            
            return AgentResponse(
                agent_name="GeminiVisionBrain",
                query=question,
                thinking=thinking,
                response=final_answer,
                confidence=0.85,
                needs_human_review=False,
                timestamp=datetime.now()
            )
        except Exception as e:
            return AgentResponse(
                agent_name="GeminiVisionBrain",
                query=question,
                thinking=f"Error processing image: {str(e)}",
                response="I encountered an error while trying to see the document.",
                confidence=0.0,
                needs_human_review=True,
                timestamp=datetime.now()
            )

    @track(name="gemini_brain.discuss")
    def discuss(
        self, 
        character: str, 
        conversation_history: List[Dict[str, str]], 
        new_message: str
    ) -> AgentResponse:
        """
        For ongoing conversations with context.
        """
        history_str = ""
        for msg in conversation_history:
            role = msg.get("role", "User")
            content = msg.get("content", "")
            history_str += f"{role}: {content}\n"

        prompt = f"""
{character}

CONVERSATION HISTORY:
{history_str}

USER MESSAGE:
{new_message}

Think step-by-step about the context, then respond.
"""
        response = self.model.generate_content(prompt)
        full_text = response.text
        
        thinking, final_answer = self._split_response(full_text)

        return AgentResponse(
            agent_name="GeminiChatBrain",
            query=new_message,
            thinking=thinking,
            response=final_answer,
            confidence=0.95,
            needs_human_review=False,
            timestamp=datetime.now()
        )

    def extract_json(self, response: str) -> dict:
        """
        Extracts JSON from response if present. Handles markdown code blocks.
        """
        try:
            # Look for markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # If no code block, try finding anything that looks like { ... }
            json_match = re.search(r'({.*})', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Fallback to direct parse
            return json.loads(response)
        except Exception:
            return {}

    def _split_response(self, text: str) -> tuple:
        """
        Splits the LLM output into 'thinking' and 'final response'.
        """
        # Look for common separators
        separators = [
            "\nFinal Answer:", 
            "\nResponse:", 
            "\nAnswer:", 
            "\nDecision:", 
            "\nAction:",
            "\nJSON:"
        ]
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                return parts[0].strip(), parts[1].strip()
        
        # If no explicit separator, if it's long, take the last paragraph as response
        paragraphs = text.strip().split("\n\n")
        if len(paragraphs) > 1:
            thinking = "\n\n".join(paragraphs[:-1])
            final_answer = paragraphs[-1]
            return thinking.strip(), final_answer.strip()
        
        return "Direct decision without detailed external thinking.", text.strip()
