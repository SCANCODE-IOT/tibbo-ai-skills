# Linux-платы Tibbo: LTPP3(G2) и LTPP3

Читай, когда пользователь называет LTPP3(G2), LTPP3, LTPB3 или «Tibbo на Linux». Это **не TiOS**: правила, API и
инструменты остальных справочников (tios-api.md, tibbo_build.py, tibbo_new.py, tibbo_device.py) к ним не относятся.
Каждое утверждение ниже взято со страницы docs.tibbo.com / tibbo.com (ссылка в скобках) или проверено запуском.

## 1. Что применимо из скилла, а что нет

| Задача | LTPP3(G2) |
|---|---|
| Подбор Tibbit-ов, совместимость соседей, питание модулей | **Да**: tibbits.md, tibbit-selection.md, power.md. Плата есть в `data/boards.json`, `tps_check.py` проверяет конфигурацию (слоты, UART, тайлы). |
| Какие линии у какого слота | **Да**: таблица в §3. |
| Прошивка на Tibbo BASIC / Tibbo C, AppBlocks | **Нет.** На плате Linux; программы - обычные приложения Linux (Python, C/C++, Node.js и т.д.). AppBlocks для неё проектов не собирает (среды исполнения AppBlocks: TiOS, Zephyr, MicroPython). |
| Сборка `tibbo_build.py`, загрузка `tibbo_device.py`, TIDE | **Нет.** Это инструменты TiOS-устройств. Программу на LTPP3(G2) переносят по SSH и запускают как службу Linux. |

Про Tibbo BASIC на Linux честно: на docs.tibbo.com есть раздел «Development (Linux)» о переносе приложений Tibbo
BASIC/C на Ubuntu-дистрибутив LTPP3(G2) (docs.tibbo.com/linux, linux_ref), но руководство там - заготовка от марта
2023 без шагов сборки и запуска. Платформы `LTPP3` и `LKLM601` из TIDE компилятор Tibbo на Node.js не собирает
(проверено: «undeclared identifier 'pl_ssi_baud'» даже на пустом проекте). Вывод для пользователя: под LTPP3(G2)
пиши приложение Linux; нужен именно Tibbo BASIC - бери TiOS-плату (TPP2/TPP3) или спроси Tibbo.

## 2. Плата LTPP3(G2) (docs.tibbo.com/ltpp3g2)

- Процессор Plus1 (SP7021): 4 ядра Cortex-A7, 1 ГГц; 512 МБ DDR3; eMMC 4 ГБ (ревизии -01, -02) или 8 ГБ (-03);
  слот microSD; EEPROM 2048 байт; RTC с суперконденсатором.
- 2 порта Ethernet 10/100 со встроенным коммутатором (цепочкой или независимо), HDMI, 2 USB 2.0 Type-A,
  консоль через USB Type-C. Wi-Fi/Bluetooth - дополнительный модуль WM6256; LTE - Tibbit #45.
