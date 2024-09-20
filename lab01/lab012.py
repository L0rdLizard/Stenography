import os

# Функция для преобразования текста в бинарный формат
def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

# Функция для преобразования бинарного формата в текст
def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

# Внедрение сообщения в файл-контейнер (через пробелы в конце предложения)
def embed_message_in_spaces(file_path, message, output_path):
    message_bits = text_to_bits(message)
    message_length = len(message_bits)

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if message_length > len(lines):
        raise ValueError("Сообщение слишком длинное для данного контейнера.")

    embedded_lines = []
    bit_index = 0
    for line in lines:
        if bit_index < message_length:
            bit = message_bits[bit_index]
            if bit == '0':
                # Добавляем один пробел (бит 0)
                line = line.rstrip() + ' \n'
            else:
                # Добавляем два пробела (бит 1)
                line = line.rstrip() + '  \n'
            bit_index += 1
        embedded_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(embedded_lines)

    return bit_index

# Извлечение сообщения из контейнера (по количеству пробелов в конце строки)
def extract_message_from_spaces(file_path, message_length):
    message_bits = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        # Определяем количество пробелов в конце строки
        if line.endswith('  \n'):
            message_bits.append('1')
        elif line.endswith(' \n'):
            message_bits.append('0')

        if len(message_bits) >= message_length * 8:
            break

    bits_str = ''.join(message_bits[:message_length * 8])
    return bits_to_text(bits_str)

# Функция для расчета коэффициента сокрытия и информационной ёмкости
def calculate_capacity_and_efficiency(file_path, message_length):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    capacity = len(lines)  # 1 бит на строку
    efficiency = (message_length * 8) / capacity if capacity > 0 else 0

    return capacity, efficiency

# Пример использования
if __name__ == "__main__":
    container_file = "text.txt"
    output_file = "stego_text_spaces.txt"
    message = "Hello, World!"

    # Внедрение сообщения
    try:
        bits_embedded = embed_message_in_spaces(container_file, message, output_file)
        print(f"Внедрено {bits_embedded} бит.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        exit(1)

    # Извлечение сообщения
    extracted_message = extract_message_from_spaces(output_file, len(message))
    print(f"Извлеченное сообщение: {extracted_message}")

    # Расчет емкости и коэффициента сокрытия
    capacity, efficiency = calculate_capacity_and_efficiency(container_file, len(message))
    print(f"Информационная ёмкость контейнера: {capacity} бит.")
    print(f"Коэффициент сокрытия: {efficiency:.2%}")
