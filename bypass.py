import os
import requests
import sys
import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm
import subprocess
import shutil


# Lädt automatisiert den "Tor Browser" herunter
def download_tor():     
    url = 'https://www.torproject.org/de/download/' 
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    download_button = soup.find('a', class_='btn btn-primary mt-4 downloadLink', string="Herunterladen fÃ¼r Windows")

    file_name = "tor-browser-windows-installer.exe"
    current_directory = os.getcwd()
    tor_folder = os.path.join(current_directory, "Tor-Browser")

    if download_button:
        download_link = download_button.get('href')
        print(f"Gefundener Download-Link: {download_link}")

        base_url = 'https://www.torproject.org/'
        full_download_url = base_url + download_link
        file_response = requests.get(full_download_url)

        with open(file_name, 'wb') as f:
            f.write(file_response.content)
        print(f"Die Datei wurde als {file_name} gespeichert.")

        try:
            subprocess.run([file_name, '/S', f'/D={tor_folder}'], check=True)
            print(f"{file_name} wurde jetzt ohne Benutzerinteraktion installiert.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen des Installers: {e}")
    else:
        print("Download-Button mit dem Text 'Herunterladen für Windows' nicht gefunden.")

    tor = os.path.join(current_directory, file_name)
    os.remove(tor)

# Lässt dich einen Command ausführen auch ohne die CMD
def command_exec():
    command = input("Gib deinen Befehl ein: ")
    while True:
        question = input("Ist die Eingabeaufforderung verfügbar? (Default ist JA) (Y|N) ").lower()
        if question == "y":
            subprocess.run(command, check=True, shell=True)
            break
        elif question == "n":
            subprocess.run(command, check=True)
            break
        else:
            print("Diese Eingabe ist nicht korrekt!")
    
# Benutzt statt die angegebenen Admin-Rechte deine eigenen User-Rechte
def admin_bypass():
    print("WARNUNG! Diese Methode benutzt nur die User-Rechte statt die Admin-Rechte! \nAlso könnte es gut sein dass die Datei Fehler aufweist beim ausführen!")
    pfad_text = input("Gib den Pfad zur Datei an: ")
    command = f'set __COMPAT_LAYER=RUNASINVOKER && start "" "{pfad_text}"'
    subprocess.run(command, check=True, shell=True)

# Versucht in einer Schleife im Hintergrund den Watch Prozess zu töten (Wird noch implementiert) TODO
def kill_watch_process():
    print("WARNUNG!!! Für diese Aktion wird keine Haftung übernommen!")
    print("Hier werden alle Watch Prozesse gekillt!")
    while True:
        question = input("Bist du dir sicher? (Y|N) ").lower()
        if question == "y":
            break
        elif question == "n":
            quit()
            break
        else:
            print("Diese Eingabe ist nicht korrekt!")
    print('Drücke "strg + c" um es zu beenden! (Running...)')
    while True:
        os.system("taskkill /f /im notepad.exe >nul 2>&1")

# Lädt die Dependencies von Winget herunter
def get_dependencies_winget():
    winget_github = "https://api.github.com/repos/microsoft/winget-cli/releases/latest"

    response = requests.get(winget_github)
    release_data = response.json()

    zip_url = None
    for asset in release_data["assets"]:
        if asset["name"].endswith("Dependencies.zip"):
            zip_url = asset["browser_download_url"]
            break

    if not zip_url:
        raise Exception("Keine passende ZIP-Datei gefunden!")
    
    zip_path = os.path.join(os.getcwd(), "Winget-Dependencies.zip")

    try:
        response = requests.get(zip_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='B', unit_scale=True)
        with open(zip_path, 'wb') as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
    except Exception as e:
        print(f"Fehler beim Herunterladen: {e}")
        sys.exit(1)

    extract_dir = os.path.splitext(zip_path)[0]
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    x64_dir = os.path.join(extract_dir, "x64")

    if os.path.exists(x64_dir) and os.path.isdir(x64_dir):
        file_paths = [os.path.join(x64_dir, file) for file in os.listdir(x64_dir)]
    else:
        file_paths = []
    
    for package in file_paths:
        os.system(f"powershell Add-AppxPackage {package}")
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    

# Installiert automatisiert am PC "Winget" (Wird noch implementiert) TODO
def install_winget():
    try:
        subprocess.run(["winget", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Winget ist bereits installiert.")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Winget ist nicht installiert. Installation wird gestartet...")
    
    get_dependencies_winget()
    winget_url = "https://aka.ms/getwinget"
    installer_path = os.path.join(os.getcwd(), "Microsoft.DesktopAppInstaller.msixbundle")
    
    try:
        response = requests.get(winget_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='B', unit_scale=True)
        with open(installer_path, 'wb') as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
    except Exception as e:
        print(f"Fehler beim Herunterladen: {e}")
        if os.path.exists(installer_path):  
            os.remove(installer_path)
        sys.exit(1)
    
    os.system(f"powershell Add-AppxPackage {installer_path}")
    print("Installation abgeschlossen. Bitte prüfen Sie, ob winget nun funktioniert.")
    if os.path.exists(installer_path):  
        os.remove(installer_path)

# Der direkt ausführende Part 
print("Willkommen zu Tobis Ultimatives Bypass Tool!")
while True:
    print("(1) Tor-Installation")
    print("(2) Command-Ausführer")
    print("(3) Admin-Bypass")
    print("(4) Watch-Process-Killer")
    print("(5) Winget-Installation")
    answer = input("Wähle deine Aktion mit den Nummern oben angezeigt!: ")
    if answer == "1":
        download_tor()
        break
    elif answer == "2":
        command_exec()
        break
    elif answer == "3":
        admin_bypass()
        break
    elif answer == "4":
        kill_watch_process()
        break
    elif answer == "5":
        install_winget()
        break
    else:
        print("Diese Eingabe ist keine Nummer von oben!")