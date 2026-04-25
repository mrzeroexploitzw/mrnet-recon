import requests
import socket
import ssl
import sys
import os
import threading
from queue import Queue
from datetime import datetime

# =========================
# CONFIG
# =========================
REPORT_FILE = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# =========================
# SAVE REPORT
# =========================
def save_report(text):
    with open(REPORT_FILE, "a") as f:
        f.write(f"\n[{datetime.now()}]\n{text}\n")

# =========================
# BANNER
# =========================
def banner():
    os.system("clear || cls")
    print(GREEN + r"""
███╗   ███╗██████╗ ███╗   ██╗███████╗████████╗
████╗ ████║██╔══██╗████╗  ██║██╔════╝╚══██╔══╝
██╔████╔██║██████╔╝██╔██╗ ██║█████╗     ██║
██║╚██╔╝██║██╔══██╗██║╚██╗██║██╔══╝     ██║
██║ ╚═╝ ██║██║  ██║██║ ╚████║███████╗   ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝

        MRZEROEXPLOIT RECON PRO v5.0
""" + RESET)

# =========================
# GET SUBDOMAINS SAFE
# =========================
def get_subdomains(domain):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        r = requests.get(url, headers=headers, timeout=20)

        if r.status_code != 200 or not r.text.strip():
            return []

        try:
            data = r.json()
        except:
            return []

        subs = set()

        for item in data:
            name = item.get("name_value")
            if name:
                for sub in name.split("\n"):
                    if sub.endswith(domain):
                        subs.add(sub.strip().lower())

        return list(subs)

    except:
        return []

# =========================
# SUBDOMAIN SCAN
# =========================
def subdomain_scan(domain):
    print(YELLOW + "\n[+] Subdomain Scan\n" + RESET)

    subs = get_subdomains(domain)

    if not subs:
        print(RED + "No subdomains found or request blocked" + RESET)
        return

    for s in sorted(subs):
        print(GREEN + "[SUB] " + s + RESET)
        save_report(s)

# =========================
# ALIVE HOST SCAN
# =========================
def alive_hosts(domain):
    print(YELLOW + "\n[+] Alive Host Scan\n" + RESET)

    subs = get_subdomains(domain)

    if not subs:
        print(RED + "No subdomains available" + RESET)
        return

    print(f"[*] Checking {len(subs)} hosts...\n")

    for sub in subs:
        try:
            requests.get("https://" + sub, timeout=3)
            print(GREEN + "[LIVE] https://" + sub + RESET)
        except:
            try:
                requests.get("http://" + sub, timeout=3)
                print(GREEN + "[LIVE] http://" + sub + RESET)
            except:
                pass

# =========================
# DNS LOOKUP
# =========================
def dns_lookup(domain):
    print(YELLOW + "\n[+] DNS Lookup\n" + RESET)

    try:
        ip = socket.gethostbyname(domain)
        print(GREEN + "IP: " + ip + RESET)
    except:
        print(RED + "DNS failed" + RESET)

# =========================
# PORT SCAN
# =========================
def port_scan(host):
    print(YELLOW + "\n[+] Fast Port Scan\n" + RESET)

    try:
        ip = socket.gethostbyname(host)
    except:
        print(RED + "Invalid host" + RESET)
        return

    print(f"Target: {host} ({ip})")

    ports = list(range(1, 1025))
    queue = Queue()

    for port in ports:
        queue.put(port)

    scanned = 0
    total = len(ports)
    lock = threading.Lock()

    def scan():
        nonlocal scanned
        while not queue.empty():
            port = queue.get()
            s = socket.socket()
            s.settimeout(0.5)

            try:
                if s.connect_ex((ip, port)) == 0:
                    print(GREEN + f"\n[OPEN] {port}" + RESET)
            except:
                pass

            s.close()

            with lock:
                scanned += 1
                print(f"\rProgress: {scanned}/{total}", end="")

            queue.task_done()

    for _ in range(100):
        threading.Thread(target=scan, daemon=True).start()

    queue.join()
    print(GREEN + "\nScan complete" + RESET)

