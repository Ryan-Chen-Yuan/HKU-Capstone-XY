
import os
import json
from openai import OpenAI

class SentimentService:
    """Sentiment analysis service to analyze message content and provide sentiment scores, mood, and suggestions."""

    def __init__(self, model="Meta-Llama-3.1-8B-Instruct"):
        """Initialize the sentiment analysis service.

        Args:
            model: OpenAI model name
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("BASE_URL"),
        )
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self):
        """Create the sentiment analysis prompt directly."""
        return """You are a sentiment analysis expert. Your task is to analyze the sentiment of the given messages and provide:
1. A mood intensity score (range: 0 to 10).
2. A mood category (e.g., happy, sad, angry, neutral).
3. The thinking (e.g., balanced, anxious, optimistic).
4. The scene related to the mood (e.g., work, home, social).

Respond in the following JSON format:
{
    "moodIntensity": <mood_intensity>,
    "moodCategory": "<mood_category>",
    "thinking": "<thinking>",
    "scene": "<scene>"
}
"""

    def analyze_sentiment(self, messages):
        """Analyze the sentiment of the given messages.

        Args:
            messages: List of messages to analyze.

        Returns:
            dict: Sentiment analysis results including moodIntensity, moodCategory, thinking, and scene.
        """
        try:
            # Format the input for the OpenAI API
            input_content = f"{self.prompt_template}\n\nMessages:\n" + "\n".join(
                [f"- {msg}" for msg in messages]
            )

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": input_content}],
                max_tokens=500,
                temperature=0.7,
            )

            # Parse the response
            result = response.choices[0].message.content.strip()
            return json.loads(result)

        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {
                "moodIntensity": 0.0,
                "moodCategory": "neutral",
                "thinking": "Balanced",
                "scene": "General",
            }