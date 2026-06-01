import subprocess
from datetime import datetime, timedelta


INPUT_FILE = "upload"
OUTPUT_FILE = "data.tar.gz"
DELTA = 15 * 3600 # 15 hours in seconds, to adjust for AM/PM and current time differences


def invoke_openssl(key :str):
    # Encryption command was :
    # openssl enc -aes-256-cbc -salt -in /tmp/.backup/data.tar.gz -out /tmp/.encrypted_data.enc -k $ENCRYPT_KEY

    # The name of the exported file from wireshark is "upload", we kept it in the decryption command.
    # The decryption command therefore would be :
    # openssl enc -d -aes-256-cbc -in upload -out data.tar.gz -k "$ENCRYPT_KEY"

    return subprocess.run(
            [
                "openssl", "enc", "-d", "-aes-256-cbc",
                "-in", INPUT_FILE,
                "-out", OUTPUT_FILE,
                "-k", key
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        ).stdout

def is_gz_file(filepath):
    # found at https://stackoverflow.com/a/47080739
    with open(filepath, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b'

if __name__ == "__main__":
    REF_DATE = datetime.strptime("2026-04-30 11:00:15.000000", "%Y-%m-%d %H:%M:%S.%f") # UTC
    ref_timestamp = int(REF_DATE.timestamp())

    for timestamp in range(ref_timestamp - DELTA, ref_timestamp + DELTA + 1):
        key = hex(timestamp)[2:]
        result = invoke_openssl(key)

        # first test to segregate bad results
        if "bad decrypt" not in result:

            # most important test
            if is_gz_file(OUTPUT_FILE):
                print(f"Decryption successful with key: {key}")
                print(result)
                break