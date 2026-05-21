import blake3 as blake3

# import cv2
import numpy as np
import hashlib
import math
import matplotlib.pyplot as plt
import os
import zstandard as zstd
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import sys
import time
import psutil
import tracemalloc
tracemalloc.start()
current, peak = tracemalloc.get_traced_memory()
print(f"🔍 Current memory usage: {current / 1024 / 1024:.2f} MB")
key = input("Enter the key to hash: ")
file=input("Enter the file name that Save in image:").strip()
size_bytes = os.path.getsize(file)
encrfile=None
decrfile=None

width=math.ceil(math.sqrt(size_bytes))
height=math.ceil(math.sqrt(size_bytes))
start_time = time.time()  # Start timing
def Hash_BALKE3(key):
    key_bytes = key.encode('utf-8')
    hash_object = blake3(key_bytes)

    hex_digest = hash_object.hexdigest()
    print(hex_digest)
    return hex_digest

def ImageCreateFromHash(hash, width, height):
    def md5_to_seed(key: str) -> int:
        md5_hash = hashlib.md5(key.encode()).hexdigest()
        return int(md5_hash, 16) % (2**32)

    def generate_color_pattern(seed: int, width, height):
        np.random.seed(seed)
        base = np.zeros((height, width, 3), dtype=np.uint8)
    
        for i in range(3):  # R, G, B
            x = np.linspace(0, 1, width)
            y = np.linspace(0, 1, height)
            xv, yv = np.meshgrid(x, y)
            pattern = (xv * 255 * np.random.rand() + yv * 255 * np.random.rand()) % 255
            noise = (np.random.rand(height, width) * 60).astype(np.uint8)
            base[:, :, i] = np.clip(pattern + noise, 0, 255).astype(np.uint8)
    
        return base

    def apply_artistic_edges(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=5)
        edges = cv2.convertScaleAbs(edges)
        edges_colored = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
        blended = cv2.addWeighted(img, 0.7, edges_colored, 0.3, 0)
        return blended

    def create_beautiful_image_from_key(key: str, width, height):
        seed = md5_to_seed(key)
        base_img = generate_color_pattern(seed, width, height)
        final_img = apply_artistic_edges(base_img)
        return final_img

    img = create_beautiful_image_from_key(hash, width, height)

    end_time = time.time()  # End timing
    processing_time = end_time - start_time

    success = cv2.imwrite("Main.png", img)
    if success:
        print(f"✅ Image created and saved successfully in {processing_time:.3f} seconds")
    else:
        print("❌ Something went wrong while creating image")

def Compress_Encryption(HK,DataFile):
    def compress_file(input_path: str) -> bytes:
        with open(input_path, 'rb') as f:
            data = f.read()
        cctx = zstd.ZstdCompressor()
        compressed = cctx.compress(data)
        return compressed

    def encrypt_data(data: bytes, key: bytes) -> bytes:
        if len(key) != 32:
            raise ValueError("❌ Invalid key length. Must be 32 bytes.")
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        encrypted = aesgcm.encrypt(nonce, data, None)
        return nonce + encrypted

    def save_to_file(path: str, data: bytes):
        global encrfile
        with open(path, 'wb') as f:
            f.write(data)
        encrfile=path
        print(f"✅ Encrypted file saved to: {path}")

    def main():
        input_file = DataFile
        hash_hex = HK

        base_dir = os.path.dirname(input_file)
        base_name = os.path.basename(input_file)

        # Default output file: same name + '.zst.aes'
        output_file = os.path.join(base_dir, base_name + ".zst.aes")

        try:
            key = bytes.fromhex(hash_hex)
        except ValueError:
            print("❌ Invalid hex key format.")
            sys.exit(1)

        try:
            compressed = compress_file(input_file)
            encrypted = encrypt_data(compressed, key)
            save_to_file(output_file, encrypted)
        except Exception as e:
            print("❌ Encryption or compression failed:", str(e))

    main()

