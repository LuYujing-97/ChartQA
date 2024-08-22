import json

# input_file = './benchmark_single/single_test_lu_updated_single_reasoning.jsonl'
# output_file = './benchmark_single/output_single_test.jsonl'
input_file = './benchmark_multi/multi_lu_updated_multi_reasoning.jsonl'
output_file = './benchmark_multi/output_multi_reasoning_background.jsonl'

def process_reasoning_questions(generated_questions):
    # 提取和格式化 reasoning_questions
    start_index = generated_questions.find("Question:")
    if start_index != -1:
        formatted_questions = generated_questions[start_index:].strip()
        return formatted_questions
    return ""

def fix_json_format(json_str):
    # 尝试修复常见的 JSON 格式问题
    json_str = json_str.strip()
    if json_str.startswith('{') and json_str.endswith('}'):
        return json_str
    # 添加缺失的花括号
    if not json_str.startswith('{'):
        json_str = '{' + json_str
    if not json_str.endswith('}'):
        json_str = json_str + '}'
    return json_str

# 读取文件中的所有行
with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

json_objects = []

# 逐行处理 JSON 对象
for line_number, line in enumerate(lines, start=1):
    line = line.strip()  # 去除行首尾的空白字符
    if not line:  # 跳过空行
        continue

    fixed_line = fix_json_format(line)
    try:
        json_object = json.loads(fixed_line)  # 尝试解析 JSON 对象
        
        # 使用 dict.get() 访问键
        generated_contents = json_object.get("generated_contents", {})
        reasoning_questions = generated_contents.get("reasoning_questions", "")
        formatted_questions = process_reasoning_questions(reasoning_questions)
        
        # 更新 JSON 对象
        if "generated_contents" not in json_object:
            json_object["generated_contents"] = {}
        json_object["generated_contents"]["reasoning_questions"] = formatted_questions
        
        json_objects.append(json_object)
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        print(f"Line causing error on line {line_number}: {fixed_line}")

# 将处理后的 JSON 对象写入到新的文件
with open(output_file, 'w', encoding='utf-8') as file:
    for obj in json_objects:
        file.write(json.dumps(obj, ensure_ascii=False) + '\n')

print("JSON Lines 文件已成功更新并保存为 output_single_test.jsonl。")
