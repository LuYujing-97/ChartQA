#会有乱码情况出现，还没有完全调整好，可以先用API_compare.py
import json
import random
import requests
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_openAI_response(api_key, model_name, prompt, image_path=None, temperature=0.1, max_tokens=512):
    url = 'https://api2.road2all.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    content = [{"type": "text", "text": prompt}]
    
    if image_path is not None:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
            }
        })
    
    data = {
        "model": model_name,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()['choices'][0]['message']['content']
    return result

def process_json_file(input_file, output_file, api_key, model_name, image_dir):
    # 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 定义每种问题类型的prompt模板
    prompts = {
        "Visual and Reasoning Group": (
            "Given the following image and its caption, please answer the following questions:\n"
            "1. Visual Question 1: {vq1} (Answer within 10 words)\n"
            "2. Visual Question 2: {vq2} (Answer within 10 words)\n"
            "3. Data Retrieval Question: {drq} (Answer within 10 words)\n"
            "4. Reasoning Question 1: {rq1} (Answer within 20 words)\n"
            "5. Reasoning Question 2: {rq2} (Answer within 20 words)\n"
            "6. Chart Description: {cd} (Answer within 100 words)\n"
            "Caption: {caption}"
        ),
        "Chart and Background Group": (
            "Given the following image, its caption, and the reference information, please answer the following questions:\n"
            "1. Chart Summarization: {cs} (Answer within 100 words)\n"
            "2. Reasoning Question with Background: {rqb} (Answer within 50 words)\n"
            "Caption: {caption}\n"
            "Reference: {ref}"
        )
    }

    # 处理每条记录
    for record in data:
        image_path = f"{image_dir}/{record['filename']}"  # 根据filename生成图片路径
        caption = record.get('caption', '')  # 获取caption
        ref = record.get('ref', '')  # 获取ref

        # 构建 Visual 和 Reasoning 相关问题的 prompt
        question_keys = ["Visual Question 1", "Visual Question 2", "Data Retrieval Question", 
                         "Reasoning Question 1", "Reasoning Question 2", "Chart Description"]
        question_answers = []

        for key in question_keys:
            question = record['generated_contents'].get(key, "")
            if "Question:" in question and "Answer:" in question:
                question_text = question.split("Question:")[1].split("Answer:")[0].strip()
                question_answers.append((key, question_text))
            else:
                question_answers.append((key, ""))  # 如果问题为空或格式不正确，则设置为空字符串

        # 生成 prompt 并进行 API 调用
        if any([q for _, q in question_answers]):
            visual_and_reasoning_prompt = prompts["Visual and Reasoning Group"].format(
                vq1=question_answers[0][1], vq2=question_answers[1][1], drq=question_answers[2][1], 
                rq1=question_answers[3][1], rq2=question_answers[4][1], cd=question_answers[5][1], caption=caption
            )
            visual_and_reasoning_answer = get_openAI_response(api_key, model_name, visual_and_reasoning_prompt, image_path=image_path)
            visual_and_reasoning_answers = visual_and_reasoning_answer.split('\n')

            # 将答案按顺序分配给对应的问题
            for i, (key, question_text) in enumerate(question_answers):
                if question_text:  # 只处理非空的问题
                    try:
                        answer = visual_and_reasoning_answers[i].split(':')[-1].strip() if len(visual_and_reasoning_answers) > i else ""
                        record['generated_contents'][key] = f"Question: {question_text} Answer: {answer}"
                    except IndexError:
                        print(f"Error processing {key} for record ID: {record['id']}")
                        record['generated_contents'][key] = f"Question: {question_text} Answer: N/A"
        
        # 构建 Chart Summarization 和 Reasoning Question with Background 的 prompt
        cs = record['generated_contents'].get("Chart Summarization", "").split("Question:")[1].split("Answer:")[0].strip() if "Question:" in record['generated_contents'].get("Chart Summarization", "") else ""
        rqb = record['generated_contents'].get("Reasoning Question with Background", "").split("Question:")[1].split("Answer:")[0].strip() if "Question:" in record['generated_contents'].get("Reasoning Question with Background", "") else ""

        if cs or rqb:
            chart_and_background_prompt = prompts["Chart and Background Group"].format(
                cs=cs, rqb=rqb, caption=caption, ref=ref
            )
            chart_and_background_answer = get_openAI_response(api_key, model_name, chart_and_background_prompt, image_path=image_path)
            chart_and_background_answers = chart_and_background_answer.split('\n')

            # 将答案按顺序分配给对应的问题
            if cs:
                record['generated_contents']["Chart Summarization"] = f"Question: {cs} Answer: {chart_and_background_answers[0].split(':')[-1].strip() if len(chart_and_background_answers) > 0 else ''}"
            if rqb:
                record['generated_contents']["Reasoning Question with Background"] = f"Question: {rqb} Answer: {chart_and_background_answers[1].split(':')[-1].strip() if len(chart_and_background_answers) > 1 else ''}"

    # 保存结果到输出文件
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(data, out_file, indent=4, ensure_ascii=False)




# 使用示例
api_key = 'sk-E7gOgfTjf0tREnYXEa1767178b7f43499eBdA49389CdD905'
model_name = 'gpt-4o-mini'
input_file = './sampled_output/sampled_output_file_multi.json'
output_file = './GPT4o-mini-result/output_multi_gpt-4o-mini.json'
image_dir = './benchmark_multi/multi'
process_json_file(input_file, output_file, api_key, model_name, image_dir)