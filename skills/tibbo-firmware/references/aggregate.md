# AggreGate и оборудование Tibbo

Когда открывать: пользователь спрашивает про AggreGate (SCADA/HMI, IoT-платформа, «Агрегейт»), про подключение
контроллеров и модулей Tibbo к AggreGate, про библиотеку AGG, Embedded AggreGate или LTPP с AggreGate.
API библиотеки AGG (defines, процедуры, колбэки, enum) - в `libraries.md`, раздел `## aggregate/aggregate.tbh`.
Источники (проверено 28.11.2026): aggregate.digital (сайт и документация 6.4), docs.tibbo.com/lib_agg,
github.com/tibbotech/CA-Test-AGG-lib, tibbo.com/linux/embedded-aggregate.

## 1. Кто есть кто - не путать

- **Tibbo Technology** (Тайбэй, Тайвань) - железо: TPS, Tibbit, DS, EM, WM, WA, LTPP3(G2), TiOS, TIDE, AppBlocks.
  Производство - на Тайване, завод группы Gigatek в Тайчжуне (tibbo.com/about-us).
- **Tibbo Systems** (ООО «Объединение Агрегейт») - разработчик платформы **AggreGate**. Название общее по истории,
  сейчас это разные компании. Не пиши, что AggreGate - продукт Tibbo Technology, и наоборот.
- Поддержка AggreGate - у Tibbo Systems и её партнёров; железо Tibbo в России и СНГ - у Сканкода (tibbo.ru).

## 2. Что такое AggreGate

- Low-code платформа IoT и SCADA. Продукты: IoT Platform, Edge, Network Manager, SCADA/HMI, Building Automation,
  Data Center Supervisor, MES/OEE.
- Данные приходят через **драйверы** (сервер сам опрашивает устройство по стандартному протоколу), **агенты**
  (устройство само подключается к серверу по протоколу AggreGate, буферизует данные без связи) и **шлюзы**
  (сервер AggreGate на промышленном ПК, Linux-ПЛК, одноплатнике).
- Драйверы в документации 6.4 (больше 50): Modbus, BACnet, DNP3, DLMS/COSEM, IEC-104 (и сервер IEC-104), Ethernet/IP,
  Siemens S7, Omron FINS, M-Bus, NMEA 0183, IPMI, OPC (классический), OPC UA (и сервер OPC UA), MQTT, CoAP, Kafka, SNMP,
  WMI, HTTP/SOAP, SQL, Flexible (настраиваемый без кода) и **TPS** (только в AggreGate для Linux TPS, см. §4).
- SCADA/HMI: проекты и мнемосхемы в браузере, МЭК 61131-3 (LD, FBD, SFC, ST), скрипты Java и Python, тревоги, тренды,
  отчёты, резервирование сервера. По данным разработчика - в реестре российского ПО, совместимость с Astra Linux и РЕД ОС.
- Лицензии: бессрочные и подписка; именные, привязаны к серверу (активационный ключ сервера). Цены - по запросу у
  Tibbo Systems. Не называй цен и не обещай бесплатный режим: в открытой документации их нет.
- Документация: https://aggregate.digital/docs/ru/ (6.4 - текущая, 7.0 - ранний доступ).

## 3. Четыре способа связать Tibbo с AggreGate - выбирай по задаче

| Способ | Что делает Tibbo | Что делает AggreGate | Когда выбирать |
|---|---|---|---|
| Modbus TCP или MQTT | Прошивка TiOS: ведомый Modbus TCP (рецепт 14-modbus-tcp-slave) или публикация в MQTT (07-mqtt-publish-subscribe) | Драйвер Modbus или MQTT, переменные описываются на сервере | По умолчанию: стандартно, та же прошивка подойдёт для любой SCADA |
| Агент AGG на TiOS | Библиотека `aggregate` (AGG): устройство само описывает A-переменные, A-функции, A-события | Принимает агента, показывает его контексты | Много одинаковых устройств, нужна смена настроек и команды с сервера |
| Embedded AggreGate на LTPP | Linux-плата LTPP с сервером AggreGate на борту | Сервер на плате; драйвер TPS - чтение и запись GPIO, нужен плагину управления процессами | Небольшой объект, сервер прямо в шкафу; наличие для LTPP3(G2) уточнять у Tibbo |
| Конвертер DS + Modbus Gateway | DS1101/DS1102/WS1102 переводит Modbus RTU в Modbus TCP, программировать не нужно | Драйвер Modbus TCP | Готовые приборы Modbus RTU без своей логики на объекте |

Если пользователь не просит именно агента, предлагай сначала Modbus TCP или MQTT: проще отлаживать, нет привязки к
одной SCADA. Агент AGG - когда нужны его сильные стороны (самоописание, буфер событий, функции с сервера).

