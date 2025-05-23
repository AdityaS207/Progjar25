import subprocess
import time
import os
import csv
from client_stress_test import stress_test

# Konfigurasi
OPERATIONS = ['list', 'upload', 'download']
VOLUMES = ['test_files/test_10mb.bin', 'test_files/test_50mb.bin', 'test_files/test_100mb.bin']
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]
POOL_TYPES = ['thread', 'process']

results = []

def run_server(pool_type, workers):
    print(f"[+] Starting server with {pool_type} pool, {workers} workers")
    return subprocess.Popen(
        ["python3", "server.py", "--type", pool_type, "--workers", str(workers)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def stop_server(proc):
    print("[!] Stopping server...")
    proc.terminate()
    proc.wait()

row_num = 1
for pool_type in POOL_TYPES:
    for sw in SERVER_WORKERS:
        # Jalankan server
        server_proc = run_server(pool_type, sw)
        time.sleep(2)  # Tunggu server siap

        for op in OPERATIONS:
            for vol in VOLUMES:
                for cw in CLIENT_WORKERS:
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

# Simpan hasil
keys = results[0].keys()
with open('results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(results)

print("✅ Semua uji selesai. Hasil disimpan di 'results.csv'")