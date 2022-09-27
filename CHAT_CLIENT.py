import os
import socket
import sys
from threading import *
import _thread
import time

# Dikkat: socket, sys, time ve threading modülleri Python Standart Kütüphanesi'nde bulunmaktadır.
#
#print("Gerekli olan modülleri indirmeniz gerekmektedir indirmek istermisiniz ?")
#soru = input("(Y/N): ")
#if soru == "Y":
#    os.system("pip install socket")
#    os.system("pip install sys")
#    os.system("pip install time")
#if soru == "N":
#    print("hiç bir modül indirilmedi, eğer hata alırsanız aracı yeniden başlatın ve modülleri yükleyin")
#    time.sleep(2)
#

print("Araç başlatılıyor...")
time.sleep(2)
print("""         ________  ______   ________    ___________   ________ ®
        /  _/ __ \/ ____/  / ____/ /   /  _/ ____/ | / /_  __/
        / // /_/ / /      / /   / /    / // __/ /  |/ / / /   
      _/ // _, _/ /___   / /___/ /____/ // /___/ /|  / / /    
     /___/_/ |_|\____/   \____/_____/___/_____/_/ |_/ /_/
         by @Larry                                         v2.65 """)
time.sleep(2)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print("Fiziksel soket oluşturuldu !")
time.sleep(2)
print("[*] Serveri LocalHost(127.0.0.1) yada IP adresinize kurmanız gerekmektedir")
time.sleep(0.75)
print("[*] Port Numarasını 5000'den büyük seçmeniz önerilir")
time.sleep(2)
host = str(input("Server IP: "))
port = int(input("Server Port: "))
print(f"[*] Host: {host} Port: {port}")
time.sleep(1)
print("Server'a bağlanmaya çalışıyoruz...")
s.connect((host, port))

print("Server'a bağlanıldı !")
uname = input("Kullanıcı adı giriniz: ")
print("Serverin kullanıcı adı bekleniyor...")
uname1 = uname.encode()
s.send(uname1)
ser_uname = s.recv(1024)
ser_uname = ser_uname.decode()
print(f"Server kullanıcı adı: {ser_uname}")
time.sleep(2)

while True:
    try:
        print(f"Server({ser_uname}) yazıyor...")
        ser_msg = s.recv(1024)
        ser_msg = ser_msg.decode()
        if ser_msg == "/kick":
            print("Server tarafından kicklendiniz")
            time.sleep(2)
            sys.exit(0)
        print(f"{ser_uname}: {ser_msg}")
        msg = input(f"{uname}--> ")
        print(f"{uname}: {msg}")
        msg1 = msg.encode()
        s.send(msg1)
    except KeyboardInterrupt as e:
        print("Bizi tercih ettiğiniz için teşekkürler !")
        sys.exit(0)
