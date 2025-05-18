import socket
import threading
import os
import json
import base64

SERVER_ADDRESS = ('0.0.0.0', 6669)
BUFFER_SIZE = 4096
FILES_DIR = 'files'

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

def handle_client(conn, addr):
    try:
        data_received = ""
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break

        request = data_received.strip().replace("\r\n\r\n", "")
        response = process_request(request)
        conn.sendall(response.encode())
    except Exception as e:
        error_msg = json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"
        conn.sendall(error_msg.encode())
    finally:
        conn.close()

def process_request(request):
    if request == "LIST":
        files = [f for f in os.listdir(FILES_DIR) if os.path.isfile(os.path.join(FILES_DIR, f))]
        return json.dumps({'status': 'OK', 'data': files}) + "\r\n\r\n"

    elif request.startswith("UPLOAD "):
        try:
            parts = request.split(" ", 1)[1]
            filename, encoded = parts.split("|||", 1)
            filepath = os.path.join(FILES_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(encoded))
            return json.dumps({'status': 'OK', 'data': f'File {filename} uploaded'}) + "\r\n\r\n"
        except Exception as e:
            return json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"

    elif request.startswith("DELETE "):
        filename = request.split(" ", 1)[1].strip()
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.exists(filepath):
            return json.dumps({'status': 'ERROR', 'data': 'File tidak ditemukan'}) + "\r\n\r\n"
        try:
            os.remove(filepath)
            return json.dumps({'status': 'OK', 'data': f'File {filename} deleted'}) + "\r\n\r\n"
        except Exception as e:
            return json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"

    elif request.startswith("DOWNLOAD "):
        filename = request.split(" ", 1)[1].strip()
        filepath = os.path.join(FILES_DIR, filename)
        if not os.path.exists(filepath):
            return json.dumps({'status': 'ERROR', 'data': 'File tidak ditemukan'}) + "\r\n\r\n"
        try:
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return json.dumps({'status': 'OK', 'data': encoded}) + "\r\n\r\n"
        except Exception as e:
            return json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"

    else:
        return json.dumps({'status': 'ERROR', 'data': 'request tidak dikenali'}) + "\r\n\r\n"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(SERVER_ADDRESS)
    sock.listen(5)
    print(f"Server listening on {SERVER_ADDRESS}")

    try:
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        sock.close()

if __name__ == '__main__':
    main()