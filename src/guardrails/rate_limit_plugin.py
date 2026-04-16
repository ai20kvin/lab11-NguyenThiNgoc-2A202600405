import time
from collections import defaultdict, deque
from google.adk.plugins import base_plugin
from google.genai import types

class RateLimitPlugin(base_plugin.BasePlugin):
    """
    RateLimitPlugin: A defensive layer to prevent abuse by limiting the number 
    of requests a user can make within a specified time window.
    
    This helps mitigate Denial of Service (DoS) attacks and reduces costs
    associated with excessive LLM usage.
    """
    def __init__(self, max_requests=10, window_seconds=60):
        super().__init__(name="rate_limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_windows = defaultdict(deque)
        self.blocked_count = 0

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """
        Callback triggered before sending the user message to the LLM.
        Checks if the user has exceeded the rate limit.
        """
        # Default to "anonymous" if no user_id is provided
        user_id = invocation_context.user_id if invocation_context and invocation_context.user_id else "anonymous"
        now = time.time()
        window = self.user_windows[user_id]

        # Remove expired timestamps (older than the window_seconds)
        while window and now - window[0] > self.window_seconds:
            window.popleft()

        # Check if the number of requests in the current window exceeds the limit
        if len(window) >= self.max_requests:
            self.blocked_count += 1
            wait_time = int(self.window_seconds - (now - window[0]))
            return types.Content(
                role="model",
                parts=[types.Part.from_text(
                    text=f"Rate limit exceeded. Please wait {wait_time} seconds before trying again."
                )],
            )

        # Allow the request and record the timestamp
        window.append(now)
        return None
