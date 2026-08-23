import psutil

def check_system():
    print("=== SysPulse-CLI Rendszerfigyelő ===")
    
    # CPU terhelés
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Terhelés: {cpu_percent}%")
    
    # Memória (RAM) adatok
    memory = psutil.virtual_memory()
    total_ram_gb = memory.total / (1024 ** 3)
    used_ram_gb = memory.used / (1024 ** 3)
    print(f"RAM Összesen: {total_ram_gb:.2f} GB")
    print(f"RAM Használt: {memory.percent}% ({used_ram_gb:.2f} GB)")
    
    # Lemez (Disk) adatok
    disk = psutil.disk_usage('/')
    total_disk_gb = disk.total / (1024 ** 3)
    print(f"Lemez Összesen: {total_disk_gb:.2f} GB")
    print(f"Lemez Használt: {disk.percent}%")

if __name__ == "__main__":
    check_system()