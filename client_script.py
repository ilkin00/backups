import os
import tarfile
import socket
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)
server_backup_dir = "/tmp/received_backups"
os.makedirs(server_backup_dir, exist_ok=True)

def open_port(port):
    # UFW vasitəsilə portu aç
    subprocess.run(["ufw", "allow", str(port)], check=True)

def close_port(port):
    # UFW vasitəsilə portu bağla
    subprocess.run(["ufw", "deny", str(port)], check=True)

@app.route("/notify", methods=["POST"])
def notify():
    filename = request.form.get("filename")
    if filename:
        transfer_port = 9000
        open_port(transfer_port)
        return jsonify({"port": transfer_port}), 200
    return jsonify({"error": "Fayl adı verilməyib"}), 400

def receive_backup_file(transfer_port):
    s = socket.socket()
    s.bind(("", transfer_port))
    s.listen(1)
    conn, addr = s.accept()

    received_file = os.path.join(server_backup_dir, "backup_received.tar.gz")
    with open(received_file, "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    conn.close()
    s.close()

    return received_file

def validate_backup_file(received_file):
    try:
        with tarfile.open(received_file, "r:gz") as tar:
            tar.extractall(path="/tmp/validate")
        with open("/tmp/backup_validation.txt", "w") as f:
            f.write("Backup doğrulandı: OK")
        return True
    except Exception as e:
        with open("/tmp/backup_validation.txt", "w") as f:
            f.write(f"Validation failed: {e}")
        return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # Server API portu

    transfer_port = 9000
    received_file = receive_backup_file(transfer_port)
    if validate_backup_file(received_file):
        print("Backup doğrulandı!")
    else:
        print("Backup doğrulama uğursuz oldu.")
    close_port(transfer_port)  # Portu bağla
