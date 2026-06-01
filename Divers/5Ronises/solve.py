from time import time, sleep
from random import randint, seed
from hashlib import sha256
from functools import reduce
import socket


def set_seed(custom_seed: int):
    seed(custom_seed)

def matmul(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]

def genere_nombre_super_secret(n):
    A = [[randint(0, pow(2, 64)) for _ in range(n)] for _ in range(n)]
    
    for i in range(pow(2, 10)):
        A = matmul(A, A)
        A = [[y % pow(2, 64) for y in x] for x in A]

    base = reduce(lambda x, y: x ^ y, [reduce(lambda x, y: x ^ y, row) for row in A])

    hashed = sha256(hex(base).encode()).hexdigest()
    return int(hashed, 16)

def run_client(server_ip, server_port):
    DEBUG = False
    WAIT_TIME = 5
    TIME_DELTA = 0.1
    SLEEP_DELAY = 0.1
    
    # We pre-compute the secret number for in 30 seconds
    go_time = int(time()) + WAIT_TIME
    if DEBUG: print(f"Target time: {go_time} (in {WAIT_TIME} seconds)")
    set_seed(go_time)
    secret = genere_nombre_super_secret(8)
    if DEBUG: print(f"Computed secret done after {int(time()) - go_time + WAIT_TIME} seconds")

    while int(time()) < go_time - TIME_DELTA:
        sleep(SLEEP_DELAY)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    if DEBUG: print(f"Connected to server at {server_ip}:{server_port}")

    while True:
        msg = client.recv(1024).decode()
        if not msg:
            break
        if DEBUG: print('Received:' + msg)

        answer = str(secret)
        answer += '\n'
        client.send(answer.encode("utf-8")[:1024])
        if DEBUG: print(f"Sent: {answer}")

        # Flag
        msg = client.recv(1024).decode()
        print('Received:' + msg)

        break

    client.close()
    print("Connection to server closed")


run_client("localhost", 10200)
# run_client("challenge.404ctf.fr", 10200)