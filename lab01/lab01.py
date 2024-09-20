import os

# Функция для преобразования текста в бинарный формат
def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

# Функция для преобразования бинарного формата в текст
def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

# Внедрение сообщения в файл-контейнер
def embed_message_in_container(file_path, message, output_path):
    message_bits = text_to_bits(message)
    message_length = len(message_bits)

    with open(file_path, 'rb') as file:
        lines = file.readlines()

    if message_length > len(lines):
        raise ValueError("Сообщение слишком длинное для данного контейнера.")

    embedded_lines = []
    bit_index = 0
    for line in lines:
        if bit_index < message_length:
            bit = message_bits[bit_index]
            if bit == '0':
                # Закодировать бит 0 как LF
                line = line.rstrip(b'\r\n') + b'\n'
            else:
                # Закодировать бит 1 как CR+LF
                line = line.rstrip(b'\r\n') + b'\r\n'
            bit_index += 1
        embedded_lines.append(line)

    with open(output_path, 'wb') as output_file:
        output_file.writelines(embedded_lines)

    return bit_index

# Извлечение сообщения из контейнера
def extract_message_from_container(file_path, message_length):
    message_bits = []

    with open(file_path, 'rb') as file:
        lines = file.readlines()

    for line in lines:
        if line.endswith(b'\r\n'):
            message_bits.append('1')
        elif line.endswith(b'\n'):
            message_bits.append('0')

        if len(message_bits) >= message_length * 8:
            break

    bits_str = ''.join(message_bits[:message_length * 8])
    return bits_to_text(bits_str)

# Функция для расчета коэффициента сокрытия и информационной ёмкости
def calculate_capacity_and_efficiency(file_path, message_length):
    with open(file_path, 'rb') as file:
        lines = file.readlines()

    capacity = len(lines)  # 1 бит на строку
    efficiency = (message_length * 8) / capacity if capacity > 0 else 0

    return capacity, efficiency

# Функция для генерации примерного файла-контейнера
def generate_container_file(output_path, repeat=50):
    container_text = """This is a simple text container file.1
It contains several lines.
Each line will be used to hide one bit of a secret message.
The message will be encoded in the line endings.
"""
    with open(output_path, "w", newline='\n') as f:
        for _ in range(repeat):
            f.write(container_text)

# Пример использования
if __name__ == "__main__":
    container_file = "text.txt"
    output_file = "stego_text.txt"
    message = "Hello, World!"

    # Генерация файла-контейнера (если необходимо)
    if not os.path.exists(container_file):
        generate_container_file(container_file, repeat=100)
        print(f"Файл-контейнер '{container_file}' сгенерирован.")

    # Внедрение сообщения
    try:
        bits_embedded = embed_message_in_container(container_file, message, output_file)
        print(f"Внедрено {bits_embedded} бит.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        exit(1)

    # Извлечение сообщения
    extracted_message = extract_message_from_container(output_file, len(message))
    print(f"Извлеченное сообщение: {extracted_message}")

    # Расчет емкости и коэффициента сокрытия
    capacity, efficiency = calculate_capacity_and_efficiency(container_file, len(message))
    print(f"Информационная ёмкость контейнера: {capacity} бит.")
    print(f"Коэффициент сокрытия: {efficiency:.2%}")
