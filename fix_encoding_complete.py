#!/usr/bin/env python3
"""
Script de Correcao de Encoding - E-book Sistema CJP
Corrige mojibake via substituicao de texto
"""

import shutil
from datetime import datetime
from pathlib import Path

WORK_DIR = Path(__file__).parent
BACKUP_DIR = WORK_DIR / "backup_encoding_fix"

# Padroes de mojibake como TEXTO (nao bytes)
# Estes sao caracteres UTF-8 que representam UTF-8 lido como Latin-1
MOJIBAKE_MAP = {
    # Minusculas acentuadas
    "\u00c3\u00a1": "\u00e1",  # a agudo
    "\u00c3\u00a0": "\u00e0",  # a grave
    "\u00c3\u00a2": "\u00e2",  # a circunflexo
    "\u00c3\u00a3": "\u00e3",  # a til
    "\u00c3\u00a4": "\u00e4",  # a trema
    "\u00c3\u00a9": "\u00e9",  # e agudo
    "\u00c3\u00a8": "\u00e8",  # e grave
    "\u00c3\u00aa": "\u00ea",  # e circunflexo
    "\u00c3\u00ab": "\u00eb",  # e trema
    "\u00c3\u00ad": "\u00ed",  # i agudo
    "\u00c3\u00ac": "\u00ec",  # i grave
    "\u00c3\u00ae": "\u00ee",  # i circunflexo
    "\u00c3\u00af": "\u00ef",  # i trema
    "\u00c3\u00b3": "\u00f3",  # o agudo
    "\u00c3\u00b2": "\u00f2",  # o grave
    "\u00c3\u00b4": "\u00f4",  # o circunflexo
    "\u00c3\u00b5": "\u00f5",  # o til
    "\u00c3\u00b6": "\u00f6",  # o trema
    "\u00c3\u00ba": "\u00fa",  # u agudo
    "\u00c3\u00b9": "\u00f9",  # u grave
    "\u00c3\u00bb": "\u00fb",  # u circunflexo
    "\u00c3\u00bc": "\u00fc",  # u trema
    "\u00c3\u00a7": "\u00e7",  # c cedilha
    "\u00c3\u00b1": "\u00f1",  # n til
    
    # Maiusculas acentuadas
    "\u00c3\u0081": "\u00c1",  # A agudo
    "\u00c3\u0080": "\u00c0",  # A grave
    "\u00c3\u0082": "\u00c2",  # A circunflexo
    "\u00c3\u0083": "\u00c3",  # A til - CUIDADO: pode conflitar
    "\u00c3\u0084": "\u00c4",  # A trema
    "\u00c3\u0089": "\u00c9",  # E agudo
    "\u00c3\u0088": "\u00c8",  # E grave
    "\u00c3\u008a": "\u00ca",  # E circunflexo
    "\u00c3\u008b": "\u00cb",  # E trema
    "\u00c3\u008d": "\u00cd",  # I agudo
    "\u00c3\u008c": "\u00cc",  # I grave
    "\u00c3\u008e": "\u00ce",  # I circunflexo
    "\u00c3\u008f": "\u00cf",  # I trema
    "\u00c3\u0093": "\u00d3",  # O agudo
    "\u00c3\u0092": "\u00d2",  # O grave
    "\u00c3\u0094": "\u00d4",  # O circunflexo
    "\u00c3\u0095": "\u00d5",  # O til
    "\u00c3\u0096": "\u00d6",  # O trema
    "\u00c3\u009a": "\u00da",  # U agudo
    "\u00c3\u0099": "\u00d9",  # U grave
    "\u00c3\u009b": "\u00db",  # U circunflexo
    "\u00c3\u009c": "\u00dc",  # U trema
    "\u00c3\u0087": "\u00c7",  # C cedilha
    "\u00c3\u0091": "\u00d1",  # N til
    
    # Caracteres especiais (3 bytes em UTF-8)
    "\u00e2\u0080\u00a2": "\u2022",  # bullet
    "\u00e2\u0080\u0094": "\u2014",  # em-dash
    "\u00e2\u0080\u0093": "\u2013",  # en-dash
    "\u00e2\u0080\u009c": "\u201c",  # aspas esquerda
    "\u00e2\u0080\u009d": "\u201d",  # aspas direita
    "\u00e2\u0080\u0098": "\u2018",  # apostrofo esquerdo
    "\u00e2\u0080\u0099": "\u2019",  # apostrofo direito
    "\u00e2\u0080\u00a6": "\u2026",  # reticencias
    "\u00e2\u009c\u0085": "\u2705",  # checkmark verde
    "\u00e2\u009c\u0093": "\u2713",  # checkmark
    "\u00e2\u009c\u0097": "\u2717",  # X mark
    "\u00c2\u00a7": "\u00a7",        # paragrafo
    "\u00c2\u00ba": "\u00ba",        # ordinal masculino
    "\u00c2\u00aa": "\u00aa",        # ordinal feminino
    "\u00c2\u00b0": "\u00b0",        # grau
    "\u00c2\u00a9": "\u00a9",        # copyright
    "\u00c2\u00ae": "\u00ae",        # registered
    "\u00c2\u00b2": "\u00b2",        # superscript 2
    "\u00c2\u00b3": "\u00b3",        # superscript 3
    "\u00c2\u00bd": "\u00bd",        # 1/2
    "\u00c2\u00bc": "\u00bc",        # 1/4
    "\u00c2\u00be": "\u00be",        # 3/4
    "\u00c3\u0097": "\u00d7",        # multiplicacao
    "\u00c3\u00b7": "\u00f7",        # divisao
}

