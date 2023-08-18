original_list = ["a \\", "b \\", "c", "d", "e\\", "f"]

result = []
current_group = []

for item in original_list:
    if item.endswith("\\"):
        current_group.append(item[:-1])  # Remove trailing "\\"
    else:
        current_group.append(item)
        result.append(current_group)
        current_group = []

if current_group:
    result.append(current_group)

print(result)
