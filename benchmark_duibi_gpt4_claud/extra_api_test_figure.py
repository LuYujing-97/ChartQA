import json
import random

def has_filled_priority_fields(generated_contents):
    """判断优先选择的三条记录是否都不为空。如果字段缺失，则视为内容为空。"""
    priority_fields = [
        "Visual Question 1", 
        "Visual Question 2", 
        "Data Retrieval Question"
    ]
    return all(generated_contents.get(field, '').strip() for field in priority_fields)

# 读取原始 JSON 文件
with open('output_all_multi.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 优先选择三条记录都不为空的内容
priority_data = [item for item in data if has_filled_priority_fields(item['generated_contents'])]

# 检查是否有足够的优先数据
if len(priority_data) < 40:
    print(f"警告：符合优先条件的记录少于60条，当前仅有 {len(priority_data)} 条，补充其余数据。")
    # 如果优先数据不足，从剩余数据中随机抽取补足
    remaining_data = [item for item in data if item not in priority_data]
    sampled_data = priority_data + random.sample(remaining_data, 40 - len(priority_data))
else:
    # 随机抽取 60 条优先记录
    sampled_data = random.sample(priority_data, 40)

# 记录抽取内容中的 ID
sampled_ids = [item['id'] for item in sampled_data]

# 将抽取的内容保存为新的 JSON 文件
with open('./sampled_output/sampled_output_file_multi.json', 'w', encoding='utf-8') as outfile:
    json.dump(sampled_data, outfile, indent=4)

# 将抽取的 ID 保存为新的 JSON 文件
with open('./sampled_output/sampled_ids_multi.json', 'w', encoding='utf-8') as idfile:
    json.dump(sampled_ids, idfile, indent=4)

print(f"成功保存 {len(sampled_data)} 条记录到 'sampled_output_file.json'，并保存 ID 到 'sampled_ids.json'。")