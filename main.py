import requests
import time
import random
import os
import logging
from colorama import Fore, Style, init
from pathlib import Path

init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [ %(levelname)s ] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

DEFAULT_SLEEP_TIMEOUT = 10  # Atur timeout sesuai kebutuhan

def baca_file_hash():
    try:
        file_path = Path(__file__).parent / "data.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return [line.strip() for line in content.split("\n") if line.strip()]
    except Exception as e:
        logging.error(f"Error membaca data.txt:", exc_info=e)
        raise e

def ulangi(fn, retries=5, delay=2):
    for percobaan in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            if percobaan == retries:
                logging.error(f"Error setelah {retries} percobaan")
                raise e
            time.sleep(delay)

def login(hash_param):
    url = f"https://api.djdog.io/telegram/login?{hash_param}"
    return ulangi(lambda: requests.get(url).json()['data'])

def koleksi_hewan(token, klik):
    url = "https://api.djdog.io/pet/collect"
    headers = {"Authorization": token}
    params = {"clicks": klik}
    return ulangi(lambda: requests.post(url, headers=headers, params=params).json()['data'])

def dapatkan_jumlah_bar(token):
    url = "https://api.djdog.io/pet/barAmount"
    headers = {"Authorization": token}
    return ulangi(lambda: requests.get(url, headers=headers).json()['data'])

def dapatkan_kotak_mall(token):
    url = "https://api.djdog.io/pet/boxMall"
    headers = {"Authorization": token}
    return ulangi(lambda: requests.get(url, headers=headers).json()['data'])

def dapatkan_daftar_tugas(token):
    url = "https://api.djdog.io/task/list"
    headers = {"Authorization": token}
    return ulangi(lambda: requests.get(url, headers=headers).json()['data']['taskDetails'])

def selesaikan_tugas(token, id_tugas):
    url = f"https://api.djdog.io/task/finish?taskIds={id_tugas}"
    headers = {"Authorization": token}
    return ulangi(lambda: requests.post(url, headers=headers).json())

def tingkatkan_level(token):
    url = "https://api.djdog.io/pet/levelUp/1"
    headers = {"Authorization": token}
    return ulangi(lambda: requests.post(url, headers=headers).json()['returnCode'] == 200)

def prompt_user(pesan, default='n'):
    response = input(pesan).strip().lower()
    return response == 'y' if response in ['y', 'n'] else default == 'y'

def perulangan_utama(hash_param, otomatis_selesaikan_tugas, otomatis_tingkatkan_level):
    try:
        data = login(hash_param)
        token = data['accessToken']
        username = data['telegramUsername']
        logging.info(f"Login sebagai {Fore.LIGHTCYAN_EX}{username}")

        time.sleep(2)
        if otomatis_tingkatkan_level:
            status = "Berhasil" if tingkatkan_level(token) else "Gagal"
            logging.info(f"Auto LevelUP: {Fore.GREEN if status == 'Berhasil' else Fore.RED}{status}")
            time.sleep(2)

        if otomatis_selesaikan_tugas:
            daftar_tugas = dapatkan_daftar_tugas(token)
            for tugas in daftar_tugas:
                if not tugas['finished']:
                    try:
                        response = selesaikan_tugas(token, tugas['taskId'])
                        status = "Berhasil" if response['returnCode'] == 200 else "Gagal"
                        color = Fore.LIGHTGREEN_EX if status == "Berhasil" else Fore.RED
                        logging.info(f"Task ID: {Fore.YELLOW}{tugas['taskId']} | {Fore.YELLOW}Reward: {Fore.LIGHTGREEN_EX}{tugas['reward']} | Status: {color}{status}")
                    except Exception as e:
                        logging.error(f"Error saat memproses tugas {tugas['taskId']}, dilewati", exc_info=e)
                    time.sleep(2)

        while True:
            klik = random.randint(131, 433)
            hasil_koleksi = koleksi_hewan(token, klik)
            time.sleep(2)
            jumlah_bar = dapatkan_jumlah_bar(token)
            time.sleep(2)
            kotak_mall = dapatkan_kotak_mall(token)
            time.sleep(2)
            logging.info(f"Clik {Fore.LIGHTGREEN_EX}+{hasil_koleksi['amount']} | {Fore.YELLOW}Level: {Fore.LIGHTGREEN_EX}{kotak_mall['level']} | {Fore.YELLOW}Saldo: {Fore.LIGHTGREEN_EX}{kotak_mall['goldAmount']} | {Fore.YELLOW}Energi {Fore.LIGHTGREEN_EX}{jumlah_bar['availableAmount']}/{jumlah_bar['barGoldLimit']}")
            if jumlah_bar['availableAmount'] < 50:
                break
    except Exception as e:
        logging.error(f"Error: {e}")

def main():
    try:
        hashes = baca_file_hash()
        otomatis_tingkatkan_level = prompt_user("\nAuto upgrade Level Max (Y or N ) (Default N): ", 'n')
        otomatis_selesaikan_tugas = prompt_user("Auto Clear Task (Y or N ) (Default N): ", 'n')
        delay = int(input("Masukkan delay (detik) antara siklus: "))

        while True:
            for hash_param in hashes:
                perulangan_utama(hash_param, otomatis_selesaikan_tugas, otomatis_tingkatkan_level)
            logging.info(f"Semua akun telah diproses, delay selama {delay} detik")
            time.sleep(delay)
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    print(r"""                         
	 ____        _            ____   ___ _____ 
	|  _ \  ___ (_) ___ _ __ | __ ) / _ \_   _|
	| | | |/ _ \| |/ _ \ '_ \|  _ \| | | || |  
	| |_| |  __/| |  __/ | | | |_) | |_| || |  
	|____/ \___|/ |\___|_| |_|____/ \___/ |_|  
	          |__/                             
    ┌──────────────────────────┐
    │ By ZUIRE AKA Aureola     │
    └──────────────────────────┘
    """)
    main()
