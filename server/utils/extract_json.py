import json
import re


def extract_json(text):
    """从文本中提取JSON内容

    Args:
        text: 包含JSON的文本

    Returns:
        dict: 提取的JSON对象，如果提取失败则返回None
    """
    if not text:
        return None
    
    # 方法1: 查找第一个 { 和最后一个 } 之间的内容
    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end > start:
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # 方法2: 使用正则表达式查找JSON块
    # 匹配以{开始，以}结束的完整JSON块
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            # 清理可能的格式问题
            cleaned_match = match.strip()
            return json.loads(cleaned_match)
        except json.JSONDecodeError:
            continue
    
    # 方法3: 尝试修复常见的JSON格式问题
    try:
        # 移除可能的markdown代码块标记
        cleaned_text = re.sub(r'```json\s*', '', text)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
        
        # 查找JSON内容
        start = cleaned_text.find("{")
        end = cleaned_text.rfind("}") + 1
        
        if start != -1 and end > start:
            json_str = cleaned_text[start:end]
            
            # 修复常见的JSON格式问题
            json_str = re.sub(r',\s*}', '}', json_str)  # 移除尾随逗号
            json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组尾随逗号
            
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # 方法4: 尝试从多行文本中逐行解析
    lines = text.split('\n')
    json_lines = []
    in_json = False
    brace_count = 0
    
    for line in lines:
        line = line.strip()
        if not in_json and line.startswith('{'):
            in_json = True
            json_lines = [line]
            brace_count = line.count('{') - line.count('}')
        elif in_json:
            json_lines.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                try:
                    json_str = '\n'.join(json_lines)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
                in_json = False
                json_lines = []
    
    print(f"Failed to extract JSON from text: {text[:200]}...")
    return None

