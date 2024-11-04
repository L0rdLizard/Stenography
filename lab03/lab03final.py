from PIL import Image
import numpy as np
from scipy.fft import dct, idct

class KochSteganography:
    def __init__(self, threshold=50):
        self.threshold = threshold
        self.dct_pairs = [
            ((3,4), (4,3)),
        ]  # Для начала используем только одну пару коэффициентов
    
    def _split_into_blocks(self, image):
        height, width = image.shape
        blocks = []
        positions = []
        for i in range(0, height-7, 8):  # Изменено условие, чтобы избежать неполных блоков
            for j in range(0, width-7, 8):
                block = image[i:i+8, j:j+8]
                if block.shape == (8, 8):
                    blocks.append(block)
                    positions.append((i, j))
        return blocks, positions

    def _embed_bit(self, dct_block, bit):
        pos1, pos2 = self.dct_pairs[0]
        
        if bit == 0:
            # Для бита 0 делаем первый коэффициент больше второго
            if dct_block[pos1] <= dct_block[pos2]:
                diff = abs(dct_block[pos1] - dct_block[pos2])
                adjustment = self.threshold + diff
                dct_block[pos1] += adjustment
                dct_block[pos2] -= adjustment
        else:
            # Для бита 1 делаем второй коэффициент больше первого
            if dct_block[pos1] >= dct_block[pos2]:
                diff = abs(dct_block[pos1] - dct_block[pos2])
                adjustment = self.threshold + diff
                dct_block[pos1] -= adjustment
                dct_block[pos2] += adjustment
                
        return dct_block

    def _extract_bit(self, dct_block):
        pos1, pos2 = self.dct_pairs[0]
        return 0 if dct_block[pos1] > dct_block[pos2] else 1

    def embed_message(self, image_path, message, output_path):
        # Загрузка изображения
        img = Image.open(image_path).convert('L')
        image = np.array(img, dtype=float)
        
        # Преобразование сообщения в биты
        binary_message = ''.join(format(ord(c), '08b') for c in message)
        message_length = len(binary_message)
        
        # Разбиение на блоки
        blocks, positions = self._split_into_blocks(image)
        
        if len(blocks) < message_length:
            raise ValueError("Изображение слишком маленькое для этого сообщения")
        
        # Встраивание битов
        for idx, bit in enumerate(binary_message):
            if idx < len(blocks):
                # DCT преобразование
                dct_block = dct(dct(blocks[idx].T, norm='ortho').T, norm='ortho')
                # Встраивание бита
                modified_dct = self._embed_bit(dct_block, int(bit))
                # Обратное DCT
                modified_block = idct(idct(modified_dct.T, norm='ortho').T, norm='ortho')
                # Обновление блока в изображении
                i, j = positions[idx]
                image[i:i+8, j:j+8] = modified_block
        
        # Сохранение результата
        Image.fromarray(np.uint8(np.clip(image, 0, 255))).save(output_path, 'BMP')
        
        # Сохраняем длину сообщения в последнем блоке
        with open(output_path, 'ab') as f:
            f.write(message_length.to_bytes(4, byteorder='big'))

    def extract_message(self, image_path, message_length):
        # Загрузка изображения
        img = Image.open(image_path).convert('L')
        image = np.array(img, dtype=float)
        
        # Получение блоков
        blocks, _ = self._split_into_blocks(image)
        
        # Извлечение битов
        extracted_bits = []
        for idx in range(message_length * 8):
            if idx < len(blocks):
                # DCT преобразование
                dct_block = dct(dct(blocks[idx].T, norm='ortho').T, norm='ortho')
                # Извлечение бита
                bit = self._extract_bit(dct_block)
                extracted_bits.append(str(bit))
        
        # Преобразование битов в символы
        binary_string = ''.join(extracted_bits)
        message = ''
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i+8]
            if len(byte) == 8:
                message += chr(int(byte, 2))
        
        return message

def main():
    # Создаем экземпляр класса с пороговым значением M0 = 50
    steganography = KochSteganography(threshold=50)
    
    # Тестовое сообщение
    message = "Love GUAP and evermore!"
    
    # Встраивание сообщения
    print("Встраивание сообщения...")
    steganography.embed_message('clown.bmp', message, 'output.bmp')
    print(f"Сообщение '{message}' встроено в изображение output.bmp")
    
    # Извлечение сообщения
    print("\nИзвлечение сообщения...")
    extracted_message = steganography.extract_message('output.bmp', len(message))
    print(f"Извлеченное сообщение: {extracted_message}")
    
    # Проверка корректности
    if message == extracted_message:
        print("\nУспех! Сообщение извлечено без искажений")
    else:
        print("\nОшибка! Извлеченное сообщение отличается от исходного")

if __name__ == "__main__":
    main()