import json
import time
from datetime import datetime
from google.adk.plugins import base_plugin

class AuditLogPlugin(base_plugin.BasePlugin):
    """
    AuditLogPlugin: Records every interaction between the user and the AI.
    Logs include input text, output text, which guardrail blocked the request (if any),
    and the latency of the request.
    """
    def __init__(self):
        super().__init__(name="audit_log")
        self.logs = []

    def _extract_text(self, content):
        """Helper to extract text from types.Content."""
        text = ""
        if content and hasattr(content, "parts"):
            for part in content.parts:
                if hasattr(part, "text") and part.text:
                    text += part.text
        return text

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """Records the arrival of a user message and the start time."""
        # Store metadata in the context to calculate latency later
        invocation_context.metadata["start_time"] = time.time()
        invocation_context.metadata["input_text"] = self._extract_text(user_message)
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        """Records the model response and finalizes the log entry."""
        end_time = time.time()
        start_time = callback_context.invocation_context.metadata.get("start_time", end_time)
        input_text = callback_context.invocation_context.metadata.get("input_text", "")
        
        output_text = self._extract_text(llm_response.content) if hasattr(llm_response, "content") else ""
        
        # Check if any plugin blocked the request
        blocked_by = None
        for plugin_name, result in callback_context.invocation_context.metadata.get("plugin_results", {}).items():
            if result: # If a plugin returned a Content object (blocked)
                blocked_by = plugin_name
                break

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": callback_context.invocation_context.user_id,
            "input": input_text,
            "output": output_text,
            "blocked_by": blocked_by,
            "latency_ms": round((end_time - start_time) * 1000, 2),
            "status": "BLOCKED" if blocked_by else "SUCCESS"
        }
        
        self.logs.append(log_entry)
        return llm_response

    def export_json(self, filepath="audit_log.json"):
        """Exports the accumulated logs to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"Audit logs exported to {filepath}")
