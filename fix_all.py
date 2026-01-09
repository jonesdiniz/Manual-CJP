# -*- coding: utf-8 -*-
"""
Script Unificado de Correcao - E-book Sistema CJP
1. Corrige encoding restante (mojibake)
2. Escapa R$ para R\$ (LaTeX correto)
3. Adiciona ,00 em valores monetarios sem centavos
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(__file__).parent
BACKUP_DIR = WORK_DIR / "backup_final"
BACKUP_DIR.mkdir(exist_ok=True)

# Padroes de encoding (mojibake)
ENCODING_PATTERNS = [
    ("\u00c3\u2021", "\u00c7"),  # C cedilha
    ("\u00c3\u0192", "\u00c3"),  # A til
    ("\u00c3\u201d", "\u00d3"),  # O agudo
    ("\u00c3\u0089", "\u00c9"),  # E agudo
    ("\u00c3\u0160", "\u00da"),  # U agudo
    ("\u00c3\u0152", "\u00ca"),  # E circunflexo
    ("\u00c3\u201c", "\u00d4"),  # O circunflexo
    ("\u00c3\u201a", "\u00c2"),  # A circunflexo
    ("\u00c3\u20ac", "\u00c0"),  # A grave
]

def fix_encoding(content):
    """Corrige padroes de encoding restantes"""
    for old, new in ENCODING_PATTERNS:
        content = content.replace(old, new)
    return content

def fix_currency_escape(content):
    """
    Corrige R$ para R\\$ (escape LaTeX correto)
    Evita double-escape (R\\$ ja escapado)
    """
    # Substituir R$ por R\$ APENAS quando NAO esta com barra antes
    # Usar regex para evitar double-escape
    
    # Pattern: R$ NAO precedido por \
    # Complexo em Python, usar abordagem diferente
    
    # Primeiro, normalizar: remover escapes antigos incorretos
    # Depois, aplicar escape correto
    
    # Abordagem simples e segura:
    # 1. Substituir R\\$ por placeholder
    # 2. Substituir R$ por R\\$
    # 3. Restaurar placeholders
    
    placeholder = "___REAIS_ESCAPED___"
    content = content.replace("R\\$", placeholder)
    content = content.replace("R$", "R\\$")
    content = content.replace(placeholder, "R\\$")
    
    return content

def fix_currency_format(content):
    """
    Adiciona ,00 em valores monetarios sem centavos
    Exemplo: R\\$ 500 -> R\\$ 500,00
    NAO altera: R\\$ 500/mes, R\\$ 500-1.000, R\\$ 500,50
    """
    
    def add_cents(m):
        prefix = m.group(1)  # R\\$ e numero
        number = m.group(2)  # digitos
        suffix = m.group(3)  # caractere apos (para verificacao)
        
        # Se o proximo caractere for , . / - nao adicionar centavos
        if suffix and suffix in ',-/.':
            return m.group(0)  # Retornar original
        
        return f"{prefix}{number},00{suffix if suffix else ''}"
    
    # Pattern: R\$ numero NAO seguido de ,XX ou -
    # Captura: (R\$ )(numero)(proximo char ou fim)
    pattern = r'(R\\\$\s*)(\d{1,3}(?:\.\d{3})*|\d+)([,\-/\.]|\s|$)?'
    
    def smart_replace(m):
        prefix = m.group(1)
        number = m.group(2)
        suffix = m.group(3) if m.group(3) else ""
        
        # Se sufixo for virgula (ja tem centavos) ou hifen (range), nao mexer
        if suffix.startswith(',') or suffix in '-/':
            return m.group(0)
        
        # Se sufixo for ponto, pode ser milhar ou fim de frase
        if suffix == '.':
            # Verificar se e milhar (numero depois) ou fim de frase
            # Neste caso, assumir fim de frase e adicionar ,00
            return f"{prefix}{number},00{suffix}"
        
        # Sem sufixo especial, adicionar ,00
        return f"{prefix}{number},00{suffix}"
    
    content = re.sub(pattern, smart_replace, content)
    
    return content

def process_file(filepath):
    """Processa um arquivo .tex"""
    
    content = filepath.read_text(encoding='utf-8')
    original = content
    
    # 1. Corrigir encoding
    content = fix_encoding(content)
    
    # 2. Escapar R$
    content = fix_currency_escape(content)
    
    # 3. Padronizar valores monetarios
    content = fix_currency_format(content)
    
    if content != original:
        # Backup
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / (filepath.stem + "_" + ts + filepath.suffix)
        shutil.copy2(filepath, backup)
        
        # Salvar
        filepath.write_text(content, encoding='utf-8')
        
        return True
    
    return False

def main():
    print("=" * 60)
    print("CORRECAO UNIFICADA - E-BOOK SISTEMA CJP")
    print("=" * 60)
    print()
    
    tex_files = sorted(WORK_DIR.glob("*.tex"))
    print(f"Arquivos: {len(tex_files)}")
    print()
    
    fixed = 0
    for tex_file in tex_files:
        print(f"Processando: {tex_file.name}...", end=" ")
        if process_file(tex_file):
            fixed += 1
            print("CORRIGIDO")
        else:
            print("OK")
    
    print()
    print(f"Total corrigidos: {fixed}")
    print(f"Backups em: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
