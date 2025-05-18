import socket
import json
import base64
import logging

server_address = ('progjar-mesin-1', 6669)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"connecting to {server_address}")
        sock.sendall((command_str + "\r\n\r\n").encode())

        data_received = ""
        while True:
            data = sock.recv(4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = json.loads(data_received.strip())
        return hasil
    except Exception as e:
        logging.warning(f"Error: {e}")
        return {'status': 'ERROR', 'data': str(e)}
    finally:
        sock.close()

def remote_list():
    hasil = send_command("LIST")
    if hasil['status'] == 'OK':
        print("\nDaftar File di Server:")
        for file in hasil['data']:
            print(f"- {file}")
        return hasil['data']
    else:
        print("Gagal mengambil daftar file:", hasil.get('data'))
        return []

def remote_upload(filename=""):
    try:
        with open(filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        command_str = f"UPLOAD {filename}|||{encoded}"
        hasil = send_command(command_str)
        if hasil['status'] == 'OK':
            print(f"Upload file '{filename}' berhasil.")
        else:
            print("Gagal upload:", hasil.get('data'))
    except Exception as e:
        print("Gagal membuka file:", str(e))

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print(f"File '{filename}' berhasil dihapus.")
    else:
        print("Gagal hapus:", hasil.get('data'))

def remote_download(filename=""):
    command_str = f"DOWNLOAD {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        try:
            filedata = base64.b64decode(hasil['data'])
            with open(filename, "wb") as f:
                f.write(filedata)
            print(f"File '{filename}' berhasil di-download.")
        except Exception as e:
            print(f"Gagal menyimpan file: {e}")
    else:
        print("Gagal download:", hasil.get('data'))

def main():
    while True:
        print("\n====================")
        filelist = remote_list()

        print("\nPilih Feature:")
        print("1. Upload File")
        print("2. Hapus File")
        print("3. Download File")
        print("4. Keluar")
        pilihan = input("Masukkan pilihan (1/2/3/4): ").strip()

        if pilihan == '1':
            filename = input("Masukkan nama file lokal yang akan diupload: ").strip()
            remote_upload(filename)

        elif pilihan == '2':
            if not filelist:
                print("Tidak ada file di server.")
                continue
            filename = input("Masukkan nama file yang akan dihapus dari server: ").strip()
            if filename in filelist:
                remote_delete(filename)
            else:
                print("File tidak ditemukan di server.")

        elif pilihan == '3':
            if not filelist:
                print("Tidak ada file di server.")
                continue
            filename = input("Masukkan nama file yang akan di-download dari server: ").strip()
            if filename in filelist:
                remote_download(filename)
            else:
                print("File tidak ditemukan di server.")

        elif pilihan == '4':
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == '__main__':
    main()