import os
import json
import base64
from openai import OpenAI
import requests

# # 设置代理环境变量
# os.environ["http_proxy"] = "http://10.105.20.64:7890"
# os.environ["https_proxy"] = "http://10.105.20.64:7890"

def closeAI(model_name, image_path, question):
    from openai import OpenAI

    api_key = 'sk-Ee0f5EaLhGBg9SjeKmTBGG0J0Y6w2zBVmiK2Sqx2QdY0XFvZ'

    base64_image = encode_image(image_path)

    if model_name.startswith('gpt'):
        client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key=api_key,
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            model=model_name,
        )
        # print(chat_completion)
        generated_content = chat_completion.choices[0].message.content
    else:
        url = "https://api.openai-proxy.org/anthropic/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": model_name,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ],
                }
            ],
        }

        response = requests.post(url, headers=headers, json=data)
        generated_content = response.json()['content'][0]['text']
        # print(response.json())
    
    # 提取生成的内容

    
    return generated_content

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_templates(image_path, templates, model_name, caption, ref, title):
    results = {}
    for key, template in templates.items():
        question = template.format(caption=caption, ref=ref, title=title)
        results[key] = closeAI(model_name, image_path, question)
    return results

def update_json_file(json_file, base_image_path, templates, model_name):
    output_data = []

    with open(json_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                
                image_path = os.path.join(base_image_path, data['filename'])
                caption = data.get('caption', '')
                ref = data.get('ref', '')
                title = data.get('title', '')
                # 检查 ref 是否为空，如果为空则跳过
                if not ref:
                    print(f"Skipping file due to empty 'ref': {data['filename']}")
                    continue

                generated_contents = process_templates(image_path, templates, model_name, caption, ref, title)
                data['generated_contents'] = generated_contents

                output_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line.strip()}")
                print(f"Error message: {e}")
            except Exception as e:
                print(f"Error processing data: {e}")
    
    output_file = json_file.replace('.json', '_updated_multi_reasoning.json')
    # output_file = json_file.replace('.json', '_updated_gpt4_single_2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in output_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 定义 JSON 文件路径和基础图片路径

# base_image_path = './benchmark_single/single'
json_file = './benchmark_multi/multi_lu.jsonl'
base_image_path = './benchmark_multi/multi'



#Chart_Summarization
# templates = {
#     'Chart_Summarization': """Role: You are an AI visual assistant who can analyze a scientific paper graph. 
# Task: You are provided with an image, its caption, its description, and the paper's title. Generate a chart summarization that aims at summarizing the trend-like or high-level characteristics from the plot.
# Requirements: The answer should be within 100 words, should be as related to the image as possible, and should clearly differentiate from a simple chart description by providing a more macro-level summary. If applicable, compare and summarize across multiple images, highlighting overall patterns and differences. The output should be in paragraph format, not a list.
# Caption: {caption}
# Des: {ref}
# Title: {title}
# END_OF_INSTRUCTIONS"""
# }
#background_reasoning
templates = {
    'reasoning_questions': """Role: You are an AI visual assistant who can analyze a scientific paper graph. 
Task: You are provided with an image, its caption and its description. Generate one Reasoning question based solely on the provided image and information. For each question, provide the following:
Question: The question itself.
Answer: The final, concise answer.
Requirements: 
These questions require a certain level of astronomical background and needs to involve some analysis.
Only ask questions that you can clearly answer yourself. Answers should be within 50 words.
Caption: {caption}
Des: {ref}
END_OF_INSTRUCTIONS"""
}
# templates_multi = {
#     'reasoning_questions': """Role: You are an AI visual assistant who can analyze a scientific paper graph. 
# Task: You are provided with an image and its caption. Generate four Reasoning questions based solely on the provided image and information. For each question, provide the following:
# Question: The question itself.
# Answer: The final, concise answer.
# Requirements:
# These question require numerical calculations, comparisons, and other information that cannot be directly obtained from the image. 
# Tow questions should involve comparisons between multiple images. Only ask questions that you can clearly answer yourself. Answers should be within 20 words.
# Caption: {caption}
# Des: {ref}
# END_OF_INSTRUCTIONS"""
# }

# 更新 JSON 文件
update_json_file(json_file, base_image_path, templates, "claude-3-5-sonnet-20240620")
# update_json_file(json_file, base_image_path, templates, "gpt-4o")
# update_json_file(json_file, base_image_path, templates, "gpt-4o-mini")
