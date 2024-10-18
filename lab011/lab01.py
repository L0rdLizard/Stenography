import os

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def embed_message_in_invisible_chars(file_path, message, output_path):
    message_bits = text_to_bits(message)
    message_length = len(message_bits)

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if message_length > len(lines):
        raise ValueError("Too long message")

    embedded_lines = []
    bit_index = 0
    for line in lines:
        if bit_index < message_length:
            bit = message_bits[bit_index]
            if bit == '1':
                line = line.rstrip() + '\u200B\n'
            else:
                line = line.rstrip() + '\n'
            bit_index += 1
        embedded_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(embedded_lines)

    return bit_index

def extract_message_from_invisible_chars(file_path, message_length):
    message_bits = []

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if line.endswith('\u200B\n'):
            message_bits.append('1')
        else:
            message_bits.append('0')

        if len(message_bits) >= message_length * 8:
            break

    bits_str = ''.join(message_bits[:message_length * 8])
    return bits_to_text(bits_str)

def calculate_capacity_and_efficiency(file_path, message_length):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    capacity = len(lines)
    efficiency = (message_length * 8) / capacity if capacity > 0 else 0

    return capacity, efficiency

if __name__ == "__main__":
    container_file = "text.txt"
    output_file = "stego_text_invisible.txt"
    message = "Hello world"

    try:
        bits_embedded = embed_message_in_invisible_chars(container_file, message, output_file)
        print(f"Внедрено {bits_embedded} бит.")
    except ValueError as e:
        print(f"Ошибка: {e}")
        exit(1)

    extracted_message = extract_message_from_invisible_chars(output_file, len(message))
    print(f"Извлеченное сообщение: {extracted_message}")

    capacity, efficiency = calculate_capacity_and_efficiency(container_file, len(message))
    print(f"Информационная ёмкость контейнера: {capacity} бит.")
    print(f"Коэффициент сокрытия: {efficiency:.2%}")
