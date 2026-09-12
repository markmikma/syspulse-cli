def parse_log_file(file_path):
    error_count = 0
    warning_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if "ERROR" in line:
                    error_count += 1
                elif "WARNING" in line:
                    warning_count += 1

        print(f"=== Log Elemzés Eredmény ({file_path}) ===")
        print(f"Talált hibák (ERROR): {error_count}")
        print(f"Talált figyelmeztetések (WARNING): {warning_count}")

    except FileNotFoundError:
        print(f"Hiba: A {file_path} fájl nem található!")

if __name__ == "__main__":
    parse_log_file("sample.log")