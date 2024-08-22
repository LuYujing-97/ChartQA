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
    
    output_file = json_file.replace('.json', '_updated_claude_multi_all.json')
    # output_file = json_file.replace('.json', '_updated_gpt4_single_2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in output_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 定义 JSON 文件路径和基础图片路径
json_file = './multi/multi_lu.jsonl'
# json_file = './singlt_test_update_lu.jsonl'
base_image_path = './multi/multi'
# base_image_path = './subject/subject/astro-ph.IM/'
# 定义不同的模板
templates = {
    'generated_questions': """Role: You are an AI visual assistant who can analyze a scientific paper graph.

Task: You are provided with an image and its caption. Generate eight questions based solely on the provided image and information, and provide corresponding answers for each question. For each question, provide the following:

Question: The question itself.
Answer: The final, concise answer.
Requirements:

Visual Questions (2): The questions should focus on the visual aspects of the chart, including elements such as colors, text, formulas, and chart types. Avoid questions involving maximum or minimum values, and aim for questions related to the analysis of chart elements. Answers should be within 10 words.

Data Retrieval Question (1): The question should require retrieving specific data points or ranges from the chart. Avoid questions involving maximum or minimum values. Answers should be within 10 words.

Reasoning Questions (4): These questions require numerical calculations, comparisons, and other information that cannot be directly obtained from the image. Two questions should involve comparisons between multiple images. Only ask questions that you can clearly answer yourself. Answers should be within 20 words.

Chart Description (1): Generate a chart description that aims at presenting all the visual elements of the plot. Answers should be within 100 words.
Example Questions and Answers:

Visual Question 1:

Question: What color represents the progenitor stars with metallicity Z=0.013-0.02 in the graph?
Answer: Pink or light purple.
Visual Question 2:

Question: What type of chart is used in the image?
Answer: Line chart.
Data Retrieval Question:

Question: What is the metallicity range labeled as "Z:0.013-0.02"?
Answer: Z=0.013-0.02.
Reasoning Question 1:

Question: Comparing the two charts, which shows a stronger correlation between X and Y variables?
Answer: The left chart shows a stronger correlation.
Reasoning Question 2:

Question: Based on the trends in both panels, how does the data suggest the relationship between metallicity and star formation rate?
Answer: Higher metallicity generally correlates with a lower star formation rate.
Reasoning Question 3:

Question: How does the pink curve compare to the blue curve at Z=0.02?
Answer: The pink curve is higher.
Reasoning Question 4:

Question: Calculate the difference in slope between the green and red lines.
Answer: Green line has a steeper slope.
Chart Description:

Question: Describe the chart.
Answer: The chart displays several colored lines representing different metallicity ranges of progenitor stars. Each line is labeled in the legend, with colors including pink, blue, green, and red. The X-axis represents metallicity values, and the Y-axis represents an unspecified variable. The lines show trends and variations in the data across the metallicity spectrum.
Caption: {caption}
END_OF_INSTRUCTIONS""",
}



# 更新 JSON 文件
update_json_file(json_file, base_image_path, templates, "claude-3-5-sonnet-20240620")
# update_json_file(json_file, base_image_path, templates, "gpt-4o")
# update_json_file(json_file, base_image_path, templates, "gpt-4o-mini")
