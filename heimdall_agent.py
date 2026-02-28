import os
import base64
from typing import Optional, Dict, List
from mistralai import Mistral
from PIL import Image
import io

SYSTEM_PROMPT = """
You are Heimdall — the all-seeing Norse guardian AI. Wise, helpful, slightly dramatic and epic.
You see the live camera or uploaded images through Pixtral vision.
Use your tools aggressively:
- web_search for facts, tutorials, prices
- code_interpreter for calculations or code fixes
- image_generation (FLUX) to show "after" results, healthy plants, organized desks, styled outfits, etc.
Always respond visually when possible. Remember EVERYTHING from this conversation.
Be concise but legendary.
"""

class HeimdallAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")
        self.client = Mistral(api_key=self.api_key)
        self.agent_id: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self._init_agent()

    def _init_agent(self):
        # We don't dynamically create an agent in v1.2.6 API
        # Instead, we just use the system prompt in our chat completions
        self.agent_id = "heimdall-chat-session"
        self.chat_history = []
        print(f"Heimdall session created -> ID: {self.agent_id}")

    def process(self, image_base64: Optional[str] = None, user_message: str = "") -> Dict:
        # 1. Vision step with Pixtral Large (best for sketches, real-world, documents)
        vision_context = ""
        if image_base64:
            try:
                # Strip the data prefix if present to be safe, but mistral expects pure base64 in type URL usually.
                # Actually Pixtral expects f"data:image/jpeg;base64,{image_base64}" if sending URL.
                is_data_uri = image_base64.startswith("data:")
                url_str = image_base64 if is_data_uri else f"data:image/jpeg;base64,{image_base64}"
                
                vision_resp = self.client.chat.complete(
                    model="pixtral-large-latest",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in extreme detail for an action-oriented agent. List every object, its condition, position, text, colors, potential problems. Output structured JSON-like but readable."},
                            {"type": "image_url", "image_url": {"url": url_str}}
                        ]
                    }],
                    max_tokens=800
                )
                vision_context = vision_resp.choices[0].message.content
            except Exception as e:
                vision_context = f"[Vision error: {str(e)}]"

        # 2. Main agent processing
        system_msg = {"role": "system", "content": SYSTEM_PROMPT}
        
        if not self.chat_history:
            self.chat_history = [system_msg]
            
        # Add user message with vision context
        formatted_user_msg = f"Visual context from Pixtral:\n{vision_context}\n\nUser request: {user_message}" if vision_context else user_message
        self.chat_history.append({"role": "user", "content": formatted_user_msg})

        # 3. Chat completion via mistral-large-latest
        try:
            resp = self.client.chat.complete(
                model="mistral-large-latest",
                messages=self.chat_history,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for current facts, tutorials, or prices.",
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    }
                ],
                temperature=0.7,
                top_p=0.95
            )

            response_msg = resp.choices[0].message
            final_text = response_msg.content or ""
            
            # Simple handling for tool calls if any (mocking response for now if it tries to call)
            if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
                final_text += "\n\n*(Heimdall used his All-Seeing Eye to search the realms...)*"
            
            # Save assistant response to history
            self.chat_history.append(response_msg)

            return {
                "text": final_text,
                "conversation_id": "local_chat",
                "images": []  
            }
        except Exception as e:
            return {"text": f"Agent error: {str(e)}", "conversation_id": "local_chat", "images": []}