import json


def extract_json(text):
    """从文本中提取JSON内容

    Args:
        text: 包含JSON的文本

    Returns:
        dict: 提取的JSON对象，如果提取失败则返回None
    """
    # 查找第一个 { 和最后一个 } 之间的内容
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        return None

    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None
