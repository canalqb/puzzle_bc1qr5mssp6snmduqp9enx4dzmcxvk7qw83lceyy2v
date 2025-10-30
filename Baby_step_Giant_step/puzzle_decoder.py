import cv2
import numpy as np
from PIL import Image
import re
from collections import defaultdict
import math
import os
import sys

def baby_step_giant_step(a, b, n):
    """Baby-step Giant-step para resolver a^x ≡ b (mod n)"""
    try:
        m = int(math.ceil(math.sqrt(n)))
        
        table = {}
        power = 1
        for j in range(m):
            if power not in table:
                table[power] = j
            power = (power * a) % n
        
        factor = pow(a, m * (n - 2), n)
        
        gamma = b
        for i in range(m):
            if gamma in table:
                x = (i * m + table[gamma]) % (n - 1)
                if pow(a, x, n) == b:
                    return x
            gamma = (gamma * factor) % n
        
        return None
    except:
        return None

def cesar_shift(text, shift):
    """Aplica Cifra de César com shift específico"""
    result = []
    for char in text:
        if char.isalpha():
            if char.isupper():
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def extract_colored_characters(image_path):
    """Extrai caracteres coloridos da imagem"""
    if not os.path.exists(image_path):
        print(f"❌ Arquivo não encontrado: {image_path}")
        print(f"📁 Diretório atual: {os.getcwd()}")
        print(f"📄 Arquivos disponíveis:")
        for f in os.listdir('.')[:10]:
            print(f"   - {f}")
        return None, None
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Erro ao carregar: {image_path}")
        return None, None
    
    print(f"✅ Imagem carregada: {image_path}")
    print(f"   Dimensões: {img.shape}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    ranges = [
        (np.array([130, 50, 50]), np.array([170, 255, 255])),
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([170, 50, 50]), np.array([180, 255, 255])),
    ]
    
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lower, upper in ranges:
        mask |= cv2.inRange(hsv, lower, upper)
    
    cv2.imwrite('mask_debug.jpg', mask)
    print(f"✅ Máscara salva: mask_debug.jpg")
    
    return img, mask

def find_colored_positions(img, mask):
    """Encontra posições dos caracteres coloridos"""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    positions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        positions.append({'x': x, 'y': y, 'w': w, 'h': h})
    
    positions.sort(key=lambda p: (p['y'], p['x']))
    
    print(f"✅ {len(positions)} caracteres destacados encontrados")
    return positions

def brute_force_caesar(text):
    """Tenta todos os shifts de César"""
    print("\n" + "="*60)
    print("TESTANDO CIFRA DE CÉSAR (Todos os 26 shifts)")
    print("="*60)
    
    solutions = []
    keywords_pt = ['mensagem', 'chave', 'código', 'desafio', 'palavra', 'puzzle', 'resposta']
    
    for shift in range(26):
        decoded = cesar_shift(text, shift)
        solutions.append({'shift': shift, 'text': decoded})
        
        decoded_lower = decoded.lower()
        for keyword in keywords_pt:
            if keyword in decoded_lower:
                print(f"\n🎯 Shift {shift}: POSSÍVEL MATCH!")
                print(f"   {decoded[:100]}...")
                break
    
    return solutions

