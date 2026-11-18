# Tibbit modules catalog (auto-extracted from github.com/tibbotech/TibbitDefinitions/tibbits.json)

Колонка Power — **потребление** Tibbit (или «supplies» — что он выдаёт). Правила питания и проверка бюджета: power.md и `scripts/tps_check.py`. Машиночитаемая версия с тегами, статусом и характеристиками источников: `data/tibbits.json`.

Form: size code from the catalog (M1S/M2S/M1/M2 etc.). Lines: TPS socket lines the Tibbit occupies (LN1..LN4 ↔ socket lines A..D; map them to PL_IO_NUM_* with the TPP2/TPP3 socket table in platforms.md). Mates: Tibbits usually paired with it. Requires: other Tibbits/conditions needed.

| Model | Name | Category | Form | Lines used | Mates | Requires | Power | For sale |
|---|---|---|---|---|---|---|---|---|
| 00_1 | Four direct I/O lines | empty | M1S | LN1,LN2,LN3,LN4 | 19,20,21,49 |  | 5V 20mA | yes |
| 00_2 | Three direct I/O lines and ground | empty | M1S | LN1,LN2,LN3,LN4 | 19,20,21 |  | 5V 20mA | yes |
| 00_3 | Two direct I/O lines, +5V power, ground | empty | M1S | LN1,LN2,3,4 | 19,20,21,28,29,30,35,36,38,39_1,39_2,39_3,39_4,41 |  | 5V 20mA | yes |
| 01 | Four-line RS232 port | io | M1S | TX,RX,RTS,CTS | 19,20,21 | serial,interrupt | 5V 20mA | yes |
| 02 | RS232/422/485 port | io | M2S | TX,RX,RTS,CTS,FD/-HD,-232/422&485,DTR,DSR | 19,20 | serial,interrupt | 5V 40mA | yes |
| 03_1 | Two low-power relays (configuration 1) | output | M1S | RL1,RL2,3,4 | 19,20,21 |  | 5V 60mA | yes |
| 03_2 | Two low-power relays (configuration 2) | output | M1S | RL1,RL2,3,4 | 19,20,21 |  | 5V 60mA | yes |
| 04_1 | Two isolated inputs | input | M1S | IN1,IN2,3,4 | 19,20,21 |  | 5V 30mA | yes |
| 04_2 | Three isolated inputs, common (-) | input | M1S | IN1,IN2,IN3,4 | 19,20,21 |  | 5V 35mA | yes |
| 04_3 | Three isolated inputs, common (+) | input | M1S | IN1,IN2,IN3,4 | 19,20,21 |  | 5V 35mA | yes |
| 04_4 | Four opto-inputs, common ground | input | M1S | IN1,IN2,IN3,IN4 | 19,20,21 |  | 5V 40mA | yes |
| 04_5 | Two 24V isolated inputs | input | M1S | IN1,IN2,3,4 | 19,20,21 |  | 5V 30mA | yes |
| 04_6 | Three 24V isolated inputs, common (-) | input | M1S | IN1,IN2,IN3,4 | 19,20,21 |  | 5V 35mA | yes |
| 04_7 | Three 24V isolated inputs, common (+) | input | M1S | IN1,IN2,IN3,4 | 19,20,21 |  | 5V 35mA | yes |
| 04_8 | Four 24V isolated inputs, common ground | input | M1S | IN1,IN2,IN3,IN4 | 19,20,21 |  | 5V 40mA | yes |
| 05 | RS485 port | io | M1S | TX,RX,DIR,4 | 19,20,21 | serial | 5V 15mA | yes |
| 06 | Two high-power relays | output | M2T | RL1,RL2,3,4,5,6,7,8 | 19,20,21 |  | 5V 140mA | yes |
| 07 | Two solid state relays | output | M1S | RL1,RL2,3,4 | 19,20,21 |  | 5V 25mA | yes |
| 08 | Wiegand and clock/data reader port | io | M1S | OUT,W1,CTRL,W0&1 | 19,20,21 | serial,interrupt | 5V 20mA | yes |
| 09 | Low-power 5V supply, 12V input | power | M1S | SDWN,2,3,4 | 18,19,20,21 |  | 5V 700mA (supplies) | yes |
| 10 | Medium-power 5V supply, 12V input | power | M1T | SDWN,2,3,4 | 18,19,20,21 |  | 5V 1100mA (supplies) | yes |
| 11 | Four open collector outputs | output | M1S | OUT1,OUT2,OUT3,OUT4 | 19,20,21 |  | 5V 50mA | yes |
| 12 | Low-power +15/-15V power supply, 5V input | power | M1S | SDWN,2,3,4 |  |  | 5V 230mA; +15V 15mA (supplies); -15V 15mA (supplies) | yes |
| 13 | Four-channel ADC | input | M1S | SCL,SDA,3,4 | 19,20,21 |  | 5V 10mA; +15V 9mA; -15V 4mA | yes |
| 14 | Four-channel DAC | output | M1S | SCL,SDA,LOAD,BUSY | 19,20,21 |  | 5V 20mA; +15V 4mA; -15V 4mA | yes |
| 15 | High-voltage AC solid state relay | output | H1 | RL1,2,3,4 |  |  | 5V 20mA | yes |
| 16 | Three PWMs with open collector outputs | output | M1S | SCL,SDA,RST,INT | 20,21,19 |  | 5V 20mA | yes |
| 17 | Three PWMs with power outputs | output | M1S | SCL,SDA,RST,INT | 20,21,19 |  | 5V 20mA | yes |
| 18 | Power input | connector | C1 |  | 09,10,25,33 |  |  | yes |
| 19 | DB9M connector | connector | C2 |  | 00_1,00_2,00_3,01,02,03_1,03_2,04_1,04_2,04_3,04_4,04_5,04_6,04_7,04_8,05,06,07,08,09,10,11,12,13,14,16,17,22,23,25,26,31,33,40_1,40_2,40_3,40_4,42,51,52,53,54,57,58,59 |  |  | yes |
| 20 | Nine terminal blocks | connector | C2 |  | 00_1,00_2,00_3,01,02,03_1,03_2,04_1,04_2,04_3,04_4,04_5,04_6,04_7,04_8,05,06,07,08,09,10,11,12,13,14,16,17,22,23,25,26,31,33,40_1,40_2,40_3,40_4,42,51,52,53,54,57,58,59 |  |  | yes |
| 21 | Four terminal blocks | connector | C1 |  | 00_1,00_2,00_3,01,03_1,03_2,04_1,04_2,04_3,04_4,04_5,04_6,04_7,04_8,05,06,07,08,09,10,11,13,14,16,17,22,23,25,26,31,33,40_1,40_2,40_3,40_4,42,51,53,54,57,58,59 |  |  | yes |
| 22 | RTD Temperature Meter | input | M1S | CSL,SDA,RST,INT | 19,20,21 | interrupt | 5V 10mA | yes |
| 23 | Isolated PoE power supply, 5V output | power | M2T | SDWN,2,3,4,5,6,7,8 | 19,20,21,37 |  | 5V 1300mA (supplies) | yes |
| 25 | High-power 5V supply, 12/24/48V input | power | M2T | SDWN,2,3,4,5,6,7,8 | 18,19,20,21 |  | 5V 1500mA (supplies) | yes |
| 26 | IR code processor | io | M1S | CS,SCLK,MOSI,DONE/MISO | 19,20,21,27 |  | 5V 100mA | yes |
| 27 | IR Receiver/Transmitter | connector | C1 |  | 26 |  | 5V 10mA | yes |
| 28 | Ambient light sensor | connector | C1 |  | 00_3 |  | 5V 2mA | yes |
| 29 | Ambient temperature meter | connector | C1 |  | 00_3 |  | 5V 2mA | yes |
| 30 | Temperature/humidity meter | connector | C1 |  | 00_3 |  | 5V 2mA | yes |
| 31 | PIC coprocessor | io | M1S | SCL,SDA,RST,INT | 19,20,21,12 |  | 5V 20mA | yes |
| 33 | Wide input range power supply | power | M1T | 5V,-SDWN,-PF | 18,19,20,21 |  | 5V 1500mA (supplies) | yes |
| 35 | Barometric pressure sensor | connector | C1 |  | 00_3 |  | 5V 2mA | yes |
| 36 | 3-axis accelerometer | connector | C1 |  | 00_3 |  | 5V 2mA | no |
| 37 | RF connector | connector | C1 |  | 12,23,42 |  |  | yes |
| 38 | Pushbutton | connector | C1 |  | 00_3 |  | 5V 1mA | yes |
| 39_1 | Large green LED (low brightness) | connector | C1 |  | 00_3 |  | 5V 30mA | yes |
| 39_2 | Large red LED (high brightness) | connector | C1 |  | 00_3 |  | 5V 30mA | yes |
| 39_3 | Large yellow LED (low brightness) | connector | C1 |  | 00_3 |  | 5V 30mA | yes |
| 39_4 | Large blue LED (high brightness) | connector | C1 |  | 00_3 |  | 5V 30mA | yes |
| 40_1 | Digital potentiometer, 5KOhm | io | M1S | SCL,SDA,3,4 | 19,20,21 |  | 5V 10mA | yes |
| 40_2 | Digital potentiometer, 10KOhm | io | M1S | SCL,SDA,3,4 | 19,20,21 |  | 5V 10mA | yes |
| 40_3 | Digital potentiometer, 50KOhm | io | M1S | SCL,SDA,3,4 | 19,20,21 |  | 5V 10mA | yes |
| 40_4 | Digital potentiometer, 100KOhm | io | M1S | SCL,SDA,3,4 | 19,20,21 |  | 5V 10mA | yes |
| 41 | 8-bit port (supplied with 200mm cable) | connector | C1 |  | 00_3 |  | 5V 40mA | yes |
| 42 | RTC and NVRAM with backup | io | M1S | CS,CLK,MOSI,MISO/-INT | 19,20,21,37 |  | 5V 10mA | yes |
| 43_1 | 4-Channel Streaming ADC ±10V | input | M1S | TX,RX,RTS,-MCLR | 19,20,21 | serial | 5V 20mA | yes |
| 43_2 | 4-Channel Streaming ADC ±100V | input | M1S | TX,RX,RTS,-MCLR | 19,20,21 | serial | 5V 20mA | yes |
| 44_1 | Isolated RS232/422/485 port | connector | H2 | TX,RX,RTS,CTS,FD/-HD,-232/422&485,DTR,DSR |  | serial,interrupt | 5V 80mA | yes |
| 44_2 | Isolated RS232/422/485 port | connector | H2 | TX,RX,RTS,CTS,FD/-HD,-232/422&485,DTR,DSR |  | serial,interrupt | 5V 80mA | yes |
| 45_1 | LTE (4G) Modem (SA) | io | H2 | TX,RX,RTS,CTS,-SDWN,PWRKEY,RESET,STATUS |  | serial,interrupt | 5V 500mA | yes |
| 45_2 | LTE (4G) Modem (E) | io | H2 | TX,RX,RTS,CTS,-SDWN,PWRKEY,RESET,STATUS |  | serial,interrupt | 5V 500mA | yes |
| 45_3 | LTE (4G) Modem (A) | io | H2 | TX,RX,RTS,CTS,-SDWN,PWRKEY,RESET,STATUS |  | serial,interrupt | 5V 500mA | yes |
| 46 | Cat-M1/NB-IoT Modem | io | H2 | TX,RX,RTS,CTS,-SDWN,PWRKEY,RESET,STATUS |  | serial,interrupt | 5V 300mA | yes |
| 47 | GPRS modem | io | H2 | TX,RX,RTS,CTS,-SDWN,PWRKEY,RESET,STATUS |  | serial | 5V 300mA | no |
| 48 | Audio In/Out | io | H2 | BCLK,WCLK,MCLK,RESET,I2C_SCL,I2C_SDA,DOUT,DIN |  |  | 5V 50mA | yes |
| 49 | Micro SD card slot | connector | C2 |  | 00_1 |  | 5V 10mA | yes |
| 50 | Mini type B USB port | connector | C1 |  |  |  | 5V 10mA | yes |
| 51 | CAN bus | io | M1S |  | 19,20,21 |  | 5V 60mA | no |
| 52 | Four-channel isolated +/-10V ADC | input | M2T | CSL,SDA,-RST,-INT,5,6,7,8 | 19,20 |  | 5V 100mA | yes |
| 53 | Isolated 4-20mA ADC | input | M2T | CSL,SDA,3,4,5,6,7,8 | 19,20,21 |  | 5V 100mA | yes |
| 54 | Four dry contact inputs | input | M1S | -IN1,-IN2,-IN3,-IN4 | 19,20,21 |  | 5V 40mA | yes |
| 56 | USB Type-A port | connector | C1 |  |  |  | 5V 10mA | no |
| 57 | FPGA Tibbit | io | M1S | -CS,-SCLK,-MOSI,-DONE/MISO | 19,20,21 |  | 5V 25mA | yes |
| 58 | Two 24V NPN isolated open collector outputs | output | M1S | -OUT1,-OUT2,3,4 | 19,20,21 |  | 5V 20mA | yes |
| 59 | Two 24V PNP isolated open collector outputs | output | M1S | -OUT1,-OUT2,3,4 | 19,20,21 |  | 5V 20mA | yes |
| 61_1 | ISOLATED ±10V, 4-20mA ADC Tibbit with 24V Output | io | H2 | -CS,SCLK,MOSI,MISO,SCL,SDA | 19,20 |  | 5V 120mA | yes |
| 61_2 | ISOLATED ±10V, 4-20mA ADC Tibbit | input | H2 | -CS,SCLK,MOSI,MISO,SCL,SDA | 19,20 |  | 5V 35mA | yes |
| 62 | Two 1-Wire/Single-Wire Ports | io | M1T | SCL,SDA,-RST,-BUSY | 21,20 |  | 5V 20mA | yes |
| 63_1 | AC Voltage Detector (110V) | input | H1 | ,,,-DETECT |  |  | 5V 12mA | yes |
| 63_2 | AC Voltage Detector (220V) | input | H1 | ,,,-DETECT |  |  | 5V 12mA | yes |
| WA2000C | WA2000C Wi-Fi Add-on Module with on-board antenna | empty | WIFI |  |  |  | 5V 200mA | yes |
| WA2000U | WA2000U Wi-Fi Add-on Module | empty | WIFI |  |  |  | 5V 200mA | yes |
| WM6256 | WM6256 Wi-Fi Add-on Module | empty | WIFI |  |  |  | 5V 200mA | yes |


