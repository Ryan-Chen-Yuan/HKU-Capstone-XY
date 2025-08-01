import os
import json
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
            timeout=45  # 增加超时时间
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

    def analyze_mood(self, messages):
        """Analyze the mood of the given messages.

        Args:
            messages: List of messages to analyze.

        Returns:
            dict: Mood analysis results including moodIntensity, moodCategory, thinking, and scene.
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
            
            # 尝试提取JSON内容（可能被包含在代码块中）
            if "```json" in result:
                # 提取JSON代码块
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                if json_end != -1:
                    result = result[json_start:json_end].strip()
            elif "```" in result:
                # 提取普通代码块
                json_start = result.find("```") + 3
                json_end = result.find("```", json_start)
                if json_end != -1:
                    result = result[json_start:json_end].strip()
            
            # 尝试解析JSON
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试修复常见问题
                print(f"JSON解析失败，原始响应: {result}")
                
                # 尝试查找JSON对象的开始和结束
                json_start = result.find("{")
                json_end = result.rfind("}")
                
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_content = result[json_start:json_end+1]
                    try:
                        return json.loads(json_content)
                    except json.JSONDecodeError:
                        pass
                
                # 如果还是失败，返回默认值
                raise Exception(f"无法解析AI响应为JSON格式: {result}")

        except Exception as e:
            print(f"Error analyzing mood: {str(e)}")
            return {
                "moodIntensity": 0.0,
                "moodCategory": "neutral",
                "thinking": "情绪分析暂时不可用",
                "scene": "一般场景",
            }