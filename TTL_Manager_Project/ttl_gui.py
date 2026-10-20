import os
import sys
import ctypes
import sqlite3
import subprocess
import re
import threading
from datetime import datetime
import customtkinter as ctk

# Флаг для скрытия черных всплывающих окон консоли в Windows
CREATE_NO_WINDOW = 0x08000000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_DIR, "network_history.db")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
    )
    sys.exit()

class TTLModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTL Control & Diagnostics")
        self.geometry("920x540")
        self.minsize(860, 500)

        self.init_database()
        self.setup_ui()
        self.refresh_system_status()

    def init_database(self):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network_name TEXT NOT NULL,
                ttl_value INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def log_to_db(self, net_name, ttl):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO history (network_name, ttl_value, timestamp) VALUES (?, ?, ?)",
                    (net_name, ttl, now))
        conn.commit()
        conn.close()

    def write_console(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def setup_ui(self):
        self.top_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1f2430")
        self.top_frame.pack(fill="x", padx=14, pady=(12, 8))

        self.lbl_net = ctk.CTkLabel(
            self.top_frame, text="Сеть: Определение...", font=("Segoe UI", 14, "bold"), text_color="#38bdf8"
        )
        self.lbl_net.pack(side="left", padx=16, pady=10)

        self.lbl_ttl = ctk.CTkLabel(
            self.top_frame, text="Hop Limit: --", font=("Segoe UI", 13), text_color="#94a3b8"
        )
        self.lbl_ttl.pack(side="right", padx=16, pady=10)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # Левая панель: TTL
        self.left_card = ctk.CTkFrame(self.main_container, width=280, corner_radius=12, fg_color="#181a20")
        self.left_card.pack(side="left", fill="y", padx=(0, 10))

        lbl_left_title = ctk.CTkLabel(self.left_card, text="Управление TTL", font=("Segoe UI", 16, "bold"))
        lbl_left_title.pack(pady=(16, 12), padx=16, anchor="w")

        self.btn_65 = ctk.CTkButton(
            self.left_card, text="TTL 65 (Обход раздачи)", font=("Segoe UI", 12, "bold"),
            fg_color="#8b5cf6", hover_color="#7c3aed", height=38,
            command=lambda: self.apply_ttl_async(65)
        )
        self.btn_65.pack(fill="x", padx=16, pady=6)

        self.btn_64 = ctk.CTkButton(
            self.left_card, text="TTL 64 (Модемы / Роутеры)", font=("Segoe UI", 12),
            fg_color="#334155", hover_color="#475569", height=38,
            command=lambda: self.apply_ttl_async(64)
        )
        self.btn_64.pack(fill="x", padx=16, pady=6)

        self.btn_128 = ctk.CTkButton(
            self.left_card, text="TTL 128 (Windows стандарт)", font=("Segoe UI", 12),
            fg_color="#1e293b", hover_color="#334155", height=38,
            command=lambda: self.apply_ttl_async(128)
        )
        self.btn_128.pack(fill="x", padx=16, pady=6)

        self.sep = ctk.CTkFrame(self.left_card, height=2, fg_color="#262b36")
        self.sep.pack(fill="x", padx=16, pady=16)

        lbl_custom = ctk.CTkLabel(self.left_card, text="Кастомный TTL (1-255):", font=("Segoe UI", 12), text_color="#94a3b8")
        lbl_custom.pack(anchor="w", padx=16, pady=(0, 4))

        self.custom_box = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.custom_box.pack(fill="x", padx=16, pady=4)

        self.entry_ttl = ctk.CTkEntry(self.custom_box, width=70, font=("Consolas", 14), justify="center")
        self.entry_ttl.pack(side="left", padx=(0, 8))
        self.entry_ttl.insert(0, "65")

        self.btn_custom = ctk.CTkButton(
            self.custom_box, text="Задать", font=("Segoe UI", 12, "bold"),
            fg_color="#10b981", hover_color="#059669", text_color="#ffffff",
            command=self.apply_custom_ttl
        )
        self.btn_custom.pack(side="left", fill="x", expand=True)

        # Правая панель: Тесты + Консоль
        self.right_card = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color="#181a20")
        self.right_card.pack(side="right", fill="both", expand=True)

        self.test_bar = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.test_bar.pack(fill="x", padx=14, pady=12)

        self.btn_ping_local = ctk.CTkButton(
            self.test_bar, text="Ping 127.0.0.1", font=("Segoe UI", 11, "bold"),
            fg_color="#0284c7", hover_color="#0369a1", width=120, height=32,
            command=lambda: self.run_test_async(["ping", "-n", "1", "127.0.0.1"])
        )
        self.btn_ping_local.pack(side="left", padx=(0, 6))

        self.btn_ping_ext = ctk.CTkButton(
            self.test_bar, text="Ping 8.8.8.8", font=("Segoe UI", 11, "bold"),
            fg_color="#0ea5e9", hover_color="#0284c7", width=120, height=32,
            command=lambda: self.run_test_async(["ping", "-n", "2", "8.8.8.8"])
        )
        self.btn_ping_ext.pack(side="left", padx=6)

        self.btn_history = ctk.CTkButton(
            self.test_bar, text="История сетей", font=("Segoe UI", 11),
            fg_color="#475569", hover_color="#334155", width=110, height=32,
            command=self.show_db_history
        )
        self.btn_history.pack(side="left", padx=6)

        self.btn_clear = ctk.CTkButton(
            self.test_bar, text="Очистить", font=("Segoe UI", 11),
            fg_color="#e11d48", hover_color="#be123c", width=90, height=32,
            command=self.clear_console
        )
        self.btn_clear.pack(side="right")

        self.console = ctk.CTkTextbox(
            self.right_card, font=("Consolas", 12), text_color="#cbd5e1",
            fg_color="#0b0d11", corner_radius=8
        )
        self.console.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.console.configure(state="disabled")

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def get_current_network(self):
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                stderr=subprocess.DEVNULL,
                encoding="oem",
                creationflags=CREATE_NO_WINDOW
            )
            match = re.search(r"^\s*SSID\s*:\s*(.+)$", out, re.MULTILINE)
            if match:
                return f"Wi-Fi: {match.group(1).strip()}"
        except Exception:
            pass

        try:
            out = subprocess.check_output(
                ["route", "print", "0.0.0.0"],
                stderr=subprocess.DEVNULL,
                encoding="oem",
                creationflags=CREATE_NO_WINDOW
            )
            for line in out.splitlines():
                if "0.0.0.0" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        return f"Ethernet/LAN (IP: {parts[3]})"
        except Exception:
            pass

        return "Интерфейс не определен"

    def get_system_ttl(self):
        try:
            out = subprocess.check_output(
                ["netsh", "int", "ipv4", "show", "glob"],
                stderr=subprocess.DEVNULL,
                encoding="oem",
                creationflags=CREATE_NO_WINDOW
            )
            match = re.search(r":\s*(\d+)", out)
            if match:
                return match.group(1)
        except Exception:
            pass
        return "--"

    def refresh_system_status(self):
        net = self.get_current_network()
        ttl = self.get_system_ttl()
        self.lbl_net.configure(text=f"Сеть: {net}")
        self.lbl_ttl.configure(text=f"Системный Hop Limit: {ttl}")
        self.write_console(f"[*] Система запущена. Подключение: {net}")
        self.write_console(f"[*] Текущий лимит в сетевом стеке: {ttl} (без изменений)")

    def apply_custom_ttl(self):
        val = self.entry_ttl.get().strip()
        if not val.isdigit() or not (1 <= int(val) <= 255):
            self.write_console("[-] Ошибка: введите число в диапазоне от 1 до 255.")
            return
        self.apply_ttl_async(int(val))

    def apply_ttl_async(self, val):
        threading.Thread(target=self._apply_ttl_worker, args=(val,), daemon=True).start()

    def _apply_ttl_worker(self, val):
        self.write_console(f"\n[>] Применение TTL = {val} без перезагрузки...")
        try:
            # Вызовы без появления окон
            subprocess.run(
                ["netsh", "int", "ipv4", "set", "glob", f"defaultcurhoplimit={val}"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
            subprocess.run(
                ["netsh", "int", "ipv6", "set", "glob", f"defaultcurhoplimit={val}"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )

            reg_args = [
                "reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters",
                "/v", "DefaultTTL", "/t", "REG_DWORD", "/d", str(val), "/f"
            ]
            subprocess.run(
                reg_args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )

            net = self.get_current_network()
            self.log_to_db(net, val)

            self.after(0, lambda: self.lbl_ttl.configure(text=f"Системный Hop Limit: {val}"))
            self.write_console(f"[+] Успешно! Системный TTL переключен на {val}")
            self.write_console(f"[+] Сеть зарегистрирована в базе: {net}")
        except Exception as e:
            self.write_console(f"[-] Ошибка применения: {e}")

    def run_test_async(self, cmd_list):
        threading.Thread(target=self._test_worker, args=(cmd_list,), daemon=True).start()

    def _test_worker(self, cmd_list):
        target = " ".join(cmd_list)
        self.write_console(f"\n[>] Запуск теста: {target}")
        try:
            out = subprocess.check_output(
                cmd_list,
                stderr=subprocess.STDOUT,
                encoding="oem",
                creationflags=CREATE_NO_WINDOW
            )
            self.write_console(out.strip())
            match = re.search(r"TTL=(\d+)", out, re.IGNORECASE)
            if match:
                self.write_console(f"[i] Ответный пакет зафиксировал TTL: {match.group(1)}")
        except Exception as e:
            self.write_console(f"[-] Ошибка выполнения: {e}")

    def show_db_history(self):
        self.write_console("\n--- История из SQLite ---")
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT network_name, ttl_value, timestamp FROM history ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                self.write_console("База данных пуста.")
                return

            for name, ttl, date in rows:
                self.write_console(f"[{date}] {name} -> TTL: {ttl}")
        except Exception as e:
            self.write_console(f"[-] Ошибка чтения БД: {e}")

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()

    app = TTLModernApp()
    app.mainloop()