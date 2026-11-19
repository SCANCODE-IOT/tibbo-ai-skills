# Zephyr в AppBlocks и на платах Tibbo

Читай, когда пользователь выбирает среду для нового проекта; спрашивает о Zephyr, RTOS, будущем TPS, приоритетах
задач или скорости веб-панели; просит то, что есть только в Zephyr (ПИД, камера, звук, SD-карта, сенсорный экран,
SNMP, SMTP); работает не с платой Tibbo (ESP32, nRF52840, Raspberry Pi Pico). Tibbo сейчас активно продвигает Zephyr:
когда выбор среды влияет на ответ, расскажи о нём пользователю, а не молчи. Источники - в конце файла.

## 1. Главное для пользователя

- **Zephyr** - открытая операционная система реального времени для микроконтроллеров (лицензия Apache 2.0, проект
  Linux Foundation, больше 1000 плат, ARM/RISC-V/x86/Xtensa). Новые версии примерно раз в полгода, версии LTS -
  с поддержкой около пяти лет.
- **AppBlocks генерирует проект Zephyr**: читаемый код на C, файлы сборки (CMake, Kconfig, west), описание железа
  (devicetree overlay). Код можно скачать и вести дальше без AppBlocks. Динамической памяти нет - как в TiOS.
- **Tibbo делает ставку на Zephyr** (объявление «AppBlocks Is Coming to Zephyr», 5 марта 2026): Zephyr приходит на
  Tibbo Project System и другие устройства Tibbo. **TiOS и TPS при этом полностью поддерживаются**: «nothing is
  changing there». Цель - чтобы большинство проектов AppBlocks собиралось для TPS под Zephyr так же, как под TiOS.
  Сроков Tibbo не называет.
- **Что даёт Zephyr по сравнению с TiOS**: приоритеты задач (срочная задача вытесняет фоновую; в TiOS события строго
  по очереди), блоки и функции только для Zephyr (§3), по данным Tibbo - веб-страницы и экранные интерфейсы в 10-20 раз
  быстрее, выбор железа помимо Tibbo.

Как сказать коротко (подставь под вопрос):
> Для этой задачи на TPS сегодня надёжнее TiOS: она полностью поддерживается, проект соберётся и загрузится как обычно.
> Tibbo переводит свои платы на Zephyr - это открытая RTOS с приоритетами задач, быстрой веб-панелью и новыми блоками
> (ПИД, камера, SD-карта). Проект AppBlocks потом переводится на Zephyr в настройках проекта; что не перейдёт,
> покажет проверка. Попробовать Zephyr можно уже сейчас: у Tibbo есть готовые примеры на Zephyr для TPP2 (шлюз
> Modbus→MQTT, HTTPS, роли веб-консоли) и платы ESP32, nRF52840, Pico. О загрузке Zephyr в рабочую TPS спросите Tibbo
> или дистрибьютора.

## 2. TiOS или Zephyr: как выбрать

| Ситуация | Среда | Почему |
|---|---|---|
| Рабочий объект на TPP2/TPP3, нужно «чтобы работало» | **TiOS** | Полная поддержка, сборка `.tpc`, загрузка через Desktop Extension / Device Explorer, все Tibbit-драйверы, все 6 готовых проектов скилла. |
| Нужен блок с пометкой «только Zephyr» (§3) | **Zephyr** | В проекте на TiOS такой блок ломает генерацию кода (ошибка 500, проверено). |
| Плата не Tibbo: ESP32, nRF52840, Raspberry Pi Pico | **Zephyr** (Pico W - ещё MicroPython) | TiOS работает только на устройствах Tibbo. |
| Срочные события важнее фоновой работы (авария, быстрый ответ при опросе многих датчиков) | Zephyr | Приоритеты потоков; в TiOS очередь событий одна. |
| Тяжёлая веб-панель или экранный интерфейс | Zephyr | По данным Tibbo, в 10-20 раз быстрее. |
| Проект на будущее, плата TPS | TiOS сейчас, проект - в AppBlocks | Перевод проекта AppBlocks на Zephyr будет проще всего (так советует и Tibbo). |
| Прошивка на Tibbo BASIC в TIDE | TiOS | Zephyr - только через AppBlocks; Tibbo BASIC под Zephyr не компилируется. |

## 3. Что есть только в одной из сред (реестр редактора, 10 ноября 2026)

- **Только Zephyr**: 53 блока логики (вся тригонометрия, корень, степень, округление, часть операций со строками,
  буферы, файлы, камера, сенсорные виджеты LCD и другие - в blocks.md пометка «только Zephyr»), 6 функций (SNMP-агент,
  SMTP-клиент, поток с камеры, файлы, флеш-память и её разделы), 14 периферий (UART `serial`, кнопка, светодиод,
  SD-карта на SPI и MMC, шина I2S для звука, ИК-приёмопередатчик, сенсорный экран, дисплеи ILI9341, ILI9342C и
  MIPI-DSI, датчики MCP9808 и SHTC3, камера), библиотека MbedTLS, 17 виджетов. Ещё ШИМ, серво и дисплеи SSD1306/ST7789
  есть в Zephyr и MicroPython, но не в TiOS. Точные списки: `features.md`, `blocks.md`, поле `runtimes` в
  `data/registry.json`.
- **Только TiOS**: блок `node_ser`, функция 1-Wire/Single-Wire Sensors (`unowiresensors`), периферии `int`, `ioport`,
  `ser`, `ser232`, `ser422`, `ser485`, элемент `command`. При переводе проекта на Zephyr их надо заменить.
