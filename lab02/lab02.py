import numpy as np
from PIL import Image
import math

def embed_text_lsb(image_path, text, output_path):
    img = Image.open(image_path)
    img_data = np.array(img)
    text_bin = ''.join(format(ord(char), '08b') for char in text) + '00000000'
    text_len = len(text_bin)
    height, width, _ = img_data.shape
    max_bits = height * width * 3

    if text_len > max_bits:
        raise ValueError("Текст слишком длинный для внедрения в изображение")

    bit_index = 0
    for i in range(height):
        for j in range(width):
            for k in range(3):
                if bit_index < text_len:
                    pixel_value = img_data[i, j, k]
                    img_data[i, j, k] = (pixel_value & 0xFE) | int(text_bin[bit_index])
                    bit_index += 1
                else:
                    break

    embedded_image = Image.fromarray(img_data.astype(np.uint8))
    embedded_image.save(output_path)

def extract_text_lsb(image_path):
    img = Image.open(image_path)
    img_data = np.array(img)
    extracted_bin = ""
    height, width, _ = img_data.shape

    for i in range(height):
        for j in range(width):
            for k in range(3):
                extracted_bin += str(img_data[i, j, k] & 1)

    extracted_text = ""
    for i in range(0, len(extracted_bin), 8):
        byte = extracted_bin[i:i+8]
        if byte == "00000000":
            break
        extracted_text += chr(int(byte, 2))
    
    return extracted_text

def calculate_psnr(original_image_path, modified_image_path):
    original_img = Image.open(original_image_path)
    modified_img = Image.open(modified_image_path)
    original_data = np.array(original_img, dtype=np.float64)
    modified_data = np.array(modified_img, dtype=np.float64)
    
    mse = np.mean((original_data - modified_data) ** 2)
    if mse == 0:
        return float('inf')
    
    max_pixel_value = 255.0
    psnr = 20 * math.log10(max_pixel_value / math.sqrt(mse))
    return psnr

if __name__ == "__main__":
    original_image = "clown.bmp"
    text = "Hello world!"
    output_image = "lsb_embedded_image.bmp"

    embed_text_lsb(original_image, text, output_image)
    extracted_text = extract_text_lsb(output_image)
    print(f"Output: {extracted_text}")
    psnr_value = calculate_psnr(original_image, output_image)
    print(f"PSNR: {psnr_value:.2f} dB")
