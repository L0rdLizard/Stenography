from PIL import Image
import numpy as np
from scipy.fft import dct, idct

class KochSteganography:
    def __init__(self, threshold=50):
        self.threshold = threshold
        self.dct_pairs = [
            ((3,4), (4,3)),
        ]

    def _split_into_blocks(self, image):
        height, width = image.shape
        blocks = []
        positions = []
        for i in range(0, height-7, 8):
            for j in range(0, width-7, 8):
                block = image[i:i+8, j:j+8]
                if block.shape == (8, 8):
                    blocks.append(block)
                    positions.append((i, j))
        return blocks, positions

    def _embed_bit(self, dct_block, bit):
        pos1, pos2 = self.dct_pairs[0]
        if bit == 0:
            if dct_block[pos1] <= dct_block[pos2]:
                diff = abs(dct_block[pos1] - dct_block[pos2])
                adjustment = self.threshold + diff
                dct_block[pos1] += adjustment
                dct_block[pos2] -= adjustment
        else:
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
        img = Image.open(image_path).convert('RGB')
        image = np.array(img, dtype=float)

        binary_message = ''.join(format(ord(c), '08b') for c in message)
        message_length = len(binary_message)

        blocks = []
        positions = []
        for channel in range(3):
            channel_blocks, channel_positions = self._split_into_blocks(image[:,:,channel])
            blocks.extend(channel_blocks)
            positions.extend([(pos, channel) for pos in channel_positions])

        if len(blocks) < message_length:
            raise ValueError("Изображение слишком маленькое для этого сообщения")

        for idx, bit in enumerate(binary_message):
            if idx < len(blocks):
                dct_block = dct(dct(blocks[idx].T, norm='ortho').T, norm='ortho')
                modified_dct = self._embed_bit(dct_block, int(bit))
                modified_block = idct(idct(modified_dct.T, norm='ortho').T, norm='ortho')
                i, j = positions[idx][0]
                channel = positions[idx][1]
                image[i:i+8, j:j+8, channel] = modified_block

        Image.fromarray(np.uint8(np.clip(image, 0, 255))).save(output_path, 'BMP')

        with open(output_path, 'ab') as f:
            f.write(message_length.to_bytes(4, byteorder='big'))

    def extract_message(self, image_path, message_length):
        img = Image.open(image_path).convert('RGB')
        image = np.array(img, dtype=float)

        blocks = []
        for channel in range(3):
            channel_blocks, _ = self._split_into_blocks(image[:,:,channel])
            blocks.extend(channel_blocks)

        extracted_bits = []
        for idx in range(message_length * 8):
            if idx < len(blocks):
                dct_block = dct(dct(blocks[idx].T, norm='ortho').T, norm='ortho')
                bit = self._extract_bit(dct_block)
                extracted_bits.append(str(bit))

        binary_string = ''.join(extracted_bits)
        message = ''
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i+8]
            if len(byte) == 8:
                message += chr(int(byte, 2))

        return message

def main():
    steganography = KochSteganography(threshold=50)

    message = "Love GUAP and SUAI!"

    print("Встраивание сообщения...")
    steganography.embed_message('clown.bmp', message, 'output.bmp')
    print(f"Сообщение '{message}' встроено в изображение output.bmp")

    print("\nИзвлечение сообщения...")
    extracted_message = steganography.extract_message('output.bmp', len(message))
    print(f"Извлеченное сообщение: {extracted_message}")

    if message == extracted_message:
        print("\nУспех! Сообщение извлечено без искажений")
    else:
        print("\nОшибка! Извлеченное сообщение отличается от исходного")

if __name__ == "__main__":
    main()