- 4 тайла: 8 слотов «M» и 8 слотов «C», 32 линии ввода-вывода. UART - 4 слота, прерывания - 8, SPI/I2C - 4 одновременно.
- **Питание: 8-60 В на любой из двух разъёмов (одновременно использовать только один), встроенный источник 2,5 А -
  Tibbit-ы питания (#09, #10, #12, #23, #33 ...) не нужны.** Потребление самой платы - 400 мА при 12 В (оба Ethernet).
- Корпус - LTPB3. Рабочая температура -40…+85 °C.
- LTPP3 первого поколения - другая плата (TI Sitara Cortex-A8, 512 МБ NAND, 7 тайлов, дистрибутив линии Red Hat,
  LTiOS и Node.js; docs.tibbo.com/ltpp3). Не путай: образы, слоты и инструменты у поколений разные.

## 3. Слоты и линии LTPP3(G2) (docs.tibbo.com/ltpp3g2_tiles_sockets, ltpp3g2_platform_pl_io_num)

Слоты «M»: S1, S3, S5, S7, S9, S11, S13, S15; парные «C»: S2 … S16. Тайл = два слота M и два C подряд (S1-S4,
S5-S8, S9-S12, S13-S16). UART - только S1, S5, S9, S13. Прерывания и SPI/I2C - любой слот «M» (через PinMux).

| Слот M | A | B | C | D | UART |
|---|---|---|---|---|---|
| S1 | 9 | 8 | 0 | 16 | да |
| S3 | 32 | 33 | 4 | 20 | - |
| S5 | 11 | 10 | 1 | 17 | да |
| S7 | 34 | 35 | 5 | 21 | - |
| S9 | 13 | 12 | 2 | 18 | да |
| S11 | 36 | 37 | 6 | 22 | - |
| S13 | 15 | 14 | 3 | 19 | да |
| S15 | 38 | 39 | 7 | 23 | - |

Числа - номера `PL_IO_NUM_n` (24-31 зарезервированы). Линии однонаправленные: перед работой каждую настраивают как
вход или как выход. Раскладка совпадает с первыми 16 слотами TPP3, поэтому правила установки Tibbit-ов те же.

## 4. Системы и вход (docs.tibbo.com/ltpp3g2_getting_started, ltpp3g2_ssh, ltpp3g2_firmware)

- Образы: заводской на Yocto (Tibbo советует сразу обновить), **Ubuntu-дистрибутив Tibbo** (с репозиторием пакетов
  PPA и сценариями первого запуска), слои Yocto и Buildroot для своих сборок.
- Вход по умолчанию: Ubuntu - `ubuntu`/`ubuntu` и `root`/`root`; Yocto - `root`/`123`. **Сразу смени пароли** (так
  требует и Tibbo). SSH включён в Ubuntu и Yocto (порт 22); в Buildroot его включают вручную.
- Консоль: USB Type-C на плате (в корпусе LTPB3 - под верхней крышкой), 115200 бод, 8N1. IP-адрес - `ip addr show`.
- Обновление системы: файл образа с точным именем `ISPBOOOT.BIN` на флешку FAT32 (перемычка CN11) или на microSD
  (перемычки CN10 и CN11); выключенную плату включить и ждать в консоли «ISP all: Done»; затем выключить, снять
  перемычки и носитель. Образ Ubuntu: tibbo.com/downloads/open/ubuntu/ISPBOOOT.BIN. Обновление стирает систему на
  eMMC - сначала сохрани свои данные.

## 5. Ubuntu-дистрибутив: с чего начать (tibbo.com/store/tps/ltpp3g2/ubuntu-start.html)

- Обновить пакеты: `sudo apt-get update && sudo apt-get upgrade`, после обновления пакетов Tibbo - `sudo reboot`.
- Сценарии Tibbo: `sudo tb_wlan_mainmenu` (Wi-Fi: драйвер, поиск и подключение к сети; нужен модуль WM6256),
  `sudo tb_bt_mainmenu` (Bluetooth), `sudo tb_daisy_chain_onoff` (два порта Ethernet цепочкой или раздельно).
- **PinMux** - особенность процессора Plus1: UART, I2C, SPI и прерывания назначаются на линии слотов на лету, без
  перезагрузки. В PPA есть обёртка для Python и примеры: `hello_serial.py` (эхо по UART, `pip3 install pyserial`),
  `test_tbt36.py` (I2C, Tibbit #36, `pip3 install smbus2`), `poll_bp.py` (RS-485/Modbus, `pip3 install pyserial pymodbus`).
- Прерывания: линию назначают как источник фронта и слушают `gpiomon`; только фронт или спад, не больше восьми сразу.
- Разработка: VS Code с расширением Remote - SSH (`ssh ubuntu@<IP>`), код и отладка прямо на плате.
- Пошаговые уроки Tibbo (GPIO и светодиод, I2C и PinMux в Python, включение SPI): support.tibbo.com, раздел LTPP3(G2).
- Исходники: github.com/tibbotech - `plus1_kernel`, `LTPP3_ROOTFS`, `ltpp3g2_ppa`, `yocto_layers`, `br2_external`.

## 6. Как отвечать пользователю

1. Уточни поколение (LTPP3(G2) или LTPP3) и систему (Ubuntu Tibbo, Yocto, своя сборка) - от этого зависят шаги.
2. Железо (какие Tibbit-ы, куда, хватит ли питания) собирай как для TPS: `tps_check.py` с платой `LTPP3(G2)`.
   Tibbit-ы питания не добавляй - на плате свой источник.
3. Программу предлагай как приложение Linux на языке пользователя (чаще Python): доступ к UART/I2C/SPI/GPIO - через
   PinMux и стандартные средства Linux; запуск - служба systemd. Точные имена функций обёртки PinMux бери из примеров
   в PPA на самой плате, а не выдумывай: в документации Tibbo они не перечислены.
4. Не предлагай TIDE, Tibbo BASIC, AppBlocks и скрипты сборки/загрузки этого скилла для LTPP3(G2).
5. Чего нет на страницах Tibbo - так и скажи и дай ссылку: docs.tibbo.com/ltpp3g2, support.tibbo.com.