def main(image_file='puzzle.jpeg'):
    print("="*60)
    print("PUZZLE DECODER")
    print("Cifra de César + Baby-step Giant-step")
    print("="*60)
    print()
    
    # Carregar imagem
    img, mask = extract_colored_characters(image_file)
    if img is None:
        return
    
    print()
    
    # Texto do puzzle
    text = """T9U3V8W2Y0Z5R401B9M6J2K7H0L3X1Q5N8P7A4C9D3E6F2G8I7
S0T4U5V9W3Y6Z2R700B4M8J1K3H6L2X0Q4N9P1A5C7D8E2F6G3
I1S9T7U0V4W8Y5Z3R602B1M7J9K4H0L5X2Q8N3P6A1C4D7E9F5
G2I8S3T6U2V7W0Y4Z9R501B0M3J6K8H2L1X7Q9N4P0A2C5D3E8
F6G4I0S7T1U9V5W2Y8Z6R309B4M1J7K0H3L6X5Q2N8P1A9C4D2
E7F0G3I6S8T5U3V0W4Y7Z2R106B5M0J2K9H7L3X1Q4N8P6A3C1
D5E2F9G7I4S0T6U8V3W5Y1Z9R207B4M6J3K1H8L0X2Q5N9P7A4
C8D6E3F1G5I2S7T0U4V9W6Y3Z1R805B2M7J0K6H3L9X4Q1N5P8
A2C7D4E0F6G8I3S1T5U2V7W9Y0Z4R603B1M8J5K2H7L4X0Q3N9
P6A1C5D8E2F7G4I9S6T3U0V5W2Y8Z7R401B3M0J6K9H2L5X1Q7
N4P0A8C3D6E5F1G2I7S9T8U4V0W3Y5Z2R604B1M7J3K0H5L2X9
Q6N1P8A2C4D7E3F9G5I0S6T1U5V2W8Y7Z4R003B9M6J2K1H4L7
X3Q0N5P8A1C6D2E4F7G9I3S8T5U0V2W6Y1Z4R709B3M5J0K2H6
L4X8Q1N3P7A5C2D9E6F0G4I7S1T3U8V5W2Y6Z0R402B6M9J3K7
H0L5X2Q1N4P0A8C3D6E5F1G2I0S4T8U1V3W5Y7Z9R602B4M1J5
K0H3L6X4Q8N2P7A0C3D6E2F9G5I1S7T4U3V0W2Y6Z3R509B2M4
J1K7H3L0X5Q6N8P1A9C4D2E7F3G6I0S5T1U4V8W2Y7Z6R303B9
M5J2K1H4L7X0Q3N6P8A2C1D5E9F4G7T3S6T0U2V5W8Y1Z4R703
B2M6J0K9H5L3X1Q4N8P7A0C2D6E3F1G5I9S4T7U5V2W0Y6Z3R8
01B4M2J7K3H0L6X5Q1N9P8A3C2D5E7F4G6I0S3T8U1V7W2Y5Z9
R604B0M3J1K2H7L4X0Q6N5P8A1C9D3E6F2G5I7S4T0U3V2W8Y6"""
    
    # Limpar texto
    text_clean = ''.join(c for c in text if c.isalpha())
    print(f"✅ Texto extraído: {len(text_clean)} caracteres")
    
    # Encontrar posições coloridas
    positions = find_colored_positions(img, mask)
    print()
    
    # Brute force César
    solutions = brute_force_caesar(text_clean)
    
    # Baby-step Giant-step
    print("\n" + "="*60)
    print("TESTE BABY-STEP GIANT-STEP")
    print("="*60)
    
    a, b, n = 2, 3, 17
    result = baby_step_giant_step(a, b, n)
    print(f"Exemplo: {a}^x ≡ {b} (mod {n})")
    if result is not None:
        print(f"✅ Resultado: x = {result}")
        print(f"   Verificação: {a}^{result} mod {n} = {pow(a, result, n)}")
    else:
        print(f"❌ Solução não encontrada")
    
    # Números
    print("\n" + "="*60)
    print("ANÁLISE DE NÚMEROS")
    print("="*60)
    
    numbers = re.findall(r'\d+', text)
    print(f"Números encontrados: {len(numbers)}")
    if numbers:
        print(f"Primeiros 15: {numbers[:15]}")
    
    all_digits = ''.join(numbers)
    freq = defaultdict(int)
    for d in all_digits:
        freq[d] += 1
    
    print("\nFrequência de dígitos:")
    for digit in sorted(freq.keys()):
        print(f"  {digit}: {freq[digit]:3d} vezes")
    
    # Top 5 shifts
    print("\n" + "="*60)
    print("TOP 5 DECODIFICAÇÕES (Shifts de César)")
    print("="*60)
    
    for i in range(min(5, len(solutions))):
        shift = solutions[i]['shift']
        decoded = solutions[i]['text']
        print(f"\n{i+1}. Shift {shift}:")
        print(f"   {decoded[:80]}...")
    
    print("\n" + "="*60)
    print("✅ Análise concluída!")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    else:
        image_file = 'puzzle.jpeg'
    
    if not os.path.exists(image_file):
        alternatives = [
            './puzzle.jpeg',
            '../puzzle.jpeg',
            os.path.expanduser('puzzle.jpeg'),
        ]
        
        for alt in alternatives:
            if os.path.exists(alt):
                image_file = alt
                break
    
    main(image_file)