def create_backup(file_path):
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    return backup_path

def fix_mojibake(content):
    """Substitui padroes de mojibake pelos caracteres corretos."""
    fixed = content
    total_fixes = 0
    
    # Ordenar do mais longo para o mais curto
    sorted_patterns = sorted(MOJIBAKE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for corrupted, correct in sorted_patterns:
        count = fixed.count(corrupted)
        if count > 0:
            fixed = fixed.replace(corrupted, correct)
            total_fixes += count
    
    return fixed, total_fixes

def has_mojibake(content):
    """Verifica se o conteudo tem padroes de mojibake."""
    for pattern in MOJIBAKE_MAP.keys():
        if pattern in content:
            return True
    return False

def process_file(file_path):
    result = {
        "file": file_path.name,
        "status": "skipped",
        "fixes": 0,
        "backup": None,
        "error": None
    }
    
    try:
        # Ler arquivo
        content = file_path.read_text(encoding='utf-8')
        
        # Verificar se tem mojibake
        if not has_mojibake(content):
            result["status"] = "clean"
            return result
        
        # Criar backup
        backup_path = create_backup(file_path)
        result["backup"] = str(backup_path)
        
        # Corrigir
        fixed_content, fixes = fix_mojibake(content)
        result["fixes"] = fixes
        
        if fixes > 0:
            file_path.write_text(fixed_content, encoding='utf-8')
            result["status"] = "fixed"
        else:
            result["status"] = "unchanged"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    print("=" * 60)
    print("CORRECAO DE MOJIBAKE - E-BOOK SISTEMA CJP")
    print("=" * 60)
    print()
    
    tex_files = list(WORK_DIR.glob("*.tex"))
    
    if not tex_files:
        print("ERRO: Nenhum arquivo .tex encontrado!")
        return
    
    print(f"Diretorio: {WORK_DIR}")
    print(f"Arquivos encontrados: {len(tex_files)}")
    print()
    
    results = []
    for file_path in sorted(tex_files):
        print(f"Processando: {file_path.name}...", end=" ")
        result = process_file(file_path)
        results.append(result)
        
        if result["status"] == "fixed":
            print(f"CORRIGIDO! ({result['fixes']} substituicoes)")
        elif result["status"] == "clean":
            print("LIMPO")
        elif result["status"] == "error":
            print(f"ERRO: {result['error']}")
        else:
            print("NAO ALTERADO")
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    fixed = sum(1 for r in results if r["status"] == "fixed")
    clean = sum(1 for r in results if r["status"] == "clean")
    errors = sum(1 for r in results if r["status"] == "error")
    total_fixes = sum(r["fixes"] for r in results)
    
    print(f"Arquivos corrigidos: {fixed}")
    print(f"Arquivos limpos: {clean}")
    print(f"Erros: {errors}")
    print(f"Total de substituicoes: {total_fixes}")
    
    if fixed > 0:
        print(f"\nBackups salvos em: {BACKUP_DIR}")
    
    print()
    print("Script concluido!")

if __name__ == "__main__":
    main()
