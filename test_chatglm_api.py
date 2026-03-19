#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

import requests

def test_chatglm_api():
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    api_key = os.getenv("CHATGLM_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 CHATGLM_API_KEY 环境变量")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # 测试题目解析
    parse_data = {
        "model": "glm-4.6",
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的教育分析师，擅长分析各类学科题目。你必须只输出纯 JSON 格式，不要添加任何 markdown 标记或其他文字。",
            },
            {
                "role": "user",
                "content": "你是一位经验丰富的教师，请分析以下题目：\n\n题目：求解方程：2x + 3 = 7\n\n请按以下 JSON 格式输出分析结果（只输出 JSON，不要添加 markdown 代码块标记或其他内容）：\n\n{\n    \"type\": \"题目类型（选择/填空/解答/判断）\",\n    \"subject\": \"所属学科\",\n    \"knowledgePoints\": [\"知识点1\", \"知识点2\"],\n    \"difficulty\": \"难度等级（简单/中等/困难）\",\n    \"prerequisites\": [\"前置知识1\", \"前置知识2\"]\n}"
            },
        ],
        "temperature": 0.1,
        "max_tokens": 1600,
    }
    
    print("Testing problem parsing...")
    try:
        response = requests.post(url, headers=headers, json=parse_data, timeout=60)
        print(f"Status code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试解答生成
    solve_data = {
        "model": "glm-4.6",
        "messages": [
            {
                "role": "system",
                "content": "你是一位优秀的 AI 教师。你必须只输出纯 JSON，禁止输出 markdown 代码块和额外说明。JSON 字段内容允许 Markdown 与 LaTeX。",
            },
            {
                "role": "user",
                "content": "你是一位耐心的 AI 教师，请为学生提供详细解答。\n\n题目：求解方程：2x + 3 = 7\n\n题目类型：解答\n所属学科：数学\n知识点：一元一次方程、等式的性质、移项\n难度等级：简单\n\n请严格输出 JSON（不要 markdown 代码块、不要额外说明），字段必须齐全：\n\n{\n    \"thinking\": \"解题思路（1-3段）\",\n    \"steps\": [\"步骤1\", \"步骤2\", \"步骤3\"],\n    \"answer\": \"最终答案（简洁明确）\",\n    \"summary\": \"知识总结（可迁移的方法与易错点）\"\n}\n\n要求：\n1. steps 必须是字符串数组，至少 2 步；\n2. answer 只保留最终结论，不要重复完整推导；\n3. summary 必须总结方法与易错点，不要留空；\n4. thinking / steps / summary 请使用清晰的 Markdown 结构（如标题、列表、加粗）；\n5. 涉及数学表达式时，使用 LaTeX：行内用 $...$，独立公式用 $$...$$；\n6. 仅输出合法 JSON，字段值中的换行必须按 JSON 字符串格式正确转义。"
            },
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    
    print("Testing solution generation...")
    try:
        response = requests.post(url, headers=headers, json=solve_data, timeout=60)
        print(f"Status code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chatglm_api()