## Сверка с docs.tibbo.com (октябрь 2026)

Сверены 76 страниц `tibbit_NN` (поля Function, Form factor, Category, Special needs, Power requirements, Mates with, статус) с каталогом. Исправлено в `data/tibbits.src.json` (затем `scripts/build_data.py`):
- **#02, #44-1, #44-2**: в docs особые требования [SER] и [INT] (INT нужен для RTS/CTS), в каталоге было только serial → добавлено interrupt. На TPP2/TPP3 все UART-сокеты имеют линию прерывания, поэтому раскладка не меняется.
- **#13, #14**: в docs потребление 5V/10 мА (#13) и 5V/20 мА (#14) плюс ±15 В; «66 мА» и «56 мА» в каталоге - это суммарная нагрузка на +5V **вместе с** долей #12 (10 + 4,5 × (9 + 3,5) ≈ 66; 20 + 4,5 × 8 = 56). `tps_check.py` считает долю #12 отдельно, поэтому собственное потребление исправлено на 10 и 20 мА (раньше бюджет завышался на ~56 и ~36 мА).
- Mates по docs: #09/#10/#25/#33 → #18, #19, #20, #21; #16/#17 → ещё #19; #23 → #19, #20, #21 (нижняя часть), #37.
- Добавлены отсутствовавшие в каталоге **#47** (GPRS-модем, H2, [SER], 5V/300 мА, пики 1,5 А, DEPRECATED → #45/#46), **#51** (CAN, M1S, [CAN], 5V/60 мА + до 200 мА на CAN-устройства, DEPRECATED, только LTPP3 первого поколения), **#56** (USB Type-A, C1, [USB], 5V/10 мА + до 500 мА, DEPRECATED, только LTPP3 первого поколения). В новых проектах не использовать.

