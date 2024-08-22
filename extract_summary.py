import json

# 读取 A.jsonl 文件中的数据并提取 summation 字段
summations = {}
with open('./multi/multi_lu_updated_multi_summary.jsonl', 'r', encoding='utf-8') as file_a:
    for line in file_a:
        try:
            json_object = json.loads(line.strip())
            obj_id = json_object.get("id", "")
            summation = json_object.get("generated_contents", {}).get("Chart_Summarization", "")
            if obj_id:
                summations[obj_id] = summation
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError in A.jsonl: {e}")

# 读取 output.jsonl 文件中的数据并更新 generated_contents
updated_objects = []
with open('output_multi.jsonl', 'r', encoding='utf-8') as file_output:
    for line in file_output:
        try:
            json_object = json.loads(line.strip())
            obj_id = json_object.get("id", "")
            if obj_id in summations:
                if 'generated_contents' not in json_object:
                    json_object['generated_contents'] = {}
                json_object['generated_contents']['Chart_Summarization'] = summations[obj_id]
            updated_objects.append(json_object)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError in output.jsonl: {e}")

# 将更新后的 JSON 对象写回到 output.jsonl 文件中
with open('output_multi_all.jsonl', 'w', encoding='utf-8') as file_output:
    for obj in updated_objects:
        file_output.write(json.dumps(obj, ensure_ascii=False) + '\n')

print("JSON Lines 文件已成功更新并保存为 output.jsonl。")
