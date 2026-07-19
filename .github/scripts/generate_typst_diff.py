import sys
import difflib

def split_into_blocks(text):
    lines = text.split('\n')
    blocks = []
    current_block = []
    nest_level = 0
    
    for line in lines:
        current_block.append(line)
        # Typstのブロック・関数呼び出しのネストを計算
        nest_level += line.count('[') - line.count(']')
        nest_level += line.count('(') - line.count(')')
        nest_level += line.count('{') - line.count('}')
        
        # 空行かつカッコが全て閉じている場合、ブロックとして区切る
        if line.strip() == '' and nest_level == 0:
            blocks.append('\n'.join(current_block).strip())
            current_block = []
            
    if current_block:
        blocks.append('\n'.join(current_block).strip())
        
    return [b for b in blocks if b]

def generate_diff(old_file, new_file, out_file):
    with open(old_file, 'r', encoding='utf-8') as f:
        old_text = f.read()
    with open(new_file, 'r', encoding='utf-8') as f:
        new_text = f.read()
        
    old_blocks = split_into_blocks(old_text)
    new_blocks = split_into_blocks(new_text)
    
    sm = difflib.SequenceMatcher(None, old_blocks, new_blocks)
    
    out_lines = []
    
    diff_macros = """
// --- Diff Macros ---
#let diff-del-block(body) = block(
  fill: rgb("ffebe9"),
  stroke: (left: 4pt + rgb("cf222e")),
  inset: (top: 8pt, bottom: 8pt, left: 10pt, right: 10pt),
  above: 1.2em,
  below: 1.2em,
  width: 100%
)[
  #text(fill: rgb("cf222e"))[#strike[#body]]
]

#let diff-add-block(body) = block(
  fill: rgb("e6ffec"),
  stroke: (left: 4pt + rgb("1a7f37")),
  inset: (top: 8pt, bottom: 8pt, left: 10pt, right: 10pt),
  above: 1.2em,
  below: 1.2em,
  width: 100%
)[
  #text(fill: rgb("1a7f37"))[#body]
]

#set page(
  header: align(right + top)[
    #rect(fill: rgb("f8f9fa"), stroke: 0.5pt + luma(200), inset: 5pt, radius: 2pt)[
      #text(size: 8pt)[
        #text(fill: rgb("cf222e"))[■ 削除部分] \\
        #text(fill: rgb("1a7f37"))[■ 追加部分]
      ]
    ]
  ]
)
// -------------------
"""
    out_lines.append(diff_macros)
    
    for opcode, i1, i2, j1, j2 in sm.get_opcodes():
        if opcode == 'equal':
            for block in new_blocks[j1:j2]:
                out_lines.append(block)
                out_lines.append("")
        elif opcode == 'insert':
            for block in new_blocks[j1:j2]:
                out_lines.append("#diff-add-block[")
                out_lines.append(block)
                out_lines.append("]")
                out_lines.append("")
        elif opcode == 'delete':
            total_deleted_articles = 0
            for block in old_blocks[i1:i2]:
                out_lines.append("#diff-del-block[")
                out_lines.append(block)
                out_lines.append("]")
                total_deleted_articles += block.count("#article[")
                
            if total_deleted_articles > 0:
                out_lines.append(f"#article-counter.update(c => c - {total_deleted_articles})")
            out_lines.append("")
            
        elif opcode == 'replace':
            total_deleted_articles = 0
            for block in old_blocks[i1:i2]:
                out_lines.append("#diff-del-block[")
                out_lines.append(block)
                out_lines.append("]")
                total_deleted_articles += block.count("#article[")
                
            if total_deleted_articles > 0:
                out_lines.append(f"#article-counter.update(c => c - {total_deleted_articles})")
            out_lines.append("")
                
            for block in new_blocks[j1:j2]:
                out_lines.append("#diff-add-block[")
                out_lines.append(block)
                out_lines.append("]")
                out_lines.append("")

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

if __name__ == '__main__':
    generate_diff(sys.argv[1], sys.argv[2], sys.argv[3])
