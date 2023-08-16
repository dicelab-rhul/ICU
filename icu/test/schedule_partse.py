import re

text = "group1, this is group2, another group3, with, commas"
_matchgroup = "\s*([^,]+(?:,[^,]+)*)\s*"
pattern = f"{_matchgroup},{_matchgroup},{_matchgroup}"

matches = re.match(pattern, text)
if matches:
    group1 = matches.group(1)
    group2 = matches.group(2)
    group3 = matches.group(3)
    print("Group 1:", group1)
    print("Group 2:", group2)
    print("Group 3:", group3)
else:
    print("No match found.")