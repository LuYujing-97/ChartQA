
import os
import json
import base64
from openai import OpenAI
import requests
import random

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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


def process_json_file(input_file, output_file, model_name, image_dir):
    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 随机抽取60条记录

    # 为每种问题类型定义prompt模板
    prompts = {
        "Visual Question 1": "Given the following image and its caption, please answer the visual question: {question}\nCaption: {caption}, Answer within 10 words",
        "Visual Question 2": "Analyze the image and caption below, and provide an answer to the question: {question}\nCaption: {caption}, Answer within 10 words",
        "Data Retrieval Question": "Based on the provided caption and image, retrieve the relevant data to answer the question: {question}\nCaption: {caption}, Answer within 10 words",
        "Reasoning Question 1": "Use the information from the image and caption to reason and answer the following question: {question}\nCaption: {caption}, Answer within 20 words",
        "Reasoning Question 2": "With the given image and caption, please think logically and provide an answer to the question: {question}\nCaption: {caption}, Answer within 20 words",
        "Chart Description": "Describe the chart shown in the image and explain it based on the caption: {question}\nCaption: {caption}, Answer within 100 words",
        "Chart Summarization": "Summarize the key points of the chart in the image, considering the caption: {question}\nCaption: {caption}, Ref: {ref}, Answer within 100 words",
        "Reasoning Question with Background": "Using the background information from the caption and the image, answer the following reasoning question: {question}\nCaption: {caption}, Ref: {ref}, Answer within 50 words"
    }

    # 处理每条记录
    for record in data:
        image_path = f"{image_dir}/{record['filename']}"  # 根据filename生成图片路径
        caption = record.get('caption', '')  # 获取caption
        ref = record.get('ref', '')  # 获取ref

        for question_type, qa_pair in record['generated_contents'].items():
            # 检查qa_pair是否包含"Question:"和"Answer:"
            if "Question:" in qa_pair and "Answer:" in qa_pair:
                question = qa_pair.split("Question:")[1].split("Answer:")[0].strip()
                if question:
                    # 根据question_type获取相应的prompt模板，并填充内容
                    prompt_template = prompts.get(question_type, "Answer the question based on the image and caption: {question}\nCaption: {caption}")
                    prompt = prompt_template.format(question=question, caption=caption, ref=ref)
                    answer = closeAI(model_name, image_path, prompt)
                    record['generated_contents'][question_type] = f"Question: {question} Answer: {answer}"
            # else:
            #     print(f"Warning: Missing 'Question:' or 'Answer:' in {question_type} of record ID {record['id']}")

    # 将处理后的数据写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# 使用示例
model_name = 'claude-3-5-sonnet-20240620'
input_file = './sampled_output/sampled_output_file_single.json'
output_file = './Claude-3-5-result/output_single_claude-3-5_all.json'
image_dir = './benchmark_single/single'
process_json_file(input_file, output_file, model_name, image_dir)