# -*- coding: utf-8 -*-
"""
Script Completo de Auditoria e Correcao
- Corrige encoding restante
- Padroniza valores monetarios para R$ X.XXX,XX
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
BACKUP_DIR = WORK_DIR / "backup_encoding_fix"
BACKUP_DIR.mkdir(exist_ok=True)

# ============================================================================
# PARTE 1: Padroes de Encoding (Mojibake)
# ============================================================================

ENCODING_PATTERNS = [
    # C cedilha + A til maiusculos
    ("\u00c3\u2021", "\u00c7"),  # C cedilha
    ("\u00c3\u0192", "\u00c3"),  # A til
    # Outros acentos maiusculos
    ("\u00c3\u201d", "\u00d3"),  # O agudo
    ("\u00c3\u0089", "\u00c9"),  # E agudo
    ("\u00c3\u0160", "\u00da"),  # U agudo
    ("\u00c3\u0152", "\u00ca"),  # E circunflexo
    ("\u00c3\u201c", "\u00d4"),  # O circunflexo
    ("\u00c3\u201a", "\u00c2"),  # A circunflexo
    ("\u00c3\u20ac", "\u00c0"),  # A grave
    # Bullet e checkmarks
    ("\u00e2\u20ac\u00a2", "\u2022"),  # bullet
    ("\u00e2\u0080\u00a2", "\u2022"),  # bullet alt
]

# ============================================================================
# PARTE 2: Padronizacao Monetaria
# ============================================================================

def format_currency(match):
    """
    Formata valor monetario para o padrao R$ X.XXX,XX
    """
    full_match = match.group(0)
    
    # Extrair o numero do match
    # Remover R$ e espacos
    num_part = re.sub(r'R\s*\$\s*', '', full_match)
    num_part = re.sub(r'R\\\s*\$\s*', '', num_part)
    
    # Verificar se ja tem centavos
    if ',' in num_part:
        # Ja tem formato com virgula
        parts = num_part.split(',')
        integer_part = parts[0].replace('.', '').strip()
        decimal_part = parts[1].strip() if len(parts) > 1 else '00'
        
        # Garantir 2 digitos decimais
        if len(decimal_part) == 1:
            decimal_part += '0'
        elif len(decimal_part) > 2:
            decimal_part = decimal_part[:2]
    else:
        # Nao tem centavos - adicionar ,00
        integer_part = num_part.replace('.', '').strip()
        decimal_part = '00'
    
    # Formatar parte inteira com pontos de milhar
    try:
        integer_val = int(integer_part)
        formatted_int = f"{integer_val:,}".replace(',', '.')
    except ValueError:
        # Se nao conseguir converter, retornar original
        return full_match
    
    # Retornar no formato padrao
    return f"R\\$ {formatted_int},{decimal_part}"

# Regex para encontrar valores monetarios
# Captura: R$ 500, R$ 4.000, R$ 4.000,00, R\$ 500, etc
CURRENCY_PATTERNS = [
    # R$ seguido de numero sem centavos (ex: R$ 500, R$ 4.000)
    (r'R\\\$\s*(\d{1,3}(?:\.\d{3})*|\d+)(?!\s*,\d)', format_currency),
    # R$ com espaco sem centavos
    (r'R\$\s+(\d{1,3}(?:\.\d{3})*|\d+)(?!\s*,\d)', format_currency),
]

def fix_currency_format(content):
    """
    Corrige formatos monetarios para o padrao R$ X.XXX,XX
    """
    changes = 0
    
    # Primeiro, encontrar todos os valores que precisam de ,00
    # Padrao: R\$ XXXX ou R$ XXXX (sem ,XX no final)
    
    # Pattern para encontrar valores sem centavos
    pattern = r'(R\\\$\s*)(\d{1,3}(?:\.\d{3})*|\d+)(?![,\d])'
    
    def add_cents(m):
        nonlocal changes
        prefix = m.group(1)  # R\$ ou R$ 
        number = m.group(2)  # O numero
        
        # Verificar se ja tem centavos logo apos
        end_pos = m.end()
        if end_pos < len(content):
            next_chars = content[end_pos:end_pos+3]
            if next_chars.startswith(',') and next_chars[1:3].isdigit():
                return m.group(0)  # Ja tem centavos
        
        # Reformatar o numero
        num_clean = number.replace('.', '')
        try:
            num_val = int(num_clean)
            formatted = f"{num_val:,}".replace(',', '.')
            changes += 1
            return f"R\\$ {formatted},00"
        except ValueError:
            return m.group(0)
    
    content = re.sub(pattern, add_cents, content)
    
    return content, changes

def fix_encoding(content):
    """Corrige padroes de encoding restantes"""
    changes = 0
    for old, new in ENCODING_PATTERNS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            changes += count
    return content, changes

def process_file(filepath):
    """Processa um arquivo .tex"""
    
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # 1. Corrigir encoding
    content, enc_changes = fix_encoding(content)
    
    # 2. Padronizar valores monetarios
    content, curr_changes = fix_currency_format(content)
    
    total_changes = enc_changes + curr_changes
    
    if content != original:
        # Backup
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / (filepath.stem + "_" + ts + filepath.suffix)
        shutil.copy2(filepath, backup)
        
        # Salvar
        filepath.write_text(content, encoding='utf-8')
        
        return {
            'file': filepath.name,
            'encoding_fixes': enc_changes,
            'currency_fixes': curr_changes,
            'status': 'fixed'
        }
    
    return {
        'file': filepath.name,
        'encoding_fixes': 0,
        'currency_fixes': 0,
        'status': 'ok'
    }

def main():
    print("=" * 60)
    print("AUDITORIA COMPLETA - E-BOOK SISTEMA CJP")
    print("=" * 60)
    print()
    
    tex_files = sorted(WORK_DIR.glob("*.tex"))
    
    print(f"Arquivos encontrados: {len(tex_files)}")
    print()
    
    results = []
    for tex_file in tex_files:
        print(f"Processando: {tex_file.name}...", end=" ")
        result = process_file(tex_file)
        results.append(result)
        
        if result['status'] == 'fixed':
            print(f"CORRIGIDO (enc:{result['encoding_fixes']}, moeda:{result['currency_fixes']})")
        else:
            print("OK")
    
    # Resumo
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    fixed_count = sum(1 for r in results if r['status'] == 'fixed')
    enc_total = sum(r['encoding_fixes'] for r in results)
    curr_total = sum(r['currency_fixes'] for r in results)
    
    print(f"Arquivos corrigidos: {fixed_count}")
    print(f"Correcoes de encoding: {enc_total}")
    print(f"Valores monetarios padronizados: {curr_total}")
    
    if fixed_count > 0:
        print(f"\nBackups em: {BACKUP_DIR}")
    
    print("\nConcluido!")

if __name__ == "__main__":
    main()
