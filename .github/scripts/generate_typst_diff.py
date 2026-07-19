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
#let diff-del-block(body) = block(fill: rgb("ffe6e6"), stroke: red, inset: 10pt, width: 100%, radius: 4pt, spacing: 1em)[#body]
#let diff-add-block(body) = block(fill: rgb("e6ffe6"), stroke: green, inset: 10pt, width: 100%, radius: 4pt, spacing: 1em)[#body]
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
            for block in old_blocks[i1:i2]:
                out_lines.append("#diff-del-block[")
                out_lines.append(block)
                out_lines.append("]")
                
                article_count = block.count("#article[")
                if article_count > 0:
                    out_lines.append(f"#article-counter.update(c => c - {article_count})")
                    
                out_lines.append("")
        elif opcode == 'replace':
            for block in old_blocks[i1:i2]:
                out_lines.append("#diff-del-block[")
                out_lines.append(block)
                out_lines.append("]")
                
                article_count = block.count("#article[")
                if article_count > 0:
                    out_lines.append(f"#article-counter.update(c => c - {article_count})")
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