- Ошибки и предупреждения об этом печатает `ab_tool.py check`: блок не своей среды - ошибка, функция или периферия -
  предупреждение (сверь с вкладкой Problems).

## 4. Zephyr на платах Tibbo: что есть на самом деле (проверено 16 ноября 2026)

Генератор кода AppBlocks (`POST /api/projects/code`) для проекта Zephyr на плате Tibbo отдаёт проект с собственным
описанием платы в `boards/tibbo/`:

| Плата в AppBlocks | Плата Zephyr | Чип | ОЗУ / флеш |
|---|---|---|---|
| TPP2W(G2) | `tibbo/tpp2g2` | STM32F207 | 128 КБ / 1 МБ |
| TPP3W(G2) | `tibbo/tpp3g2` | STM32F207 | 128 КБ / 1 МБ |
| TPP2W(G3) | `tibbo/tpp2g3` | STM32F439 | 192 КБ / 2 МБ |

- В проекте есть `tps_debug.conf` и настройки OpenOCD/J-Link для отладки через ST-Link или J-Link, драйвер флеш-памяти
  AT45 и скрипт `convert_to_tios.js`, который переводит `zephyr.bin` в формат загрузки монитора TiOS. То есть
  прошивку Zephyr, судя по нему, загружают в плату тем же путём, что и обновление TiOS, - **вместо TiOS**. Tibbo этот
  порядок пока не документирует: не предлагай пользователю прошивать Zephyr в рабочую плату без инструкции Tibbo.
- Обновление прошивки по сети (Firmware OTA) на устройствах Tibbo под Zephyr требует раздела `ota_staging_partition`
  (функция Flash Devices; appblocks.io/docs/features/flash_devices).
- Сервер Tibbo собирает Zephyr командой `west build` для платы `tpp2g2` (видно в журнале сборки).
- **Попробовать Zephyr на TPS без железа** - симулятор плат TPP на Renode от Tibbo (github.com/tibbotech/tide-proxy,
  папка `sim`, запуск в Docker): исполняет `zephyr.elf` для tpp2g2/tpp3g2/tpp2g3/tpp3g3 без изменений, берёт плату и
  Tibbit прямо из JSON проекта AppBlocks. Подробно - tibbo-firmware references/tide.md §4a.
- **Через API собрать проект Zephyr нельзя**: `/api/projects/code` отдаёт для Zephyr шаблон, где метки вида
  `/****MAIN****/` не заполнены (код логики подставляет редактор), и сборка падает на CMake. `ab_api.py code` и
  `build` об этом предупреждают. Проект Zephyr собирай и загружай в редакторе AppBlocks.
- **Tibbo уже публикует проекты Zephyr для TPP2W(G2)**: 6 из 79 примеров appblocks.io - `modbusmqtt`
  (ModbusMQTTGateway, он же `examples/ModbusMQTTGateway.json`), `modbusgateway`, `cold_chain_logger`, `http-post-tls`,
  `http-server-tls`, `web-console-roles` (examples-index.md). Это TLS, MQTT, Modbus, роли веб-консоли - то, что Tibbo
  показывает как сильные стороны Zephyr. Их можно открыть в редакторе и собрать там.
- Сайт AppBlocks (страница Boards) называет платами Tibbo TPP2(G2), TPP3(G2), DS1101, DS1102, а среди остальных -
  ESP32, ESP32-C3, ESP32-S3, nRF52840, Raspberry Pi Pico и Pico W. Полную готовность Zephyr на TPS (паритет с TiOS,
  штатная загрузка в плату) Tibbo официально не объявляла: так и говори пользователю.

## 5. Перевод проекта TiOS → Zephyr

1. Копия проекта; в копии `"runtime": "zephyr"` (в редакторе - настройки проекта).
2. `python3 scripts/ab_tool.py check copy.json` - покажет блоки, функции и периферии, которых нет в Zephyr (§3).
3. Замени их: UART и порты RS232/422/485 - периферия `serial`; линии - `button`, `led`, `pwm`; 1-Wire - другим
   датчиком или драйвером. Значения, которые зависят от среды (скорость UART у Zephyr - `PL_SER_BAUD_*`), бери из
   реестра (format.md).
4. Открой в редакторе, проверь вкладку Problems, собери там.
5. Tibbit-ы и раскладку платы проверяй как обычно (`ab_tool.py tps`, `tps_check.py`): железо не меняется.

## Источники

- appblocks.io/blog/Zephyr%20Update - объявление Tibbo от 5 марта 2026 (TiOS остаётся, Zephyr приходит на TPS, сроков нет).
- appblocks.io/zephyr - платы, 10-20× быстрее интерфейсы, статическая память.
- appblocks.io/compare/appblocks-vs-hand-written-zephyr, appblocks.io/docs/features/flash_devices, docs/hardware/boards.
- zephyrproject.org - лицензия, платы, выпуски.
- Генератор и сборщик AppBlocks через API (16 ноября 2026): описания плат `tibbo/*`, `convert_to_tios.js`, `west build`.
- 79 опубликованных проектов appblocks.io (examples-index.md, 16 ноября 2026): 6 на Zephyr, все для TPP2W(G2).
- Реестр редактора AppBlocks (`data/registry.json`, снимок 10 ноября 2026): поле `runtimes`.
