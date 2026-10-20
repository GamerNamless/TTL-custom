<div align="center">

# ⚡ TTL-custom

**Легковесная утилита с современным темным интерфейсом на CustomTkinter для мгновенного изменения значения TTL в Windows без перезагрузки системы.**

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?logo=windows&logoColor=white)](#)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Silent Mode: Supported](https://img.shields.io/badge/Console-Silent%20Mode-brightgreen)](#)

<p align="center">
  <a href="#-документация-на-русском"><b>Русская версия</b></a> •
  <a href="#-english-documentation"><b>English Version</b></a>
</p>

---

</div>

## 🇷🇺 Документация на русском

Утилита создана для быстрого обхода блокировок и тарифных ограничений мобильных операторов при раздаче интернета (тетеринге) со смартфона или модема на ПК под управлением Windows. Все изменения применяются моментально «на лету» без необходимости перезагружать систему.

---

### 📑 Оглавление
1. [Архитектура и как это работает](#-архитектура-и-как-это-работает)
2. [Ключевые возможности](#-ключевые-возможности)
3. [Быстрые пресеты TTL](#-быстрые-пресеты-ttl)
4. [Инструкция по использованию](#-инструкция-по-использованию)
5. [Часто задаваемые вопросы (FAQ)](#-часто-задаваемые-вопросы-faq)
6. [Сборка автономного EXE](#-сборка-автономного-exe)

---

### 🧠 Архитектура и как это работает

Стандартный метод смены TTL через реестр Windows (`HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\DefaultTTL`) требует обязательной перезагрузки ПК, так как ядро считывает этот параметр только при инициализации драйвера стека.

**TTL-custom** использует гибридный подход:
1. **Мгновенный отклик:** Команда `netsh int ipv4/ipv6 set glob defaultcurhoplimit=<val>` перенастраивает счетчик переходов (Hop Limit) прямо в памяти сетевого стека ядра Windows — новые исходящие пакеты сразу получают заданный TTL.
2. **Персистентность:** Значение параллельно дублируется в системный реестр, чтобы параметр оставался активным даже после выключения или перезагрузки компьютера.
3. **Безопасность по умолчанию:** При открытии программа **только опрашивает** сетевые интерфейсы и не переписывает значения в системе, пока пользователь не нажмет кнопку применения.
4. **Тихий режим (No Flicker):** Все вызовы подсистем Windows (`netsh`, `ping`, `route`, `reg`) изолированы системным флагом `CREATE_NO_WINDOW`, благодаря чему на экране не мерцают черные окна командной строки.

---

### ✨ Ключевые возможности

* 🎨 **Современный UI:** Темная графическая оболочка на **CustomTkinter** со скругленными элементами и удобной компоновкой.
* 📶 **Автоопределение адаптера:** Скрипт автоматически распознает активную Wi-Fi сеть (SSID) или локальное проводное Ethernet-подключение с его IP.
* 🗄️ **Локальная база данных (SQLite):** Ведет историю применения параметров в файле `network_history.db` (название сети, значение TTL, дата и время).
* 🩺 **Встроенная экспресс-диагностика:** Пинг локального интерфейса (`127.0.0.1`) и публичного DNS (`8.8.8.8`) с парсингом фактического ответа TTL в окне консоли.

---

### 🎯 Быстрые пресеты TTL

| Значение | Тип | Назначение и принцип работы |
| :---: | :---: | :--- |
| **65** | Смартфон | **Обход раздачи со смартфона (Android / iOS).** Телефон при пересылке пакета с ПК уменьшает TTL на 1 ($65 - 1 = 64$). Вышка оператора видит исходящий трафик со стандартным значением 64, характерным для самого смартфона. |
| **64** | Модемы | **Модемы, роутеры и Linux-устройства.** Используется, если входящий шлюз не декрементирует TTL или для прямого подключения через настроенные роутеры. |
| **128** | Стандарт | **Заводской стандарт Windows.** Возвращает параметры сетевого стека по умолчанию. |
| **1-255** | Кастом | **Пользовательское значение.** Позволяет задать любой произвольный лимит переходов. |

---

### 🚀 Инструкция по использованию

1. Скачайте релизный файл `TTL_Manager.exe` (или запустите исходный код `ttl_gui.py`).
2. Запустите приложение с правами Администратора (при обычном клике Windows сама отобразит запрос UAC).
3. **Левая часть окна (Управление):**
   * Нажмите нужную кнопку быстрого пресета (**65**, **64**, **128**).
   * Либо введите свое число в поле «Кастомный TTL» и нажмите кнопку **«Задать»**.
4. **Правая часть окна (Диагностика):**
   * Нажмите **Ping 127.0.0.1** для тестирования локального сетевого интерфейса.
   * Нажмите **Ping 8.8.8.8** для проверки внешнего маршрута и чтения поля TTL в ответных пакетах.
   * Нажмите **История сетей**, чтобы просмотреть сохраненные профили из SQLite.

---

### ❓ Часто задаваемые вопросы (FAQ)

<details>
<summary><b>Зачем программе требуются права Администратора?</b></summary>

Прямая правка параметров сетевого стека через утилиту `netsh`, а также запись глобальных параметров протокола TCP/IP в системную ветку реестра `HKEY_LOCAL_MACHINE` строго ограничены политиками безопасности Windows и требуют повышенных привилегий.
</details>

<details>
<summary><b>Нужно ли держать программу постоянно открытой?</b></summary>

Нет. Как только вы нажали кнопку и в консоли появилось подтверждение об успешном изменении, сетевой стек уже перенастроен. Вы можете сразу закрыть приложение.
</details>

<details>
<summary><b>Почему антивирус или Windows SmartScreen могут ругаться на файл?</b></summary>

Это стандартное ложное срабатывание (False Positive) защитных систем на бинарники, собранные через PyInstaller без коммерческого цифрового сертификата разработчика. Исходный код скрипта полностью открыт и доступен для независимой проверки.
</details>

---

### 🛠️ Сборка автономного EXE

Для сборки единого `.exe` файла со всеми встроенными стилями и библиотеками:

```powershell
# 1. Клонирование репозитория
git clone https://github.com/GamerNamless/TTL-custom.git
cd TTL-custom

# 2. Установка зависимостей
python -m pip install --upgrade pip
python -m pip install customtkinter pyinstaller

# 3. Сборка (флаг --collect-all обязателен для customtkinter)
python -m PyInstaller --noconfirm --onefile --windowed --collect-all customtkinter --name "TTL_Manager" ttl_gui.py
```

Готовый файл будет находиться по пути: `dist/TTL_Manager.exe`.

<br>

---

## 🇬🇧 English Documentation

Open-source utility featuring a modern CustomTkinter dark GUI designed for instantaneous TTL (Time to Live / Hop Limit) adjustments on Windows without system restarts. Specifically crafted to bypass cellular carrier mobile hotspot (tethering) restrictions, run quick ICMP diagnostics, and track network profiles locally with SQLite.

---

### 📑 Table of Contents
1. [Architecture & How It Works](#-architecture--how-it-works)
2. [Key Features](#-key-features)
3. [TTL Presets Reference](#-ttl-presets-reference)
4. [User Guide](#-user-guide)
5. [Frequently Asked Questions (FAQ)](#-frequently-asked-questions-faq-en)
6. [Building from Source](#-building-from-source)
7. [License](#-license)

---

### 🧠 Architecture & How It Works

Modifying the Windows TTL through registry keys (`HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\DefaultTTL`) natively requires a system reboot before changes take effect.

**TTL-custom** resolves this limitation:
1. **Live Kernel Overrides:** Executes `netsh int ipv4/ipv6 set glob defaultcurhoplimit=<val>`, enforcing the new Hop Limit dynamically inside the active Windows network stack.
2. **Reboot Persistence:** Replicates values into the registry so customizations remain active after reboots.
3. **Passive Startup:** Only reads system information upon launching without tampering with system defaults until initiated by the user.
4. **Flicker-Free Operations:** Background procedures (`netsh`, `ping`, `route`, `reg`) utilize the Win32 `CREATE_NO_WINDOW` flag, preventing intrusive command prompt pop-ups.

---

### ✨ Key Features

* 🎨 **Refined GUI:** Fully responsive dark-themed interface built using **CustomTkinter**.
* 📶 **Interface Auto-Detection:** Queries and displays current Wi-Fi SSIDs or active Ethernet LAN adapters alongside local IP assignments.
* 🗄️ **Persistent SQLite History:** Automatically logs past network transitions to `network_history.db`.
* 🩺 **Real-Time ICMP Tests:** Built-in loopback (`127.0.0.1`) and external DNS (`8.8.8.8`) ping testers reporting TTL values directly to the integrated console.

---

### 🎯 TTL Presets Reference

| Value | Target | Explanation |
| :---: | :---: | :--- |
| **65** | Smartphone | **Mobile Hotspot Bypass (Android / iOS).** The phone acts as a router, decrementing the packet TTL by 1 ($65 - 1 = 64$). The carrier antenna receives incoming traffic with a TTL of 64, matching native phone packets. |
| **64** | Modems | **Cellular modems, Linux routers, and Android units.** Ideal when the intermediary bridge does not decrement hop limits. |
| **128** | Standard | **Default Windows TCP/IP limit.** Reverts adjustments back to native OS standards. |
| **1-255** | Custom | **User-Defined Value.** Allows precise configuration within standard IP packet boundaries. |

---

### 🚀 User Guide

1. Download the latest `TTL_Manager.exe` release or execute `ttl_gui.py` from source.
2. Launch with Administrator rights (UAC elevation will trigger automatically if started normally).
3. **Left Control Card:**
   * Select a quick preset button (**65**, **64**, **128**).
   * Or input any number (1-255) into the "Custom TTL" entry field and hit **«Задать»** (Apply).
4. **Right Diagnostic Card:**
   * Run **Ping 127.0.0.1** to test loopback responsiveness.
   * Run **Ping 8.8.8.8** to evaluate outgoing routes and inspect response packet headers.
   * Click **История сетей** (History) to display the recent SQLite entries.

---

### <a id="-frequently-asked-questions-faq-en"></a>❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>Why does the program require Administrator privileges?</b></summary>

Direct modification of kernel network stack parameters via `netsh` and writing TCP/IP parameters to `HKEY_LOCAL_MACHINE` are strictly protected Windows operations requiring elevated user privileges.
</details>

<details>
<summary><b>Do I need to keep the application running in the background?</b></summary>

No. As soon as you click the button and the console outputs confirmation, the network stack has been updated. You can safely close the application.
</details>

<details>
<summary><b>Why do antivirus tools or Windows SmartScreen flag the executable?</b></summary>

This is a typical false-positive alert triggered by PyInstaller executables lacking an expensive commercial code-signing certificate. The project source code is fully open and available for auditing.
</details>

---

### 🛠️ Building from Source

To compile a standalone, single-file binary with all dependencies bundled:

```powershell
# 1. Clone the repository
git clone https://github.com/GamerNamless/TTL-custom.git
cd TTL-custom

# 2. Install dependencies
python -m pip install --upgrade pip
python -m pip install customtkinter pyinstaller

# 3. Build standalone binary
python -m PyInstaller --noconfirm --onefile --windowed --collect-all customtkinter --name "TTL_Manager" ttl_gui.py
```

The compiled standalone binary will be located in the `dist/TTL_Manager.exe` directory.

---

### 📄 License

Distributed under the [MIT](LICENSE) License.
