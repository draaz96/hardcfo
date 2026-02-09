import os
import json
import re
import time
import random
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

    def _generate_with_retry(self, func, *args, **kwargs):
        """
        Execute a generation function with exponential backoff retry.
        """
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check for rate limit errors (429) or Service Unavailable (503)
                error_str = str(e).lower()
                if "429" in error_str or "resource exhausted" in error_str or "503" in error_str:
                    if attempt == max_retries - 1:
                        raise e
                    
                    # Exponential backoff with jitter
                    delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    print(f"⚠️ Rate limit hit. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    raise e
                    
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

        response = self._generate_with_retry(self.model.generate_content, prompt)
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
        Supports Images (via PIL) and PDFs (via PyPDF2 text extraction).
        """
        try:
            # Check file extension
            is_pdf = image_path.lower().endswith('.pdf')
            content_input = []
            
            if is_pdf:
                # Always use PyPDF2 for PDFs as requested
                print(f"📄 Extracting text from PDF (PyPDF2): {image_path}")
                import PyPDF2
                text_content = ""
                with open(image_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content += extracted + "\n"
                
                # Append extracted text to the question/prompt
                question = f"{question}\n\nDOCUMENT CONTENT:\n{text_content[:30000]}" # Limit to ~30k chars
                # content_input remains empty as we put text in prompt
                
                # Use standard model for text processing since there's no image
                model_to_use = self.model 
            else:
                # Handle Image with Vision Model
                img = Image.open(image_path)
                content_input = [img]
                model_to_use = self.vision_model

            prompt = f"{character}\n\nQUESTION: {question}\n\nAnalyze this document and think step-by-step."
            
            # Call Gemini
            response = self._generate_with_retry(model_to_use.generate_content, [prompt, *content_input])
            
            if not response.parts:
                 raise ValueError("Gemini returned an empty response.")

            full_text = response.text
            
            thinking, final_answer = self._split_response(full_text)
            
            return AgentResponse(
                agent_name="GeminiVisionBrain" if not is_pdf else "GeminiTextBrain",
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
                thinking=f"Error processing document: {str(e)}",
                response=f"I encountered an error while trying to read the document: {str(e)}",
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
        response = self._generate_with_retry(self.model.generate_content, prompt)
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

    @track(name="gemini_brain.log_feedback")
    def log_feedback(self, feedback_type: str, score: float, comments: str) -> dict:
        """
        Log human feedback to Opik as a distinct event.
        """
        return {
            "feedback_type": feedback_type,
            "score": score,
            "comments": comments,
            "timestamp": datetime.now()
        }

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
