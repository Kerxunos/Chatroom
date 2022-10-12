try:
    import socket
    import sys
    import os
    import time
    from colorama import Style, init, Fore
    import logging
    logging.basicConfig(filename='Server_INFO.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
    init(autoreset=True)
except ModuleNotFoundError as e:
    print(Fore.YELLOW + "[*] Gerekli olan modülleri indirmek istermisiniz ?")
    soru = input("(Y/N): ")
    if soru == "Y":
        os.system("pip install colorama")
        print(Fore.GREEN + "Moduller indirildi !")
    if soru == "N":
        print(Fore.RED + "[!] hiç bir modül indirilmedi, eğer hata alırsanız aracı yeniden başlatın ve modülleri yükleyin")
        time.sleep(2)
#SON GÜNCELLEME TARİH: 9.10.2022
#GÜNCELLEME YENİLİKLERİ: colorama ve logging kullanıma sunuldu
#GÜNCELLEME BUGLARI: /client_ip ip_rule isimli değişkene atandığı için kod yürüyebiliyor fakat client_ip hem ip_rule hem de msg değişkenine bağlı ip_rule çalışınca kod ilerliyor ve msg de çalışıyor bu yüzden client'e 2 kez /clien_ip mesajı gidiyor ve uygulama bozuluyor
#TAHMİNİ DEBUG TARİHİ: 12.10.2022
print(Fore.RED + "Bu uygulama loglama sistemine sahiptir lütfen saygı çerçevesinde ve kibarca konuşmaya dikkat edin !")
time.sleep(2)
print("Araç başlatılıyor...")
time.sleep(2)
print("""             ________  ______   _____ __________ _    ____________ ®
            /  _/ __ \/ ____/  / ___// ____/ __ \ |  / / ____/ __ \ 
            / // /_/ / /       \__ \/ __/ / /_/ / | / / __/ / /_/ /
          _/ // _, _/ /___    ___/ / /___/ _, _/| |/ / /___/ _, _/ 
         /___/_/ |_|\____/   /____/_____/_/ |_| |___/_____/_/ |_|  
         by @Kerxunos                                             v2.65(Beta)""")
time.sleep(2)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(Fore.GREEN + "[*] Fiziksel soket oluşturuldu !")
time.sleep(2)
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(f"[*] IP Adresiniz: {ip}")
logging.info(f"Server IP: {ip}")
time.sleep(1)
print(Fore.YELLOW + "[*] Serveri LocalHost(127.0.0.1) yada IP adresinize kurmanız gerekmektedir")
time.sleep(0.75)
print("[*] Port Numarasını 5000'den büyük seçmeniz önerilir")
time.sleep(2)
host = str(input("Bind IP: "))
port = int(input("Bind Port: "))
print(Fore.GREEN + f"[*] Bind: {host} Port: {port}")
logging.info(f"[*] Bind: {host} Port: {port}")
time.sleep(1)
s.bind((host, port))
print("İstemci bağlantısı bekleniyor...")
s.listen(1)
conn, addr = s.accept()
print(Fore.GREEN + "Bağlantı kurtuldu !")
uname = input("Kullanıcı adı giriniz: ")
logging.info(f"Server Username: {uname}")
uname1 = uname.encode()
conn.send(uname1)
print("istemci kullanıcı adı bekleniyor...")
cli_uname = conn.recv(1024)
cli_uname = cli_uname.decode()
print(Fore.GREEN + f"istemci kullanıcı adı: {cli_uname}")
logging.info(f"Client Username: {cli_uname}")
time.sleep(2)
print("Admin(Server) Commands: /shutdown, /kick, /client_ip, /clear, ")
while True:
    try:
        msg = input(f"({uname})--> ")
        if msg == "/shutdown":
            msg1 = msg.encode()
            conn.send(msg1)
            print("kapatılıyor...")
            s.close()
            sys.exit(0)
        if msg == "/client_ip":
            ip_rule = "/client_ip"
            ip_rule = ip_rule.encode()
            conn.send(ip_rule)
            print("İstemci IP Bilgisi alınıyor...")
            cli_ip = conn.recv(2048)
            cli_ip = cli_ip.decode()
            print(f"İstemci IP Adresi: {cli_ip}\n")
            logging.info(f"Client IP: {cli_ip}")
            time.sleep(2)
        if msg == "/clear":
            os.system("cls")
        print(f"{uname}: {msg}")
        logging.info(f"{uname}: {msg}")
        msg1 = msg.encode()
        conn.send(msg1)
        print(f"Client({cli_uname}) yazıyor...")
        cli_msg = conn.recv(1024)
        cli_msg = cli_msg.decode()
        print(f"{cli_uname}: {cli_msg}")
        logging.info(f"{cli_uname}: {cli_msg}")
    except KeyboardInterrupt as e:
        print("Bizi tercih ettiğiniz için teşekkürler !")
        time.sleep(1)
        sys.exit(0)
        
