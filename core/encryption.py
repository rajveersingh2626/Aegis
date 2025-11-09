from cryptography.fernet import Fernet
import os
import configparser
from colorama import Fore, Style

cipher= None


try:
    config = configparser.ConfigParser()
    config.read('.aegisconfig')

    ENCRYPTION_KEY = config['SECURITY']['ENCRYPTION_KEY'].encode()
    cipher = Fernet(ENCRYPTION_KEY)

except Exception as e:
    print(Fore.RED + f"[CRITICAL] Encryption Initialization Error: {e}" + Style.RESET_ALL)
    print(Fore.YELLOW + "WARNING: Using a temporary key. Please fix .aegisconfig!")

    cipher=Fernet(Fernet.generate_key())


def encrypt_data(data: str) -> str:
    try:
        token = cipher.encrypt(data.encode())
        return token.decode()
    except Exception as e:
        print(f"[ENCRYPTION ERROR] Could not encrypt data: {e}")
        return data


def decrypt_data(encrypted_data: str) -> str:
    try:
        decrypted_data = cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        print(f"[DECRYPTION ERROR] Failed to decrypt data: {e}")
        return "ERROR: DECRYPTION FAILED"

try:
    config = configparser.ConfigParser()
    config.read('.aegisconfig')
    ENCRYPTION_KEY = config['SECURITY']['ENCRYPTION_KEY'].encode()

    cipher = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"[CRITICAL] Encryption key loading error! Check .aegisconfig: {e}")
    cipher = Fernet(Fernet.generate_key())
