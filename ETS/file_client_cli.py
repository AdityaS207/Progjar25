import socket
import json
import base64
import time
import os
from concurrent.futures import ThreadPoolExecutor

server_address = ('127.0.0.1', 6669)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        sock.sendall((command_str + "\r\n\r\n").encode())

        data_received = b''
        while True:
            data = sock.recv(65536)
            if data:
                data_received += data
                if b"\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = json.loads(data_received.strip().decode())
        return hasil
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}
    finally:
        sock.close()

def remote_list():
    return send_command("LIST")

def chunked_base64_encode(file_path, chunk_size=64*1024):
    encoded = ''
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            encoded += base64.b64encode(chunk).decode('utf-8')
    return encoded

def remote_upload(filename=""):
    try:
        encoded = chunked_base64_encode(filename)
        command_str = f"UPLOAD {filename}|||{encoded}"
        return send_command(command_str)
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}

def remote_download(filename=""):
    hasil = send_command(f"DOWNLOAD {filename}")
    if hasil['status'] == 'OK':
        try:
            base64.b64decode(hasil['data'])
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}
    return hasil

def stress_test(operation="list", filename=None, workers=5):
    def task():
        start_time = time.time()
        result = None
        if operation == "list":
            result = remote_list()
        elif operation == "upload":
            result = remote_upload(filename)
        elif operation == "download":
            result = remote_download(filename)
        end_time = time.time()
        return result['status'], end_time - start_time

    results = []
    max_workers = min(workers, 50)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for _ in range(workers)]
        for future in futures:
            results.append(future.result())

    total_time = sum(t for s, t in results)
    success_count = sum(1 for s, t in results if s == 'OK')
    failed_count = len(results) - success_count
    throughput = sum(os.path.getsize(filename) / t for s, t in results if s == 'OK') if operation != "list" else 0

    return {
        "total_time": total_time,
        "throughput": throughput,
        "success_count": success_count,
        "failed_count": failed_count
    }
