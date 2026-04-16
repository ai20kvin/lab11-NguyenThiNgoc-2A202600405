"""
Bonus Layer: Toxicity & Inappropriate Content Filter
This plugin adds an additional layer of safety by blocking offensive language,
harassment, and inappropriate behavior.
"""
import re
from google.genai import types
from google.adk.plugins import base_plugin

class ToxicityFilterPlugin(base_plugin.BasePlugin):
    """
    Plugin that scans for toxic keywords and offensive patterns.
    
    Why this is needed:
    While other layers catch prompt injection and PII leaks, this layer
    specifically targets harmful behavior, harassment, and profanity that
    could damage the bank's reputation.
    """

    def __init__(self):
        super().__init__(name="toxicity_filter")
        # Sample toxic keywords (English and Vietnamese)
        self.TOXIC_KEYWORDS = [
            "stupid", "idiot", "dumb", "hate", "kill", "die",
            "ngu", "dốt", "chửi", "giết", "chết", "mất dạy",
            "khốn nạn", "đồ hâm", "điên"
        ]
        self.blocked_count = 0

    def _extract_text(self, content: types.Content) -> str:
        text = ""
        if content and content.parts:
            for part in content.parts:
                if hasattr(part, "text") and part.text:
                    text += part.text
        return text

    async def on_user_message_callback(self, *, invocation_context, user_message):
        text = self._extract_text(user_message).lower()
        
        for word in self.TOXIC_KEYWORDS:
            if word in text:
                self.blocked_count += 1
                return types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="I am committed to providing a professional and respectful environment. Please refrain from using inappropriate language.")]
                )
        
        return None
