import socket
import sys
import os
from threading import *
import _thread
import time
print("Gerekli olan modülleri indirmek istermisiniz ?")
soru = input("(Y/N): ")
if soru == "Y":
    os.system("pip install socket")
    os.system("pip install sys")
    os.system("pip install time")
    os.system("pip install threading")
if soru == "N":
    print("hiç bir modül indirilmedi, eğer hata alırsanız aracı yeniden başlatın ve modülleri yükleyin")
    time.sleep(2)
print("Araç başlatılıyor...")
time.sleep(2)
print("""             ________  ______   _____ __________ _    ____________ ®
            /  _/ __ \/ ____/  / ___// ____/ __ \ |  / / ____/ __ \ 
            / // /_/ / /       \__ \/ __/ / /_/ / | / / __/ / /_/ /
          _/ // _, _/ /___    ___/ / /___/ _, _/| |/ / /___/ _, _/ 
         /___/_/ |_|\____/   /____/_____/_/ |_| |___/_____/_/ |_|  
         by @Larry                                             v2.65""")
time.sleep(2)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Fiziksel soket oluşturuldu !")
time.sleep(2)
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"[*] IP Adresiniz: {ip}")
time.sleep(1)
print("[*] Serveri LocalHost(127.0.0.1) yada IP adresinize kurmanız gerekmektedir")
time.sleep(0.75)
print("[*] Port Numarasını 5000'den büyük seçmeniz önerilir")
time.sleep(2)
host = str(input("Bind IP: "))
port = int(input("Bind Port: "))
print(f"[*] Bind: {host} Port: {port}")
time.sleep(1)
s.bind((host, port))
print("İstemci bağlantısı bekleniyor...")

s.listen(1)
conn, addr = s.accept()
print("Bağlantı kurtuldu !")
uname = input("Kullanıcı adı giriniz: ")
uname1 = uname.encode()
conn.send(uname1)
print("istemci kullanıcı adı bekleniyor...")
cli_uname = conn.recv(1024)
cli_uname = cli_uname.decode()
print(f"istemci kullanıcı adı: {cli_uname}")
time.sleep(2)
while True:
    try:
        print("Admin(Server) Commands: /kick, /client_ip")
        msg = input(f"({uname})--> ")
        print(f"{uname}: {msg}")
        msg1 = msg.encode()
        conn.send(msg1)
        print(f"Client({cli_uname}) yazıyor...")
        cli_msg = conn.recv(1024)
        cli_msg = cli_msg.decode()
        print(f"{cli_uname}: {cli_msg}")
    except KeyboardInterrupt as e:
        print("Bizi tercih ettiğiniz için teşekkürler !")
        sys.exit(0)
        