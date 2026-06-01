import os
from pwn import xor
import random


# Original code
SIZE = 128

class Verify:
    def __init__(self, bits):
        self.k = bits
        self.n = len(bits)

    def verify_all(self):
        assert all(sum(self.k[i:i + 4]) % 2 == 1 for i in range(0, self.n, 4)), "E1"
        assert all(self.k[2 * i + 2] for i in range(self.n // 4) if not (self.k[i] == self.k[4 * i])), "E2"
        assert all(len(set(self.k[i:i + 3])) > 1 for i in range(self.n - 2)), "E3"
        assert all(sum(self.k[i:i + 8]) == 4 for i in range(self.n - 7)), "E4"
        assert all(self.k[i] ^ self.k[self.n - 1 - i] for i in range(self.n // 2)), "E5"


# Additional functions
MAX_TRIES = 2 * 10 ** 4


def bytes_to_bits_list(data: bytes) -> list[int]:
    return [int(b) for b in format(int(data.hex(), 16), f'0{len(data) * 8}b')]

def bits_list_to_bytes(bits: list[int]) -> bytes:
    return int(''.join(map(str, bits)), 2).to_bytes(len(bits) // 8, 'big')

def print_key_bits(key_bits: list[int]):
    print(''.join(map(str, key_bits)))

FLAG_CHARSET = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{}_$"
def is_good_flag_candidate(flag_candidate: bytes) -> bool:
    real_start_ind = len('404CTF{')

    return flag_candidate.startswith(b"404CTF{") \
        and flag_candidate.endswith(b"}") \
        and all(b in FLAG_CHARSET for b in flag_candidate) \
        and flag_candidate[real_start_ind] in b'sS5' and flag_candidate[real_start_ind + 1] in b'oO0'

def generate_key_candidate(already_deduced_bits: list[int]) -> list[int]:
    return [random.choice([0, 1]) if x == 'X' else x for x in already_deduced_bits]


# Main code

with open("ciphertext.txt", "r") as f:
    ciphertext = bytes.fromhex(f.read().strip())

# === Recovering the first key bits ===
key_bits = ['X'] * SIZE

# Because of the properties of XOR, we can deduce some first and last bits of the key
ciphertext_bits = bytes_to_bits_list(ciphertext)
flag_start_bits = bytes_to_bits_list(b"404CTF{")

for i in range(len(flag_start_bits)):
    key_bits[i] = flag_start_bits[i] ^ ciphertext_bits[i]

print("Deduced from flag prefix:")
print_key_bits(key_bits)


# === Recover the remaining bits thanks to the constraints ===

# Using E5
# assert all(self.k[i] ^ self.k[self.n - 1 - i] for i in range(self.n // 2)), "E5"
for i in range(SIZE // 2):
    if key_bits[i] == 'X' and key_bits[SIZE - 1 - i] == 'X':
        continue

    if key_bits[i] == 'X':
        key_bits[i] = key_bits[SIZE - 1 - i] ^ 1
    elif key_bits[SIZE - 1 - i] == 'X':
        key_bits[SIZE - 1 - i] = key_bits[i] ^ 1

print("After E5:")
print_key_bits(key_bits)

# Using E2
# assert all(self.k[2 * i + 2] for i in range(self.n // 4) if not (self.k[i] == self.k[4 * i])), "E2"
for i in range(SIZE // 4):
    if key_bits[i] == 'X' or key_bits[4 * i] == 'X':
        continue

    if key_bits[i] != key_bits[4 * i]:
        key_bits[2 * i + 2] = 1

print("After E2:")
print_key_bits(key_bits)


# === Brute-force the remaining bits ===
print("[i] Brute-forcing the remaining bits...")
seen_flags_candidates = []
for _ in range(MAX_TRIES):
    candidate_key_bits = generate_key_candidate(key_bits)
    v = Verify(candidate_key_bits)
    try:
        v.verify_all()
        found = True
    except AssertionError:
        pass

    # Decryption attempt
    key = bits_list_to_bytes(candidate_key_bits)
    try:
        flag = xor(ciphertext, key)
        if is_good_flag_candidate(flag):
            if flag in seen_flags_candidates:
                continue
            seen_flags_candidates.append(flag)

            print(f"[+] Flag candidate found : {flag.decode()}")
    except Exception as e:
        pass

print(f"[i] Total candidates found: {len(seen_flags_candidates)}")