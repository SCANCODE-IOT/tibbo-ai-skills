# MQTT: AppBlocks, библиотека Tibbo и свой брокер (Mosquitto)

Проверено на проекте «Умная теплица» (TPP3W(G2), tios, октябрь 2026): генерация кода, компиляция в сборщике Tibbo
(`ab_api.py build`), приём данных логгером через брокер. Поля feature `mqtt` - features.md, блоки - blocks.md
(`node_mqtt_pub`, `node_mqtt_sub`, `node_mqtt_change`), API библиотеки - tibbo-firmware `references/libraries.md` (`## mqtt/`).

## 1. Когда какой путь
| Задача | Путь |
|---|---|
| Данные в свой софт (ноутбук, сервер, SCADA, Node-RED, Grafana) | feature **MQTT** + свой брокер (Mosquitto, EMQX) |
| Облако Tibbo: дашборды, OTA, команды, workflow | **AppBlocks Cloud** (feature `cgg`) - он сам ходит по MQTT с deviceId + key |
| Только веб-страница на устройстве | Web Console, MQTT не нужен |

## 2. Feature `mqtt` в проекте
- `MQTT_SERVER_HOST` (IP или имя; имя резолвится DNS-библиотекой), `MQTT_DESTINATION_PORT` (1883, с TLS обычно 8883),
  `MQTT_APP_CLIENT_ID` (уникален на брокере: два устройства с одним client id выбивают друг друга),
  `MQTT_NAME`/`MQTT_PASSWORD` (пусто = анонимно), `MQTT_TLS` (+ CERTIFICATEFILE), `MQTT_KEEPALIVE_INTERVAL`, `TOPICS`.
- **IP брокера - через настройку.** Адрес ноутбука меняется: заведи `stg_setting` (строка, напр. `MQTTHOST`) и
  `linked_setting` {SETTINGID: `MQTT_SERVER_HOST`, LINKEDSETTING: ID настройки, FEATURE: ID feature mqtt}. Генератор
  пишет `mqtt_start(current_interface, MQTTHOST, "1883", …)` - адрес меняется в веб-консоли без перепрошивки.
  Логин и пароль брокера так же выноси в настройки, не держи открытым текстом в проекте.
- `TOPICS` - только **подписки**: `mqtt_topic {TOPIC_NAME, NAME, QOS}`. Подписка делается в `callback_mqtt_connect_ok`,
  то есть заново после каждого переподключения. Публиковать можно в любой топик без объявления (`node_mqtt_pub.topic`).
- Поддержка шаблонов: генератор проверяет `mqtt_topic_match(...)`, топик подписки может содержать `+`/`#` (проверь на своём брокере).

## 3. Блоки
- **MQTT Publish** (`node_mqtt_pub`): аргументы `topic`, `publish_data`, `qos` (`QOS_AT_MOST_ONCE` | `QOS_AT_LEAST_ONCE` |
  `QOS_EXACTLY_ONCE`), `retain` (`false`/`true`). Выход `done`.
  Полезная нагрузка - строка-шаблон: `soil1={{$ID1}};air_t={{$ID2}}` генерируется в
  `"soil1=" + ftofixed(soil1,4) + ";air_t=" + ftofixed(air_t,4)`; float - `ftofixed(x,4)`, целые и boolean - `str(x)`.
  Формат `ключ=значение;…` проще всего разбирать на приёмнике; JSON с кавычками в шаблоне не проверялся.
- **On MQTT Notification** (`node_mqtt_sub`, поле TOPIC = ID `mqtt_topic`): выход `callback_mqtt_notif` с параметрами
  `{{$data}}`, `{{$topic}}` - видны только **следующему** блоку (обычно IF: `{{$data}} = water1` → `if data = "water1"`).
  Команду сравнивай в первом же блоке, дальше передавай через переменные.
- **On MQTT Change** (`node_mqtt_change`, CHANGE_TYPE 1/0) - подключились / отключились (индикация, флаг связи).
  Публикуй из него событие `online`: публикация в boot теряется (брокер ещё не подключён), а так видна каждая
  перезагрузка и каждый обрыв связи.
