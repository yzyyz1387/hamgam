
import json
import re
from datetime import datetime
from pathlib import Path

def json_to_md(json_path, output_path):
    def process_value(value, indent=0):
        if isinstance(value, dict):
            return '\n'.join(f"{indent*' '}- {k}: {process_value(v, indent+2)}" for k, v in value.items())
        elif isinstance(value, list):
            return '\n'.join(f"{indent*' '}- {process_value(v, indent+2)}" for v in value)
        else:
            return value

    with open(json_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    md_data = ""
    for key, value in data.items():
        md_data += f"### {key}\n{process_value(value)}\n"
    with open(output_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_data)

def md_to_json(md_path, output_path):
    def process_line(line):
        match = re.match(r'(\s*)- (.*?): (.*)', line)
        if match:
            indent, key, value = match.groups()
            return len(indent) // 2, key, value.strip()
        else:
            return None

    with open(md_path, 'r', encoding='utf-8') as md_file:
        lines = md_file.readlines()
    json_data = {}
    md_keys = set()
    current_key = None
    for line in lines:
        line = line.strip()
        if line.startswith('###'):
            current_key = line[4:]
            md_keys.add(current_key)
            json_data[current_key] = {}
        elif line.startswith('-'):
            result = process_line(line)
            if result is not None:
                indent, key, value = result
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                json_data[current_key][key] = value

    output_path = Path(output_path)
    if output_path.exists():
        with output_path.open('r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        for key in json_data.keys():
            if key in existing_data and 'update' not in existing_data[key]:
                existing_data[key]['update'] = datetime.now().strftime('%Y-%m-%d')
            elif key not in existing_data:
                existing_data[key] = json_data[key]
                existing_data[key]['update'] = datetime.now().strftime('%Y-%m-%d')
        json_data = existing_data

    with output_path.open('w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    return md_keys

def remove_unused_keys(json_path, md_keys):
    with open(json_path, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    keys_to_remove = [key for key in json_data if key not in md_keys]
    for key in keys_to_remove:
        del json_data[key]

    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    md_keys = md_to_json('pic_res.md', 'pic_res.json')
    remove_unused_keys('pic_res.json', md_keys)