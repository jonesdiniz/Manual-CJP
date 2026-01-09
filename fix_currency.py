# -*- coding: utf-8 -*-
"""
Script direto para padronizar valores monetarios
Adiciona ,00 em valores sem centavos
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
BACKUP_DIR = WORK_DIR / "backup_encoding_fix"
BACKUP_DIR.mkdir(exist_ok=True)

def fix_currency(content):
    """
    Adiciona ,00 em valores monetarios que nao tem centavos
    Padroes: R\\$ 500 -> R\\$ 500,00
             R\\$ 4.000 -> R\\$ 4.000,00
    """
    changes = 0
    
    # Pattern para R\$ seguido de numero sem ,XX depois
    # Match: R\$ 500 ou R\$ 4.000 mas NAO R\$ 500,00
    
    def replacer(m):
        nonlocal changes
        # m.group(0) = todo o match
        # m.group(1) = R\$ 
        # m.group(2) = numero
        
        prefix = m.group(1)
        number = m.group(2)
        
        # Verificar se o proximo char nao e virgula + digitos
        # (ja capturado pelo negative lookahead)
        
        changes += 1
        return f"{prefix}{number},00"
    
    # Pattern: R\$ seguido de numero, mas NAO seguido de ,00 ou ,XX
    pattern = r'(R\\\$\s*)(\d{1,3}(?:\.\d{3})*|\d+)(?!,\d)'
    
    new_content = re.sub(pattern, replacer, content)
    
    return new_content, changes

def process_file(filepath):
    """Processa um arquivo"""
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    new_content, changes = fix_currency(content)
    
    if new_content != original:
        # Backup
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / (filepath.stem + "_" + ts + filepath.suffix)
        shutil.copy2(filepath, backup)
        
        # Salvar
        filepath.write_text(new_content, encoding='utf-8')
        return changes
    
    return 0

# Main
print("Padronizando valores monetarios...")
print()

total_changes = 0
for tex_file in sorted(WORK_DIR.glob("*.tex")):
    changes = process_file(tex_file)
    if changes > 0:
        print(f"  {tex_file.name}: {changes} valores corrigidos")
        total_changes += changes

print()
print(f"Total de valores padronizados: {total_changes}")
