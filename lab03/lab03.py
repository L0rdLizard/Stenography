import numpy as np
from PIL import Image
import random
import os

def embed_message(image_path, message, output_path, key):
    # Открытие изображения и преобразование в формат numpy массива
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)

    # Преобразование сообщения в двоичный формат
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    message_length = len(binary_message)
    
    random.seed(key)

    # Внедрение сообщения в изображение
    for bit in binary_message:
        # Выбор случайных координат для коэффициентов
        x1, y1 = random.randint(0, image_array.shape[0] - 1), random.randint(0, image_array.shape[1] - 1)
        x2, y2 = random.randint(0, image_array.shape[0] - 1), random.randint(0, image_array.shape[1] - 1)

        # Внедрение бита в разность пикселей
        if bit == '1':
            if image_array[x1, y1, 0] > image_array[x2, y2, 0]:
                image_array[x1, y1, 0], image_array[x2, y2, 0] = image_array[x2, y2, 0], image_array[x1, y1, 0]
        else:
            if image_array[x1, y1, 0] < image_array[x2, y2, 0]:
                image_array[x1, y1, 0], image_array[x2, y2, 0] = image_array[x2, y2, 0], image_array[x1, y1, 0]

    # Сохранение нового изображения с внедренным сообщением
    result_image = Image.fromarray(image_array)
    result_image.save(output_path)
    
    print(f'Количество внедренных бит: {message_length}')
    return message_length


def extract_message(image_path, message_length, key):
    # Открытие изображения и преобразование в формат numpy массива
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)

    random.seed(key)

    binary_message = ''
    # Извлечение сообщения из изображения
    for _ in range(message_length):
        # Выбор случайных координат для коэффициентов
        x1, y1 = random.randint(0, image_array.shape[0] - 1), random.randint(0, image_array.shape[1] - 1)
        x2, y2 = random.randint(0, image_array.shape[0] - 1), random.randint(0, image_array.shape[1] - 1)

        # Извлечение бита из разности пикселей
        if image_array[x1, y1, 0] > image_array[x2, y2, 0]:
            binary_message += '0'
        else:
            binary_message += '1'

    # Преобразование двоичного сообщения в текст
    extracted_message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8))
    return extracted_message

def check_resilience(image_path, message_length, key):
    # Открытие изображения и сохранение его в формате JPEG с сжатием
    image = Image.open(image_path)
    compressed_image_path = 'compressed_image.jpg'
    compressed_image = image.resize((image.width // 2, image.height // 2))
    compressed_image.save(compressed_image_path, format='JPEG', quality=50)

    # Загрузка сжатого изображения и восстановление сообщения
    compressed_image = Image.open(compressed_image_path).resize((image.width, image.height))
    compressed_image.save('restored_image.bmp')
    restored_message = extract_message('restored_image.bmp', message_length, key)
    
    # Оценка количества ошибок
    error_count = sum(1 for a, b in zip(message, restored_message) if a != b)
    return error_count, restored_message

def calculate_psnr(original_image_path, processed_image_path):
    # Открытие оригинального и обработанного изображений
    original_image = Image.open(original_image_path).convert('RGB')
    processed_image = Image.open(processed_image_path).convert('RGB')

    original_array = np.array(original_image)
    processed_array = np.array(processed_image)

    mse = np.mean((original_array - processed_array) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


image_path = 'clown.bmp'
message = 'Hello, world!'
output_path = 'output_image.bmp'
key = 12345
embed_message(image_path, message, output_path, key)

extracted_message = extract_message(output_path, len(message) * 8, key)
print(f'Извлеченное сообщение: {extracted_message}')

psnr_value = calculate_psnr(image_path, output_path)
print(f'PSNR для встраивания информации: {psnr_value} dB')

print()
error_count, restored_message = check_resilience(output_path, len(message) * 8, key)
print(f'Количество ошибок извлечения: {error_count}')
print(f'Восстановленное сообщение: {restored_message}')

print()
compressed_psnr_value = calculate_psnr(image_path, 'restored_image.bmp')
print(f'PSNR после сжатия и восстановления: {compressed_psnr_value} dB')