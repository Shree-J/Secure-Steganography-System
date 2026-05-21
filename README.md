# Secure Image Steganography using BLAKE3, AES-GCM and Adaptive RGB Embedding

## Overview

This project implements a secure steganography system that combines:

- BLAKE3 hashing
- AES-GCM encryption
- Zstandard compression
- Adaptive RGB channel embedding
- Image generation from cryptographic hash

The system securely hides encrypted files inside images while maintaining visual quality.

---

# Features

✅ BLAKE3-based key hashing  
✅ Artistic image generation from hash  
✅ Zstandard lossless compression  
✅ AES-GCM authenticated encryption  
✅ Adaptive RGB embedding algorithm  
✅ XOR-based extraction mechanism  
✅ Memory usage monitoring  
✅ Latency measurement  

---

# Technologies Used

- Python
- OpenCV
- NumPy
- Pillow
- Cryptography
- Zstandard
- BLAKE3

---

# System Workflow

1. User enters secret key
2. BLAKE3 generates cryptographic hash
3. Hash generates artistic image
4. Secret file is compressed using Zstandard
5. Compressed file encrypted using AES-GCM
6. Encrypted bytes embedded into RGB channels
7. Embedded image generated
8. Data extracted using XOR comparison
9. AES decryption and decompression restore original file

---

# Project Architecture

```text
Input File
    ↓
Compression (ZSTD)
    ↓
AES-GCM Encryption
    ↓
Adaptive RGB Embedding
    ↓
Stego Image

Stego Image
    ↓
XOR Extraction
    ↓
AES Decryption
    ↓
ZSTD Decompression
    ↓
Recovered File
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/Secure-Steganography-System.git
cd Secure-Steganography-System
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Project

```bash
python src/All_Code.py
```

---

# Example Usage

## Input

- Secret file: `secret.txt`
- Cover image: `cover.png`

## Output

- Generated artistic image
- Embedded stego image
- Recovered encrypted file
- Final decrypted file

---

# Screenshots

## Generated Image

(Add screenshot here)

## Embedded Output

(Add screenshot here)

## Terminal Output

(Add screenshot here)

---

# Security Features

- AES-GCM provides confidentiality and authentication
- BLAKE3 provides high-speed cryptographic hashing
- Adaptive RGB embedding minimizes visible distortion
- Compression reduces embedding size

---

# Future Improvements

- GUI interface
- Deep learning based adaptive embedding
- SSIM optimization
- Video steganography support
- Multi-layer encryption
- GPU acceleration

---

# Performance Metrics

The project measures:

- Memory usage
- Peak memory
- Encryption time
- Total execution latency

---

# Applications

- Secure communication
- Digital watermarking
- Confidential data transfer
- Multimedia security
- Military communication systems

---

# Author

Your Name

---

# License

MIT License