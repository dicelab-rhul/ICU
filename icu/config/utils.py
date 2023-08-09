
import ast

def read_configpy_file(file_path):
    config_dict = {}
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        key = target.id.lower()
                        value = ast.literal_eval(node.value)
                        config_dict[key] = value
    return config_dict