def OneOfRGB(HK):
    def read_aes_file(path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def embed_file_in_image(image_path: str, aes_data: bytes, output_path: str):
        img = Image.open(image_path).convert("RGB")
        pixels = img.load()
        width, height = img.size

        total_pixels = width * height
        if len(aes_data) > total_pixels:
            raise ValueError("❌ File too large for the image!")

        index = 0
        for y in range(height):
            for x in range(width):
                if index >= len(aes_data):
                    break

                r, g, b = pixels[x, y]
                val = aes_data[index]

                diffs = {
                    'r': abs(r - val),
                    'g': abs(g - val),
                    'b': abs(b - val),
                }

               
                sorted_channels = sorted(diffs.items(), key=lambda item: item[1])

                
                if sorted_channels[0][1] == 0:
                    target_channel = sorted_channels[1][0]  # second smallest
                else:
                    target_channel = sorted_channels[0][0]  # smallest

               
                if target_channel == 'r':
                    r = val
                elif target_channel == 'g':
                    g = val
                else:
                    b = val

                pixels[x, y] = (r, g, b)
                index += 1

        img.save(output_path)
        print(f"✅ Embedded {index} bytes into {output_path}.")

    if __name__ == "__main__":
        key_hash = HK
        aes_path = encrfile
        image_path = input("🖼️ Enter Cover image Name: ").strip()
        output_path = "output_embedded.png"

        aes_data = read_aes_file(aes_path)
        embed_file_in_image(image_path, aes_data, output_path)

def Image_to_AES():
    def extract_bytes_from_xor(original_img_path, embedded_img_path, output_file_path):
        global decrfile
        original = Image.open(original_img_path).convert("RGB")
        embedded = Image.open(embedded_img_path).convert("RGB")

        if original.size != embedded.size:
            raise ValueError("❌ Images must be the same size!")

        width, height = original.size
        orig_pixels = original.load()
        emb_pixels = embedded.load()

        recovered_bytes = []

        for y in range(height):
            for x in range(width):
                r1, g1, b1 = orig_pixels[x, y]
                r2, g2, b2 = emb_pixels[x, y]

                
                xor_r = r1 ^ r2
                xor_g = g1 ^ g2
                xor_b = b1 ^ b2

            
                if xor_r != 0 and xor_g == 0 and xor_b == 0:
                    recovered_bytes.append(r2)
                elif xor_g != 0 and xor_r == 0 and xor_b == 0:
                    recovered_bytes.append(g2)
                elif xor_b != 0 and xor_r == 0 and xor_g == 0:
                    recovered_bytes.append(b2)
                
                else:
                    continue

        
        with open(output_file_path, "wb") as f:
            f.write(bytes(recovered_bytes))
        decrfile=output_file_path
        print(f"✅ Recovered {len(recovered_bytes)} bytes into: {output_file_path}")

    if __name__ == "__main__":
        original_image_path = "Main.png"            
        embedded_image_path = "output_embedded.png" 
        output_aes_file = "retrieved.zst.aes"

        extract_bytes_from_xor(original_image_path, embedded_image_path, output_aes_file)

def Decompress_And_Decrypt(HK):
    def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        # print(f" Nonce: {nonce.hex()}")
        # print(f" Ciphertext length: {len(ciphertext)} bytes")
    
        aesgcm = AESGCM(key)
        try:
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            print("✅ AES decryption successful")
            return decrypted
        except Exception as e:
            raise RuntimeError(f"❌ AES decryption failed: {e}")

    def decompress_data(compressed_data: bytes) -> bytes:
        try:
            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(compressed_data)
            print("✅ Zstandard decompression successful")
            return decompressed
        except Exception as e:
            raise RuntimeError(f"❌ Decompression failed: {e}")

    def save_output_file(output_path: str, data: bytes):
        with open(output_path, "wb") as f:
            f.write(data)
        print(f"✅ Final decompressed data saved to: {output_path}")

    def main():
        encrypted_file = decrfile
        output_file = input("📝 Enter output path for decompressed file (e.g. output.txt): ").strip()
        hash_hex = HK

        try:
            key = bytes.fromhex(hash_hex)
            if len(key) != 32:
                print("❌ Key must be 32 bytes.")
                return
        except ValueError:
            print("❌ Invalid hex key format.")
            return

        try:
            with open(encrypted_file, "rb") as f:
                encrypted = f.read()
            print(f"📦 Encrypted file size: {len(encrypted)} bytes")

            decrypted_compressed = decrypt_data(encrypted, key)
            decompressed_data = decompress_data(decrypted_compressed)
            save_output_file(output_file, decompressed_data)

        except Exception as e:
            print(str(e))

    if __name__ == "__main__":
        main()
    


start_time = time.perf_counter()
Key_Hash=Hash_BALKE3(key)
#print(Key_Hash)
ImageCreateFromHash(Key_Hash, width, height)
Compress_Encryption(Key_Hash,file)

OneOfRGB(Key_Hash)

print("=====================================================Decryption PART ===================================================")
Image_to_AES()
Decompress_And_Decrypt(Key_Hash)
end_time = time.perf_counter()
# print(f"⏱️ High-Precision Latency: {end_time - start_time:.9f} seconds")
current, peak = tracemalloc.get_traced_memory()
print(f"📈 Peak memory usage: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
