import socket
import json
import base64
import logging
from concurrent.futures import ThreadPoolExecutor

server_address = ('127.0.0.1', 6669)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
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
    return send_command("LIST")

def remote_upload(filename=""):
    try:
        with open(filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        command_str = f"UPLOAD {filename}|||{encoded}"
        return send_command(command_str)
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}

def remote_download(filename=""):
    hasil = send_command(f"DOWNLOAD {filename}")
    if hasil['status'] == 'OK':
        try:
            base64.b64decode(hasil['data'])  # Simpan atau abaikan
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
    with ThreadPoolExecutor(max_workers=workers) as executor:
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