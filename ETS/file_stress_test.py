import subprocess
import time
import os
import csv
import socket  # <-- Added
from file_client_cli import stress_test

# Konfigurasi
OPERATIONS = ['list', 'upload', 'download']
VOLUMES = ['test_files/test_10mb.bin', 'test_files/test_50mb.bin', 'test_files/test_100mb.bin']
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]
POOL_TYPES = ['thread']

results = []

def wait_for_server(timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket()
            sock.connect(('127.0.0.1', 6669))
            sock.close()
            return True
        except:
            time.sleep(0.2)
    return False

def run_server(pool_type, workers):
    print(f"[+] Starting server with {pool_type} pool, {workers} workers")
    return subprocess.Popen(
        ["python3", "file_server.py", "--type", pool_type, "--workers", str(workers)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def stop_server(proc):
    print("[!] Stopping server...")
    proc.terminate()
    proc.wait()

row_num = 1
for pool_type in POOL_TYPES:
    for sw in SERVER_WORKERS:
        server_proc = run_server(pool_type, sw)
        if not wait_for_server():
            print("[-] Gagal menunggu server")
            stop_server(server_proc)
            continue

        for op in OPERATIONS:
            for vol in VOLUMES:
                for cw in CLIENT_WORKERS:
                    if op != "list" and not os.path.exists(vol):
                        print(f"[-] File tidak ditemukan: {vol}")
                        continue

                    print(f"[{row_num}] Testing: {op}, {vol}, Client={cw}, Server={sw}, Pool={pool_type}")
                    res = stress_test(op, filename=vol, workers=cw)

                    results.append({
                        'No': row_num,
                        'Operasi': op,
                        'Volume': os.path.basename(vol),
                        'Client Worker': cw,
                        'Server Worker': sw,
                        'Jenis Pool': pool_type.capitalize(),
                        'Waktu Total': round(res['total_time'], 2),
                        'Throughput': round(res['throughput'], 2) if res['throughput'] else 0,
                        'Client Sukses': res['success_count'],
                        'Client Gagal': res['failed_count'],
                        'Server Sukses': res['success_count'],
                        'Server Gagal': res['failed_count'],
                    })
                    row_num += 1

        stop_server(server_proc)

# ✅ Only write if results are available
if results:
    keys = results[0].keys()
    with open('results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print("✅ Semua uji selesai. Hasil disimpan di 'results.csv'")
else:
    print("⚠️ Tidak ada hasil yang bisa ditulis. Pastikan server berjalan dan file uji ada.")
