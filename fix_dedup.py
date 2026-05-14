#!/usr/bin/env python3
"""Fix soulbeat deduplication: only 100% exact match counts as duplicate"""

import sys

filepath = 'soul/soulbeat.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of the deduplication block
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if '# 检查是否与历史重复（精确匹配+多维度语义相似度）' in line:
        start_idx = i
    if start_idx is not None and 'return None' in line and i > start_idx + 5:
        # Find the last return None in the similarity block
        end_idx = i
        # Look ahead to make sure we captured the whole block
        if i + 1 < len(lines) and lines[i + 1].strip() == '':
            break

if start_idx is None or end_idx is None:
    print(f"ERROR: Could not find dedup block. start={start_idx}, end={end_idx}")
    sys.exit(1)

# Show what we're replacing
print(f"Found block at lines {start_idx+1}-{end_idx+1}")
print("OLD:")
for l in lines[start_idx:end_idx+1]:
    print(f"  {l.rstrip()}")

# Replace with simple exact-match only
new_block = [
    '        # 检查是否与历史重复（仅精确匹配：100%相同才算重复）\n',
    '        for old_topic in self._topic_history[-10:]:\n',
    '            if topic.strip() == old_topic.strip():\n',
    '                logger.info("♥ 话题与历史精确重复（100%相同），跳过本次跳动")\n',
    '                return None\n',
]

print("\nNEW:")
for l in new_block:
    print(f"  {l.rstrip()}")

# Do the replacement
lines[start_idx:end_idx+1] = new_block

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nOK: Fixed! Removed {end_idx - start_idx + 1 - len(new_block)} lines of fuzzy matching code")
