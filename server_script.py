import os
import tarfile
import requests
import socket

# Yedəkləmək üçün lazımlı klasörlər
# folders_to_backup = ["/var", "/usr", "/root", "/home"]
folders_to_backup = ["/home/Code/"]

# Yedəkləmə üçün faylın adı
backup_filename = "/tmp/backup.tar.gz"

def backup_system():
    with tarfile.open(backup_filename, "w:gz") as tar:
        for folder in folders_to_backup:
            tar.add(folder)

def send_backup_notification(server_ip, server_port):
    url = f"http://{server_ip}:{server_port}/notify"
    response = requests.post(url, data={"filename": os.path.basename(backup_filename)})
    if response.status_code == 200:
        return response.json().get('port')
    else:
        return None

def transfer_backup(server_ip, transfer_port):
    s = socket.socket()
    s.connect((server_ip, transfer_port))
    with open(backup_filename, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            s.send(data)
    s.close()

if __name__ == "__main__":
    backup_system()
    server_ip = "SERVER_IP_ADDRESS"  # Serverin IP ünvanı
    server_port = 8000  # API üçün port

    transfer_port = send_backup_notification(server_ip, server_port)
    if transfer_port:
        transfer_backup(server_ip, transfer_port)
    else:
        print("Serverlə əlaqə qurmaq alınmadı.")
