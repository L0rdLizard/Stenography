import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct
import random

def dct2(block):
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def text_to_bits(text):
    bits = ''.join(format(ord(char), '08b') for char in text)
    return bits

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    text = ''.join(chr(int(char, 2)) for char in chars)
    return text

def embed_message(image_path, message, alpha, seed_key=42, M0=5):
    # Open image and convert to YCbCr
    img = Image.open(image_path).convert('YCbCr')
    img_array = np.array(img)
    
    # Convert message to bits
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
        
        dct_indices = [(3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4)]
        idx1, idx2 = dct_indices[bit_index % len(dct_indices)], dct_indices[(bit_index + 1) % len(dct_indices)]
        coef1, coef2 = dct_block[idx1], dct_block[idx2]

        if message_bits[bit_index] == '0':
            if abs(coef1) - abs(coef2) <= M0:
                dct_block[idx1] += alpha
                dct_block[idx2] -= alpha
        else:
            if abs(coef1) - abs(coef2) > M0:
                dct_block[idx1] -= alpha
                dct_block[idx2] += alpha
        
        img_array[i:i+8, j:j+8, 0] = idct2(dct_block)
        bit_index += 1

    # Save stego image
    stego_image = Image.fromarray(img_array, mode='YCbCr').convert('RGB')
    stego_image.save("stego_output.bmp")

    return bits_count

def extract_message(stego_path, bits_count, alpha, seed_key=42, M0=5):
    # Open stego image
    stego_img = np.array(Image.open(stego_path).convert('YCbCr'))

    extracted_bits = ""
    bit_index = 0

    random.seed(seed_key)
    all_indexes = [(i, j) for i in range(0, stego_img.shape[0], 8) for j in range(0, stego_img.shape[1], 8)]
    random.shuffle(all_indexes)

    dct_indices = [(3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4)]
    for i, j in all_indexes:
        if bit_index >= bits_count:
            break

        block = stego_img[i:i+8, j:j+8, 0].astype(float)
        dct_block = dct2(block)

        idx1, idx2 = dct_indices[bit_index % len(dct_indices)], dct_indices[(bit_index + 1) % len(dct_indices)]
        coef1, coef2 = dct_block[idx1], dct_block[idx2]

        if abs(coef1) - abs(coef2) > M0:
            extracted_bits += '0'
        else:
            extracted_bits += '1'

        bit_index += 1

    return bits_to_text(extracted_bits)

def main():
    image_path = 'clown.bmp'
    message = 'your_secret_message'
    alpha = 0.5  # Пороговое значение для изменения коэффициентов

    # Встраиваем сообщение в изображение
    print("Embedding message...")
    bits_count = embed_message(image_path, message, alpha)
    print(f"Embedded {bits_count} bits into the image.")

    # Извлекаем сообщение из изображения
    stego_path = 'stego_output.bmp'
    print("Extracting message...")
    extracted_message = extract_message(stego_path, bits_count, alpha)
    print(f"Extracted message: {extracted_message}")

if __name__ == "__main__":
    main()
