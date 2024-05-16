
import json
import re
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
    current_key = None
    for line in lines:
        line = line.strip()
        if line.startswith('###'):
            current_key = line[4:]
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
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    md_to_json('README.md', 'res.json')