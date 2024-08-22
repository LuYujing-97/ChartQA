import json

# 读取JSON Lines文件
with open('./multi/multi_lu_updated_claude_multi_all.jsonl', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 存储所有 JSON 对象
json_objects = []

# 逐行解析 JSON 对象
for line in lines:
    try:
        json_object = json.loads(line.strip())
        json_objects.append(json_object)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")

# 遍历每个 JSON 对象并进行处理
for json_data in json_objects:
    # 提取和格式化问题
    generated_questions = json_data["generated_contents"]["generated_questions"]
    questions_list = generated_questions.split("\n\n")

    formatted_questions = {}

    for question in questions_list:
        if "Visual Question 1:" in question:
            key = "Visual Question 1"
        elif "Visual Question 2:" in question:
            key = "Visual Question 2"
        elif "Data Retrieval Question:" in question:
            key = "Data Retrieval Question"
        elif "Reasoning Question 1:" in question:
            key = "Reasoning Question 1"
        elif "Reasoning Question 2:" in question:
            key = "Reasoning Question 2"
        elif "Reasoning Question 3:" in question:
            key = "Reasoning Question 3"
        elif "Reasoning Question 4:" in question:
            key = "Reasoning Question 4"
        elif "Chart Description:" in question:
            key = "Chart Description"
        else:
            continue

        # 提取问题和答案
        question_text = question.split("Question: ")[1].split("Answer: ")[0].strip()
        answer_text = question.split("Answer: ")[1].strip()
        formatted_questions[key] = f"Question: {question_text} Answer: {answer_text}"

    # 更新JSON数据
    json_data["generated_contents"] = formatted_questions

# 将处理后的JSON对象写回到一个新的文件
with open('output_multi.jsonl', 'w', encoding='utf-8') as file:
    for obj in json_objects:
        file.write(json.dumps(obj, ensure_ascii=False) + '\n')

print("JSON Lines 文件已成功更新并保存为 output.jsonl。")
