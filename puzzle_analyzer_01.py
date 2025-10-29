# -*- coding: utf-8 -*-
"""
Analisador de imagem tipo puzzle.
Testa múltiplas combinações de saturação, brilho e número de colunas.
Identifica cores fora do espectro do arco-íris, gera WIFs demonstrativos
e cria um pseudo-inverso baseado em Mersenne.
"""

from PIL import Image
import numpy as np
import colorsys
import hashlib
import base58

# === CONFIGURAÇÕES ===
IMG_PATH = "puzzle.jpeg"  # Caminho da imagem
ROWS = 21  # Número fixo de linhas

# Faixas de matiz (Hue) do arco-íris — cobrindo todo o espectro visível
RAINBOW_HUE_RANGES = (
    ("vermelho", 0.00, 0.05),
    ("laranja", 0.05, 0.10),
    ("amarelo", 0.10, 0.17),
    ("verde", 0.17, 0.45),
    ("ciano", 0.45, 0.52),
    ("azul", 0.52, 0.68),
    ("violeta", 0.68, 0.78),
    ("magenta", 0.78, 0.92),
    ("vermelho2", 0.92, 1.00)
)

# === FUNÇÕES ===
def is_rainbow_color(rgb, SAT_MIN, VAL_MIN):
    """Verifica se a cor está dentro das faixas do arco-íris."""
    r, g, b = [x/255 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s < SAT_MIN or v < VAL_MIN:
        return False
    for name, hmin, hmax in RAINBOW_HUE_RANGES:
        if hmin <= h <= hmax:
            return True
    return False

def is_non_rainbow(rgb, SAT_MIN, VAL_MIN):
    """Retorna True se a cor estiver fora das faixas do arco-íris."""
    return not is_rainbow_color(rgb, SAT_MIN, VAL_MIN)

def rgb_to_hex(rgb):
    """Converte RGB (0–255) em hexadecimal."""
    return "%02x%02x%02x" % tuple(int(round(x)) for x in rgb)

def to_wif_from_hex(hex_str):
    """Gera WIF comprimido e não comprimido (demonstrativos)."""
    if len(hex_str) < 64:
        hex_str = hex_str.ljust(64, "0")
    private_key_bytes = bytes.fromhex(hex_str[:64])

    # WIF não comprimido
    extended_uncompressed = b'\x80' + private_key_bytes
    checksum_uncompressed = hashlib.sha256(hashlib.sha256(extended_uncompressed).digest()).digest()[:4]
    final_uncompressed = extended_uncompressed + checksum_uncompressed
    wif_uncompressed = base58.b58encode(final_uncompressed).decode()

    # WIF comprimido
    extended_compressed = b'\x80' + private_key_bytes + b'\x01'
    checksum_compressed = hashlib.sha256(hashlib.sha256(extended_compressed).digest()).digest()[:4]
    final_compressed = extended_compressed + checksum_compressed
    wif_compressed = base58.b58encode(final_compressed).decode()

    return wif_uncompressed, wif_compressed

def pseudo_inverse_wif(hex_str):
    """Cria um pseudo-inverso do hex baseado em Mersenne (2^31-1)."""
    if len(hex_str) < 64:
        hex_str = hex_str.ljust(64, "0")
    num = int(hex_str[:64], 16)
    mersenne = 2**31 - 1  # número de Mersenne
    inverse = mersenne - (num % mersenne)
    inv_hex = f"{inverse:064x}"
    wif_uncompressed, wif_compressed = to_wif_from_hex(inv_hex)
    return wif_uncompressed, wif_compressed

# === CARREGAR IMAGEM ===
img = Image.open(IMG_PATH).convert("RGB")
width, height = img.size
pixels = np.array(img)

# === VALORES A TESTAR ===
SAT_VALUES = [0.25, 0.3, 0.35]
VAL_VALUES = [0.3, 0.4, 0.5]

# === LOOP PRINCIPAL ===
for SAT_MIN in SAT_VALUES:
    for VAL_MIN in VAL_VALUES:
        for COLS in range(1, 100):  # Colunas de 1 até 99
            cell_w = width // COLS
            cell_h = height // ROWS

            non_rainbow_cells = []
            hex_values = []
            seen = set()  # evita repetições

            for i in range(ROWS):
                for j in range(COLS):
                    x1, y1 = j * cell_w, i * cell_h
                    x2, y2 = x1 + cell_w, y1 + cell_h
                    cell = pixels[y1:y2, x1:x2]
                    avg_color = cell.mean(axis=(0, 1))
                    hex_color = rgb_to_hex(avg_color)
                    if is_non_rainbow(avg_color, SAT_MIN, VAL_MIN):
                        if hex_color not in seen:
                            seen.add(hex_color)
                            hex_values.append(hex_color)
                            non_rainbow_cells.append((i, j))

            full_hex = ''.join(hex_values)
            if len(full_hex) >= 64:
                wif_uncompressed, wif_compressed = to_wif_from_hex(full_hex)
                wif_inv_uncompressed, wif_inv_compressed = pseudo_inverse_wif(full_hex)
                #print(f"SAT_MIN={SAT_MIN:.2f} | VAL_MIN={VAL_MIN:.2f} | COLS={COLS} | Cores fora do arco-íris: {len(non_rainbow_cells)}")
                print(f"  WIF não comprimido: {wif_uncompressed}")
                print(f"  WIF comprimido:     {wif_compressed}")
                print(f"  WIF inverso não comprimido: {wif_inv_uncompressed}")
                print(f"  WIF inverso comprimido:     {wif_inv_compressed}")
            else:
                print(f"SAT_MIN={SAT_MIN:.2f} | VAL_MIN={VAL_MIN:.2f} | COLS={COLS} | Fora do arco-íris: {len(non_rainbow_cells)} | HEX muito curto para WIF\n")
