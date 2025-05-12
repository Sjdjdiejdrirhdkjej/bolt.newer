
# mistral_model.py

from smolagents import Model
from mistralai import Mistral

class MistralModel(Model):
    def __init__(self, api_key: str, model: str = "mistral-small-latest"):
        self.client = Mistral(api_key=api_key)
        self.model_id = model

    def generate(self,
                 messages: list[dict[str, str]],
                 stop_sequences: list[str] | None = None):
        # Convert tool-related roles to supported roles
        formatted_messages = []
        for msg in messages:
            role = msg["role"].lower()
            if role == "tool-call":
                role = "assistant"
            elif role == "tool-response":
                role = "user"
            formatted_messages.append({
                "role": role,
                "content": msg["content"]
            })

        # Call Mistral chat completion endpoint
        response = self.client.chat.complete(
            model=self.model_id,
            messages=formatted_messages,
            stop=stop_sequences or []
        )

        return response.choices[0].message
