from socket import *
import time

PORT = 45000
server_address = ('progjar-mesin-1', PORT)

def main():
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(server_address)

    try:
        while True:
            command = input("Ketik 'TIME' untuk waktu, 'QUIT' untuk keluar: ").strip().upper()
            if command not in ["TIME", "QUIT"]:
                print("Perintah tidak dikenali.")
                continue

            if command == "TIME":
                s.sendall(b"TIME\r\n")
            elif command == "QUIT":
                s.sendall(b"QUIT\r\n")
                print("Menutup koneksi.")
                break

            data = s.recv(1024)
            print("Dari server:", data.decode('utf-8').strip())

    except KeyboardInterrupt:
        print("Client dihentikan.")
    finally:
        s.close()

if __name__ == "__main__":
    main()
