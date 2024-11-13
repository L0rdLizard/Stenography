import random
import numpy as np
from PIL import Image
import math
import scipy.fftpack

# Русские буквы, которые мы будем отображать в диапазон ASCII от 128 до 159
russian_to_ascii = {
    'А': 128, 'Б': 129, 'В': 130, 'Г': 131, 'Д': 132, 'Е': 133, 'Ж': 134, 'З': 135, 'И': 136, 'Й': 137,
    'К': 138, 'Л': 139, 'М': 140, 'Н': 141, 'О': 142, 'П': 143, 'Р': 144, 'С': 145, 'Т': 146, 'У': 147,
    'Ф': 148, 'Х': 149, 'Ц': 150, 'Ч': 151, 'Ш': 152, 'Щ': 153, 'Ъ': 154, 'Ы': 155, 'Ь': 156, 'Э': 157,
    'Ю': 158, 'Я': 159, 'а': 128, 'б': 129, 'в': 130, 'г': 131, 'д': 132, 'е': 133, 'ж': 134, 'з': 135,
    'и': 136, 'й': 137, 'к': 138, 'л': 139, 'м': 140, 'н': 141, 'о': 142, 'п': 143, 'р': 144, 'с': 145,
    'т': 146, 'у': 147, 'ф': 148, 'х': 149, 'ц': 150, 'ч': 151, 'ш': 152, 'щ': 153, 'ъ': 154, 'ы': 155,
    'ь': 156, 'э': 157, 'ю': 158, 'я': 159
}
ascii_to_russian = {v: k for k, v in russian_to_ascii.items()}

def text_to_bits(text):
    bits = []
    for char in text:
        if char in russian_to_ascii:
            bits.append(format(russian_to_ascii[char], '08b'))
        else:
            bits.append(format(ord(char), '08b'))
    return ''.join(bits)

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        ascii_code = int(byte, 2)
        chars.append(chr(ascii_code))
        # if 128 <= ascii_code <= 159:
        #     chars.append(ascii_to_russian[ascii_code])
        # else:
        #     chars.append(chr(ascii_code))
    return ''.join(chars)

def dct2(block):
    return scipy.fftpack.dct(scipy.fftpack.dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    return scipy.fftpack.idct(scipy.fftpack.idct(block.T, norm='ortho').T, norm='ortho')

def embed_message(image_path, message, seed_key=42):
    img = Image.open(image_path).convert('YCbCr')
    img_array = np.array(img)
    
    message_bits = text_to_bits(message)
    bits_count = len(message_bits)
    random.seed(seed_key)
    all_indexes = [(i, j) for i in range(0, img_array.shape[0], 8) for j in range(0, img_array.shape[1], 8)]
    random.shuffle(all_indexes)
    
    bit_index = 0
    for i, j in all_indexes:
        if bit_index >= bits_count:
            break
        block = img_array[i:i+8, j:j+8, 0].astype(float)
        dct_block = dct2(block)
        
        # Choose two symmetric coefficients in mid-frequency range
        c1, c2 = (3, 5), (5, 3)
        
        # Embed the bit
        if message_bits[bit_index] == '1':
            if abs(dct_block[c1]) < abs(dct_block[c2]):
                dct_block[c1], dct_block[c2] = dct_block[c2], dct_block[c1]
        else:
            if abs(dct_block[c1]) > abs(dct_block[c2]):
                dct_block[c1], dct_block[c2] = dct_block[c2], dct_block[c1]
                
        img_array[i:i+8, j:j+8, 0] = idct2(dct_block)
        bit_index += 1
    
    stego_image = Image.fromarray(img_array, mode='YCbCr').convert('RGB')
    stego_image.save("stego_output.bmp")
    return bits_count

def extract_message(stego_path, bits_count, seed_key=42):
    stego_img = np.array(Image.open(stego_path).convert('YCbCr'))
    extracted_bits = ""
    
    random.seed(seed_key)
    all_indexes = [(i, j) for i in range(0, stego_img.shape[0], 8) for j in range(0, stego_img.shape[1], 8)]
    random.shuffle(all_indexes)
    
    bit_index = 0
    for i, j in all_indexes:
        if bit_index >= bits_count:
            break
        block = stego_img[i:i+8, j:j+8, 0].astype(float)
        dct_block = dct2(block)
        
        c1, c2 = (3, 5), (5, 3)
        
        # Extract the bit
        if abs(dct_block[c1]) > abs(dct_block[c2]):
            extracted_bits += '1'
        else:
            extracted_bits += '0'
            
        bit_index += 1
    
    return bits_to_text(extracted_bits)

# Test the updated implementation
input_image = "clown.bmp"
message = "Love GUAP and SUAI!"

bits_embedded = embed_message(input_image, message)
print(f"Number of embedded bits: {bits_embedded}")

extracted_message = extract_message("stego_output.bmp", bits_embedded)
print(f"Extracted message: {extracted_message}")