- Генератор сам мигает LED: при подключении `pat.play("G~")`, при потере - гасит.

## 4. Поведение библиотеки (важно для надёжности)
- **Публикация без связи молча отбрасывается**: `mqtt_publish` выходит, если состояние не `LOGGED_IN`. Буфера и
  досылки нет. Если пропуски недопустимы - копи данные в Data Tables (tbl) и досылай, или используй AppBlocks Cloud.
- Переподключение - само, через `MQTT_RECONNECT_TIME` (10 с); пинг - `MQTT_PING_TIMER`. Счёт по `sys.timercountms`,
  но `mqtt_proc_timer` всё равно вызывай из `on_sys_timer` (генератор делает это сам, период 0,5 с).
- **Сообщение вместе с топиком - не больше 255 байт.** `mqtt_publish` собирает пакет одной строкой Tibbo BASIC, лишнее
  обрезается без ошибки (компиляция проходит; `MQTT_LARGE_PACKETS 1` здесь не помогает). Телеметрию на 15-20 полей дели
  на несколько сообщений по топикам (`greenhouse/tele/env`, `…/io`, `…/bed1`); float занимает до 12 символов.
  `ab_tool.py check` считает худший случай и ругается при > 255.
- **Логика управления - на контроллере**, брокер и ноутбук - только журнал и ручные команды. Пропала сеть - полив,
  защита и вентиляция продолжают работать. Команды из MQTT повторно проверяют условия безопасности (вода есть и т.п.).

## 5. Свой брокер: Mosquitto
Установка: mosquitto.org/download (Windows - установщик, служба «Mosquitto Broker»; Linux - `apt install mosquitto`).
`mosquitto.conf` для учебного стенда в закрытой сети:
```
listener 1883
allow_anonymous true
```
Для рабочей установки - пароли и, по возможности, TLS:
```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd      # mosquitto_passwd -c /etc/mosquitto/passwd greenhouse1
```
Проверка без контроллера:
```
mosquitto_sub -h localhost -t "greenhouse/#" -v          # смотреть всё, что приходит
mosquitto_pub -h localhost -t greenhouse/cmd -m water1    # послать команду устройству
```
Частые причины «устройство не подключается»:
- брандмауэр Windows закрыл порт 1883 (разрешить входящие для mosquitto.exe или порта 1883);
- Mosquitto 2.x без строки `listener 1883` слушает только localhost;
- клиентская изоляция в школьной/гостевой Wi-Fi: устройства не видят друг друга - нужен свой роутер или точка доступа ноутбука;
- у ноутбука сменился IP - поменять настройку `MQTTHOST` в веб-консоли устройства (или дать ноутбуку статический IP);
- два устройства с одним `MQTT_APP_CLIENT_ID`.

## 6. Приёмник на компьютере
Пример - `examples/greenhouse2_logger.py` (Python, paho-mqtt + sqlite3 + matplotlib; это пример для пользователя, а не
инструмент скилла): подписка `greenhouse/#`, сборка пакета из `greenhouse/tele/*` в одну строку таблицы `tele`, разбор `ключ=значение;…`, журнал событий и тревог в SQLite, добавление новых столбцов в старую базу,
графики за N часов, отправка команд. Замечания:
- paho-mqtt 2.x требует `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, ...)`; для 1.x - старый конструктор (в примере есть оба).
- Значения реле с активным LOW приходят как уровень линии (0 = включено) - переворачивай при записи в базу.
- Для больших объёмов и дашбордов: Telegraf → InfluxDB → Grafana или Node-RED; для учебного проекта хватает SQLite.

## 7. Проверка
1. `ab_tool.py check` - 0 ошибок; 2. `ab_api.py build` - компилируется; 3. брокер + `mosquitto_sub` видят
`…/tele` после старта устройства; 4. `mosquitto_pub` команды - устройство реагирует (debug-вывод `sys.debugprint`).
