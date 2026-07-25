import os
import re
import struct

def parse_po(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = {}
    # Find all msgid/msgstr pairs
    pattern = r'msgid\s+"((?:[^"\\]|\\.)*)"\s+msgstr\s+"((?:[^"\\]|\\.)*)"'
    
    # Also support multi-line strings if any, or block matching
    blocks = re.split(r'\n(?=msgid)', content)
    for block in blocks:
        id_match = re.search(r'msgid\s+(".*?"(?:\s*\n\s*".*?")*)', block, re.DOTALL)
        str_match = re.search(r'msgstr\s+(".*?"(?:\s*\n\s*".*?")*)', block, re.DOTALL)
        if id_match and str_match:
            msgid = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', id_match.group(1)))
            msgstr = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', str_match.group(1)))
            # unescape common escapes
            msgid = msgid.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            msgstr = msgstr.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            if msgid or msgstr: # include header if present
                entries[msgid] = msgstr
    return entries

def generate_mo(entries):
    # Sort entries by msgid as required by GNU gettext spec
    sorted_keys = sorted(entries.keys())
    
    # Original strings block and Translation strings block
    o_offsets = []
    t_offsets = []
    
    ids_bytes = bytearray()
    strs_bytes = bytearray()
    
    for key in sorted_keys:
        o_bytes = key.encode('utf-8') + b'\x00'
        t_bytes = entries[key].encode('utf-8') + b'\x00'
        
        o_offsets.append((len(o_bytes) - 1, len(ids_bytes)))
        t_offsets.append((len(t_bytes) - 1, len(strs_bytes)))
        
        ids_bytes.extend(o_bytes)
        strs_bytes.extend(t_bytes)
        
    num_strings = len(sorted_keys)
    keystart = 7 * 4
    valstart = keystart + num_strings * 8
    keyoffsets = valstart + num_strings * 8
    valoffsets = keyoffsets + len(ids_bytes)
    
    header = struct.pack(
        'IIIIIII',
        0x950412de,  # Magic number
        0,           # Version
        num_strings, # Number of strings
        keystart,    # Offset of original strings table
        valstart,    # Offset of translation strings table
        0,           # Size of hashing table
        0            # Offset of hashing table
    )
    
    o_table = bytearray()
    for length, offset in o_offsets:
        o_table.extend(struct.pack('II', length, keyoffsets + offset))
        
    t_table = bytearray()
    for length, offset in t_offsets:
        t_table.extend(struct.pack('II', length, valoffsets + offset))
        
    return header + o_table + t_table + ids_bytes + strs_bytes

def main():
    base_dir = os.path.dirname(__file__)
    locale_dir = os.path.join(base_dir, 'locale')
    
    compiled = 0
    for lang in ['sw', 'fr']:
        po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
        mo_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.mo')
        
        if os.path.exists(po_path):
            entries = parse_po(po_path)
            mo_data = generate_mo(entries)
            with open(mo_path, 'wb') as f:
                f.write(mo_data)
            print(f"Successfully compiled {lang}: {len(entries)} entries -> {mo_path}")
            compiled += 1

    print(f"Total compiled: {compiled}")

if __name__ == '__main__':
    main()
