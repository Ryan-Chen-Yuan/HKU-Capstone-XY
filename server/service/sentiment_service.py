#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self):
        """Load the sentiment analysis prompt template."""
        prompt_dir = os.path.join(os.path.dirname(__file__), "../prompt")
        os.makedirs(prompt_dir, exist_ok=True)

        prompt_file = os.path.join(prompt_dir, "sentiment_prompt.txt")

        # If the template file doesn't exist, create a default template
        if not os.path.exists(prompt_file):
            default_prompt = """You are a sentiment analysis expert. Your task is to analyze the sentiment of the given messages and provide:
1. A sentiment score (range: -1 to 1, where -1 is very negative, 0 is neutral, and 1 is very positive).
2. The overall mood (e.g., happy, sad, angry, neutral).
3. Suggestions for improving the mood if necessary.

Respond in the following JSON format:
{
    "score": <sentiment_score>,
    "mood": "<overall_mood>",
    "suggestions": "<suggestions>"
}
"""
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(default_prompt)

            return default_prompt

        # Read the template file
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def analyze_sentiment(self, messages):
        """Analyze the sentiment of the given messages.

        Args:
            messages: List of messages to analyze.

        Returns:
            dict: Sentiment analysis results including score, mood, and suggestions.
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
                "score": 0,
                "mood": "neutral",
                "suggestions": "Unable to analyze sentiment due to an error.",
            }
