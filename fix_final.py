# -*- coding: utf-8 -*-
"""Correcao final - substituicao de texto direta"""

import shutil
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
BACKUP_DIR = WORK_DIR / "backup_encoding_fix"
BACKUP_DIR.mkdir(exist_ok=True)

# Padroes de texto a substituir (nao bytes)
# Usando caracteres Unicode literais
TEXT_REPLACEMENTS = [
    # C cedilha + A til maiusculos incorretos -> corretos
    ("\u00c3\u2021\u00c3\u0192", "\u00c7\u00c3"),  # Ã‡Ãƒ -> ÇÃ tentativa 1
    ("\u00c3\u2021", "\u00c7"),  # Ã‡ -> Ç (C cedilha)
    ("\u00c3\u0192", "\u00c3"),  # Ãƒ -> Ã (A til)
    # Outros acentos maiusculos
    ("\u00c3\u201d", "\u00d3"),  # Ã" -> Ó (O agudo)
    ("\u00c3\u0089", "\u00c9"),  # Ã‰ -> É (E agudo)
    ("\u00c3\u0160", "\u00da"),  # Ãš -> Ú (U agudo)
    ("\u00c3\u0178", "\u00dc"),  # Ãœ -> Ü (U trema) 
    ("\u00c3\u0152", "\u00ca"),  # ÃŠ -> Ê (E circunflexo)
    ("\u00c3\u201c", "\u00d4"),  # Ã" -> Ô (O circunflexo)
    ("\u00c3\u201a", "\u00c2"),  # Ã‚ -> Â (A circunflexo)
    ("\u00c3\u20ac", "\u00c0"),  # Ã€ -> À (A grave)
    # Bullet points e checkmarks restantes
    ("\u00e2\u20ac\u00a2", "\u2022"),  # bullet tentativa
    ("\u00e2\u0080\u00a2", "\u2022"),  # bullet tentativa 2
    ("\u00e2\u0080\u00a2", "\u2022"),  # bullet UTF-8 standard
]

def fix_file_text(filepath):
    """Corrige padroes de mojibake usando substituicao de texto"""
    
    content = filepath.read_text(encoding='utf-8')
    original = content
    changes = 0
    
    for old, new in TEXT_REPLACEMENTS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            changes += count
            print(f"  '{old}' -> '{new}' ({count}x)")
    
    if content != original:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / (filepath.stem + "_" + ts + filepath.suffix)
        shutil.copy2(filepath, backup)
        
        filepath.write_text(content, encoding='utf-8')
        return True, changes
    
    return False, 0

# Processar arquivos
print("Processando arquivos...")
total_fixed = 0
total_changes = 0

for tex_file in sorted(WORK_DIR.glob("*.tex")):
    print(f"\n{tex_file.name}:")
    fixed, changes = fix_file_text(tex_file)
    if fixed:
        total_fixed += 1
        total_changes += changes
        print(f"  CORRIGIDO! ({changes} alteracoes)")
    else:
        print("  OK")

print()
print(f"Total de arquivos corrigidos: {total_fixed}")
print(f"Total de alteracoes: {total_changes}")