Расхождения, оставленные как есть (каталог Tibbo против страницы docs):
| Tibbit | Каталог (`requires`) | docs «Special needs» | Как понимать |
|---|---|---|---|
| #08 | serial, interrupt | [SER] | Подключается к RX и CTS UART; CTS на TPP - линия D (прерывание), так что сокет с UART всё равно нужен с INT. |
| #22 | interrupt | - | По docs особых требований нет; INT-линию каталог резервирует под сигнал готовности. |
| #45-1~3, #46 | serial, interrupt | [SER] | INT нужен для RTS/CTS модема; по docs обязателен только UART. |
| #11 | - | [SER] (если нужна эмуляция считывателя) | Для эмуляции Wiegand/clock-data подключается к TX и RTS UART. |
| #23 | - | [POE] (если не как обычный источник 35–60 В) | Проверяется отдельно в `tps_check.py` (PoE-сокет, перемычки). |
| #33, #63-1/-2 | - | [INT] (необязательно) | -PF у #33 (импульс 50–100 мс, Tibbo советует прерывание) и -DETECT у #63 ловить прерыванием: сокет с INT на линии D. Линии #33 в данных Tibbo расходятся - power.md §1. |
| #48, #50 | - | [AUD], [USB] | Платформенные требования, устарели. |
| #61-1, #61-2 | форма H2 | H2T | Исправляется при сборке (`DOCS_FORM` в build_data.py). |
| #00-1 | mates 19,20,21,49 | #19, #20, #21 | #49 (microSD) в docs как пара не указан. |

Питание по docs, важное для бюджета (пики не учитываются средним током каталога): #27 - до 200 мА пиково; #45 - 500 мА в среднем, **пики до 2 А**; #47 - 300 мА, пики 1,5 А (источник #33 или #25 от 24 В и выше, или #23); #62 - 20 мА в среднем, до 70 мА в зависимости от датчиков; #03/#06/#07/#58/#59 - указанный ток при обоих включённых выходах; #12 - 230 мА + 4,5 × ток нагрузки ±15 В; **#61-1 - 120 мА только без нагрузки на выходе 24 В**, под нагрузкой «до 500 мА»; выход 24 В - до 75 мА, Tibbo советует не больше 50 мА (docs: tibbit_61-1; `tps_check.py` считает по `loads`). Температурный диапазон −40…+85 °C указан для #33, #43, #45, #46, #61, #63.

Статусы по `tibbit_list`: DEPRECATED - #47, #48, #49, #50, #51, #52, #56; NOT RECOMMENDED FOR NEW DESIGNS - #53.
