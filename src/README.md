# SysPulse-CLI 🚀

Egy könnyű súlyú, Python-alapú szerverfigyelő és logelemző parancssori eszköz (CLI), amely segít valós időben ellenőrizni a rendszererőforrásokat (CPU, RAM, Disk) és elemezni a kritikus rendszerlogokat.

## Funkciók
- **Rendszerfigyelés (`monitor.py`)**: Valós időben lekérdezi a CPU terhelést, a fizikai memória (RAM) státuszát és a lemezhasználatot a `psutil` könyvtár segítségével.
- **Logelemzés (`parser.py`)**: Átvizsgálja a szöveges logfájlokat, és összesíti a bennük található `ERROR` és `WARNING` üzeneteket.
- **Konténerizáció (Docker)**: Teljes mértékben futtatható izolált Docker konténerben is.

## Telepítés és futtatás (Lokálisan)

1. Klónozd a repót:
   ```bash
   git clone [https://github.com/markmikma/syspulse-cli.git](https://github.com/markmikma/syspulse-cli.git)
   cd syspulse-cli
2. 
 Hozz létre egy virtuális környezetet és aktiváld:
 Bash
 python -m venv venv
 venv\Scripts\Activate
3. Telepítsd a függőségeket:

 Bash
 pip install -r requirements.txt
4. Futtasd a monitorozást:

 Bash
 python src/monitor.py
5. Futtatás Dockerrel
 Bash
 docker build -t syspulse-cli .
 docker run --rm syspulse-cli