## 4. Библиотека AGG (агент на Tibbo BASIC/C)

- Файлы: `aggregate.tbs`, `aggregate.tbh` из набора библиотек (`current_library_set\aggregate\trunk\`, свежая версия -
  github.com/tibbotech/libraries, папка `aggregate`). Работает на любой платформе TiOS; без RTC нужен свой источник
  времени (`AGG_CUSTOM_RTC` = 1 и `callback_agg_rtc_sg`).
- Зависимости: `sock` (обязательно), `time`; `wln` - для Wi-Fi, `gprs` - для GPRS. A-переменные-настройки идут через
  `settings` (STG), таблицы - через `tables` (TBL, включается `AGG_TABLE_CONTROL`). Буферы: библиотеке нужно 4 страницы.
- Описание переменных, функций и событий - файл-дескриптор (`AGG_DESCRIPTOR_FILE`, по умолчанию `aggregate.txt`),
  который правят конфигуратором AggreGate в TIDE; в примере Tibbo - `aggregate.xtxt` рядом с `settings.xtxt`.
- Модель устройства:
  - **A-переменные** - настройки и таблицы, читаются и пишутся сервером; преобразование значений -
    `callback_agg_convert_setting`, `callback_agg_convert_table_field`;
  - **A-функции** - команды сервера, код в `callback_agg_device_function(function_name, context_name, input, output)`;
    аргументы разбирают `agg_record_decode`, ответ собирают `agg_record_encode`;
  - **A-события** - мгновенные `agg_fire_instant_event(...)` или сохранённые (журнал): после добавления в журнал -
    `agg_stored_event_added(...)`, отправка - `agg_proc_stored_events()`; размер журнала - `AGG_MAX_NUM_STORED_EVENTS`.
- Запуск: `agg_start(interface, owner_name, device_name, password, server_ip, server_port, ...)` из `on_sys_init` после
  старта `sock`/`stg`. Имя владельца и пароль должны совпадать с учётной записью на сервере (в примере Tibbo - `admin`).
  Точную сигнатуру бери из `libraries.md` или из `.tbh` в проекте - версии расходятся.
- Проброс событий: `agg_proc_timer()` из `on_sys_timer`, `agg_proc_data()` из `on_sock_data_arrival`,
  `agg_proc_data_sent()` из `on_sock_data_sent`, `agg_proc_sock_event(...)` из `on_sock_event`.
- Обязательные колбэки - список в `libraries.md` (в том числе `callback_agg_get_firmware_version`,
  `callback_agg_synchronized`, `callback_agg_error`, `callback_agg_pre_buffrq`, `callback_agg_buff_released`).
  Пустое тело допустимо, без реализации проект не соберётся.
- Удалённое обновление прошивки с сервера - `AGG_REMOTE_FIRMWARE_UPLOAD` = 1, прогресс -
  `callback_agg_firmware_upload_progress`.
- Образец - **github.com/tibbotech/CA-Test-AGG-lib**: СКУД по шагам (подключение, A-переменные-настройки, таблица кодов,
  A-функция «открыть дверь», мгновенное событие при старте, сохранённые события проходов). Начинай с него, а не с нуля.
- Документация docs.tibbo.com/lib_agg помечена как перерабатываемая: параметры процедур проверяй по `.tbh`, компилируй
  `tibbo_build.py`. Русский перевод - tibbo.ru/kb/docs/lib_agg.html.

## 5. Embedded AggreGate на Linux-плате

- Tibbo продаёт платы LTPP с опцией Embedded AggreGate (tibbo.com/linux/embedded-aggregate): полноценный сервер
  AggreGate на плате, работа с Tibbit через C++ API Tibbo, связь с другим железом Tibbo по протоколу агента.
- На aggregate.digital это «Linux-based Tibbo Project System» (LAPS): описана плата LTPP3 первого поколения (Sitara
  1 ГГц, 7 тайлов, корпус APB3). Про LTPP3(G2) в этих материалах ничего нет - не обещай, а предложи уточнить у Tibbo.
- Это не TiOS: программа здесь - конфигурация AggreGate и модуль управления процессами, а не Tibbo BASIC.
  Железо (Tibbit, питание) проверяй как обычно `tps_check.py` с платой LTPP3(G2) или по `linux.md`.

## 6. Как отвечать

- Сначала спроси или определи: есть ли уже сервер AggreGate, сколько устройств, нужна ли смена настроек с сервера,
  будет ли когда-нибудь другая SCADA. От этого зависит способ из §3.
- Железо подбирай по обычным правилам скилла (надёжность, раскладка без предупреждений AppBlocks, `tps_check.py`).
- Про лицензии, цены AggreGate и сроки - отсылай к Tibbo Systems или к поставщику проекта; не выдумывай.
