import json
import os

def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def update_archive(original_path, archive_path):
    # 读取原始文件和存档文件
    original_data = read_json(original_path)
    archived_data = read_json(archive_path)

    # 合并数据（这里假设每个比赛有唯一标识符，例如 'id' 或 '比赛名称'）
    new_data = {event['id']: event for event in archived_data}
    for event in original_data:
        new_data[event['id']] = event

    # 更新存档文件
    write_json(list(new_data.values()), archive_path)

def main():
    # 确保 Achieve 文件夹存在
    if not os.path.exists('Achieve'):
        os.makedirs('Achieve')

    # 更新 Global.json 和 CN.json 的存档
    update_archive('Global.json', 'Achieve/Global_archive.json')
    update_archive('CN.json', 'Achieve/CN_archive.json')

if __name__ == "__main__":
    main()