# =========================
# SSL CHECK
# =========================
def ssl_checker(domain):
    print(YELLOW + "\n[+] SSL Check\n" + RESET)

    try:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(socket.socket(), server_hostname=domain)
        s.settimeout(5)
        s.connect((domain, 443))
        print(GREEN + str(s.getpeercert()) + RESET)
        s.close()
    except Exception as e:
        print(RED + str(e) + RESET)

# =========================
# HEADER INTEL
# =========================
def header_intel(domain):
    print(YELLOW + "\n[+] Header Intelligence\n" + RESET)

    try:
        try:
            r = requests.get("https://" + domain, timeout=5)
        except:
            r = requests.get("http://" + domain, timeout=5)

        for k, v in r.headers.items():
            print(GREEN + f"{k}: {v}" + RESET)
    except Exception as e:
        print(RED + str(e) + RESET)

# =========================
# IP INFO
# =========================
def ip_info(ip):
    print(YELLOW + "\n[+] IP Info\n" + RESET)

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        for k, v in r.json().items():
            print(GREEN + f"{k}: {v}" + RESET)
    except Exception as e:
        print(RED + str(e) + RESET)

# =========================
# REVERSE DNS
# =========================
def reverse_dns(ip):
    print(YELLOW + "\n[+] Reverse DNS\n" + RESET)

    try:
        print(GREEN + str(socket.gethostbyaddr(ip)) + RESET)
    except:
        print(RED + "Lookup failed" + RESET)

# =========================
# BANNER GRAB
# =========================
def banner_grab(host, port):
    print(YELLOW + "\n[+] Banner Grab\n" + RESET)

    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((host, int(port)))

        try:
            print(GREEN + s.recv(1024).decode().strip() + RESET)
        except:
            print(RED + "No banner" + RESET)

        s.close()
    except Exception as e:
        print(RED + str(e) + RESET)

# =========================
# ZERORATED CHECK
# =========================
def zerorated(country):
    print(YELLOW + "\n[+] Zerorated Finder\n" + RESET)

    data = {
        "zw": ["facebook.com", "whatsapp.com"],
        "za": ["google.com"],
        "ng": ["freebasics.com"]
    }

    if country not in data:
        print(RED + "Country not supported" + RESET)
        return

    for site in data[country]:
        try:
            requests.get("http://" + site, timeout=5)
            print(GREEN + "[ACCESSIBLE] " + site + RESET)
        except:
            print(RED + "[BLOCKED] " + site + RESET)

# =========================
# CONTACT
# =========================
def contact():
    print(GREEN + """
CONTACT

MRZEROEXPLOIT × PAYEOBOI ZW
Email: mrzeroexploitzw@gmail.com
WhatsApp:
https://whatsapp.com/channel/0029VbCmxM69Bb5z0HwOsw0f
""" + RESET)

# =========================
# MENU
# =========================
def menu():
    banner()

    print("""
1. Subdomain Scan
2. Alive Hosts
3. DNS Lookup
4. Port Scan
5. SSL Check
6. Header Intelligence
7. IP Info
8. Reverse DNS
9. Banner Grab
10. Zerorated Finder
11. Contact Developer
12. Exit
""")

    choice = input("Select: ").strip().lower()

    if choice == "1":
        subdomain_scan(input("Domain: "))
    elif choice == "2":
        alive_hosts(input("Domain: "))
    elif choice == "3":
        dns_lookup(input("Domain: "))
    elif choice == "4":
        port_scan(input("Host: "))
    elif choice == "5":
        ssl_checker(input("Domain: "))
    elif choice == "6":
        header_intel(input("Domain: "))
    elif choice == "7":
        ip_info(input("IP: "))
    elif choice == "8":
        reverse_dns(input("IP: "))
    elif choice == "9":
        banner_grab(input("Host: "), input("Port: "))
    elif choice == "10":
        zerorated(input("Country code: "))
    elif choice == "11":
        contact()
    elif choice == "12" or choice == "exit":
        sys.exit()
    else:
        print(RED + "Invalid option" + RESET)

    input("\nPress Enter...")

# =========================
# RUN
# =========================
try:
    while True:
        menu()
except KeyboardInterrupt:
    print("\nExiting...")
