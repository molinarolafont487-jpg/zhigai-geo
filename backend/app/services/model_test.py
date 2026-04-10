import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / '.env')

API_KEY = os.getenv('ARK_API_KEY', '').strip()
BASE_URL = 'https://ark.cn-beijing.volces.com/api/v3'
MODELS = [
    'doubao-seed-2-0-lite',
    'doubao-seed-2-0-pro',
    'doubao-seed-1-8',
    'doubao-seed-2-0-250821',
    'doubao-pro-32k',
    'doubao-lite-32k',
]


def extract_text(response):
    try:
        return response.choices[0].message.content.strip()
    except Exception:
        return str(response)


def main():
    if not API_KEY:
        print('❌ 未找到 ARK_API_KEY')
        return

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    prompt = '你好，请用一句中文介绍你自己。'

    print('开始模型探测...')
    for model in MODELS:
        print(f'\n=== 测试模型: {model} ===')
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.2,
            )
            text = extract_text(response)
            print('✅ 调用成功')
            print(f'模型: {model}')
            print(f'返回片段: {text[:200]}')
            return
        except Exception as exc:
            print(f'❌ 调用失败: {exc}')

    print('\n所有候选模型均不可用。')


if __name__ == '__main__':
    main()
