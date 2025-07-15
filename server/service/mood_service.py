import os
import json
from datetime import datetime
from openai import OpenAI

class MoodService:
    """Mood analysis service to analyze message content and provide mood scores, mood, and suggestions."""

    def __init__(self):
        """Initialize the mood analysis service.

        Args:
            model: OpenAI model name
        """
        self.model = os.environ.get("CHAT_MODEL_NAME")
        self.client = OpenAI(
            api_key=os.environ.get("CHAT_API_KEY"),
            base_url=os.environ.get("CHAT_BASE_URL"),
        )
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self):
        """Create the mood analysis prompt directly."""
        return """你是一名情绪分析专家。你的任务是基于用户提供的信息内容进行情绪分析，并用中文输出如下内容：
1. 情绪强度分数（范围：0 到 10）。
2. 情绪类别，类别示例包括但不限于：
开心
悲伤
生气
中性
忧郁
紧张
兴奋
惊讶
焦虑
空虚
烦躁
3.独白（例如：我真是一事无成）。
4. 与情绪相关的场景（例如：在朋友圈看到朋友的分享）。

注意事项：
请确保所有判断均仅依据输入的具体内容，客观、谨慎地提供所需分析结果。如果没有足够的信息来做出准确的判断，你可以说"未知"。

请按照下面的 JSON 格式进行回复：
{
    "moodIntensity": <情绪强度分数>,
    "moodCategory": "<情绪类别>",
    "thinking": "<独白>",
    "scene": "<场景>"
}
"""

    def analyze_mood(self, text=None, user_id=None, session_id=None, messages=None):
        """Analyze the mood of the given text or messages.

        Args:
            text: Single text to analyze (for API compatibility)
            user_id: User ID (for logging)
            session_id: Session ID (for logging)
            messages: List of messages to analyze (legacy support)

        Returns:
            dict: Mood analysis results including moodIntensity, moodCategory, thinking, and scene.
        """
        try:
            # Handle both single text and messages list
            if text is not None:
                # New API format: single text
                input_content = f"{self.prompt_template}\n\n用户输入:\n{text}"
            elif messages is not None:
                # Legacy format: messages list
                input_content = f"{self.prompt_template}\n\nMessages:\n" + "\n".join(
                    [f"- {msg}" for msg in messages]
                )
            else:
                raise ValueError("必须提供 text 或 messages 参数")

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": input_content}],
                max_tokens=500,
                temperature=0.7,
            )

            # Parse the response
            result = response.choices[0].message.content.strip()
            
            # 处理可能包含 ```json 标记的响应
            if result.startswith("```json"):
                # 提取 ```json 和 ``` 之间的内容
                start_marker = "```json"
                end_marker = "```"
                start_idx = result.find(start_marker) + len(start_marker)
                end_idx = result.find(end_marker, start_idx)
                if end_idx != -1:
                    result = result[start_idx:end_idx].strip()
                else:
                    # 如果没有结束标记，取开始标记之后的所有内容
                    result = result[start_idx:].strip()
            elif result.startswith("```"):
                # 处理其他代码块标记
                lines = result.split('\n')
                if len(lines) > 1:
                    result = '\n'.join(lines[1:-1])  # 去掉首尾的```行
            
            mood_result = json.loads(result)
            
            # Add metadata if provided
            if user_id or session_id:
                mood_result["user_id"] = user_id
                mood_result["session_id"] = session_id
                mood_result["timestamp"] = datetime.now().isoformat()
            
            return mood_result

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            print(f"原始响应: {result if 'result' in locals() else 'No response'}")
            return {
                "moodIntensity": 5.0,
                "moodCategory": "中性",
                "thinking": "无法分析",
                "scene": "未知",
                "error": "响应格式错误"
            }
        except Exception as e:
            print(f"Error analyzing mood: {str(e)}")
            return {
                "moodIntensity": 0.0,
                "moodCategory": "neutral",
                "thinking": "Balanced",
                "scene": "General",
                "error": str(e)
            }