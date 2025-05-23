import socket
import os
import json
import base64
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

SERVER_ADDRESS = ('0.0.0.0', 6669)
BUFFER_SIZE = 65536
FILES_DIR = 'test_files'

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

_file_cache = []
_cache_time = 0
CACHE_TTL = 2

def get_cached_files():
    global _file_cache, _cache_time
    if time.time() - _cache_time > CACHE_TTL:
        _file_cache = [f for f in os.listdir(FILES_DIR) if os.path.isfile(os.path.join(FILES_DIR, f))]
        _cache_time = time.time()
    return _file_cache

def process_request(request):
    if request == "LIST":
        files = get_cached_files()
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

def handle_client(conn, addr):
    try:
        data_received = b''
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            data_received += data
            if b"\r\n\r\n" in data_received:
                break

        request = data_received.strip().replace(b"\r\n\r\n", b"").decode()
        response = process_request(request)
        conn.sendall(response.encode())
    except Exception as e:
        error_msg = json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"
        conn.sendall(error_msg.encode())
    finally:
        conn.close()

def start_server(pool_type="thread", pool_size=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDRESS)
    sock.listen(100)
    print(f"Server listening on {SERVER_ADDRESS} with {pool_type} pool size {pool_size}")

    if pool_type == "thread":
        executor = ThreadPoolExecutor(max_workers=pool_size)
    elif pool_type == "process":
        executor = ProcessPoolExecutor(max_workers=pool_size)
    else:
        raise ValueError("Invalid pool type")

    try:
        while True:
            conn, addr = sock.accept()
            executor.submit(handle_client, conn, addr)
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        sock.close()
        executor.shutdown(wait=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start server with thread/process pool.')
    parser.add_argument('--type', choices=['thread', 'process'], default='thread')
    parser.add_argument('--workers', type=int, default=5)
    args = parser.parse_args()

    start_server(pool_type=args.type, pool_size=args.workers)
