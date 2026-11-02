# AppBlocks: редактор, понятия, правила исполнения (по appblocks.io/docs, октябрь 2026)

Источник - официальная документация (docs/intro, concepts/*, setup/*, settings/linking, features/*, tips/*)
и сам редактор app.appblocks.io (реестр блоков, проверки и встроенный помощник; снято 22.10.2026, §9–10).
Пересказ; при сомнении открой страницу: `https://appblocks.io/docs/<раздел>` (WebFetch; карта — appblocks.io/sitemap.xml).

## 1. Три шага проекта
1. **Hardware** — что за устройство. Плата выбирается при создании и **потом не меняется**.
   - TPS (TPP2, TPP3): редактор-картинка. Слева библиотека Tibbit по группам (Power, Digital Inputs, Relays & Outputs,
     Analog I/O, Serial Ports, Sensors), в центре плата: M-сокеты S1, S3, S5… для модулей, C-сокеты S2, S4… для разъёмов;
     подписи сокетов показывают последовательные порты и линии прерываний. Справа Device sidebar: опции платы
     (LCD+клавиатура TPP2, PoE, корпус), кнопка Datasheet, **индикаторы питания +5V, +15V, −15V**, настройки Tibbit.
     Предупреждения: модулю нужен разъём рядом / разъём без модуля; модуль и разъём не сочетаются; Tibbit потребляют
     больше 5 V, чем даёт источник (предлагает #10 или #33); WA2000U нужен #37 для антенны; «You will not have control
     of the shutdown line, power supply will always be enabled» — источник не в том сокете; «Not enough power for
     +15/-15V. Add a Tibbit #12.»; последовательный Tibbit — только в подсвеченные serial-сокеты.
   - Другие платы: схема выводов, Add Peripheral → Assign Pin; Show Pin Definitions.
   - **Каждая линия/датчик становится переменной** (по умолчанию `T29_S2_TEMP`; имя линии = имя переменной).
     Типы: реле и цифровые I/O — Boolean, температура и АЦП — Float, свет и LED — Word. Входы опрашиваются с Update
     Interval (**минимум 1 с**, по умолчанию 1; меньше — ошибка «Value for Update Interval (seconds) must be at least 1»); для быстрых сигналов — события On Button Pressed / Interrupt.
2. **Features** — сервисы прошивки (включаются переключателем Enabled; Timers, Scheduler, Commands, Socket, Modbus,
   1-Wire включаются сами при добавлении элемента). Зависимости включаются автоматически (Cloud → Settings, Log,
   Firmware OTA, MQTT). Блок на холсте включает свою feature. Все автоправки — во вкладке **Change Log**.
   Группы: General (General, Variables, Timers, Scheduler, Commands, Log) · Data & Storage (Settings, Data Tables,
   Flash Devices, Firmware OTA) · Connectivity (Ethernet, Wi-Fi, Cellular, Bluetooth) · Cloud & Messaging (MQTT,
   Azure IoT Central, AppBlocks Cloud) · Network Services (HTTP Server, HTTP Client, Socket, DNS, SNTP, MbedTLS,
   SNMP Agent, SMTP) · Industrial (Modbus Master, Modbus Slave) · Sensors (1-Wire/Single-Wire, WM2000EV) ·
   Displays (LCD for TPP2, OLED SSD1305) · Dashboards (Web Console, LUIS BLE, DS Manager) · Custom (плагины).
   **Link to setting** — значение свойства становится настройкой устройства (меняется с панели/облака/блоками).
3. **Application** — блоки на холсте, соединённые в потоки.

## 2. Редактор приложения
- Слева вкладка **Library** (блоки по категориям; фильтры All / Triggers / Actions; Search blocks) и **Blocks** (что на холсте).
- Холст: перетаскивание, двойной клик, **Add block**, правый клик → **Insert Block**. Вкладки холста (**Main**, «+»,
  переименование двойным кликом, **Move to Tab**) — только для порядка, на исполнение не влияют.
- Справа — параметры выбранного блока. Панель блока: **Add Breakpoint**, **Rename**, **Make a Copy**, **Delete Block**.
- Снизу: **Problems** (валидация: «Invalid Variable», «Value must be set for …», «Recursion not allowed», «Name conflict: X. No duplicate names allowed» - format.md §4 п.16),
  в Debug — **Debug Console** и **Variables**; есть просмотр сгенерированного кода; меню Share/Export справа сверху.
- **Run** (справа сверху): режим **Debug** (по умолчанию: отладочная прошивка, консоль, точки останова, устройство
  останавливается без связи с редактором, мигает зелёный LED) или **Deploy Release Version**. **Download Release
  Binary** — .tpc для ручной загрузки через Device Explorer → Upload Application.
- Для загрузки и отладки на устройстве нужен **Tibbo Desktop Extension** (настольная программа, находит устройства
  в локальной сети; Windows — разрешить доступ к сети, macOS — разрешить Local Network Access в браузере).
- Симулятор — в AppBlocks Desktop: Run → **Start Simulator** (GPIO, датчики, LCD, MQTT/HTTP/сокеты, точки останова).
- **Import / Export**: на странице нового приложения кнопки **Import** (выбрать .json → появится в списке проектов)
  и **Export** (скачать .json). Открыть проект по ссылке: `https://app.appblocks.io/app/project/new?url=<URL JSON>`.
- Смена runtime: File › Application Details… › Runtime → Convert или Make a Copy (часть feature может не перейти).

## 3. Runtime
| Runtime | Платы | Особенности |
|---|---|---|
| **tios** | TPP2, TPP3, DS1101, DS1102, EM510 | Tibbo OS; Tibbit, LCD/клавиатура TPP2, DS Manager, 1-Wire. Одно событие за раз, остальные ждут. Сборка — .tpc/.pdb (Tibbo BASIC) |
| **zephyr** | сотни плат (ESP32, nRF52840, RP2040…), а также TPP2/TPP3 | Приоритетные очереди (срочные потоки вытесняют); SNMP, SMTP, MbedTLS |
| micropython | часть Zephyr-плат (Pico) | |
Сгенерированный код смотри через `ab_api.py code` (POST /api/projects/code). Для `tios` это Tibbo BASIC — его можно
проверять скиллом tibbo-firmware.

## 4. Блоки и потоки — правила
- Типы блоков: **событие** (только выходы; начинает поток: On Boot, On Time Period, On Variable Changed, On Command,
  On MQTT Notification…), **действие** (вход, обычно выход Done), **условие** (вход, выход на каждый исход: True/False, кейсы Switch).
- Поток = событие + всё, что за ним. **Блок, недостижимый из события, в прошивку не попадает.**
- Выход можно вести на несколько входов, вход может принимать несколько проводов (каждый приход — отдельный запуск).
- В событие провод вести нельзя. **Циклы запрещены** («Flows can't loop back on themselves») — повторы делай через
  таймеры, команды (Command Trigger → On Command) или For Loop.
- **Параметры блока** (значения, передаваемые следующему блоку: `time_now`, `value_old`, `data`, `response_data`,
  `rows`…) видны **только в блоке, подключённом напрямую**. Чтобы использовать дальше — сохрани в переменную.
- Исполнение в глубину; ветви одного выхода — сверху вниз по положению на холсте (горизонталь не важна).
- Set Variable может запустить On Variable Changed; на TiOS — сразу, до следующего блока текущего потока.
  Поток от On Variable Changed не может менять ту же переменную («Recursion not allowed»).
- **ASYNC-блоки** (Delay, HTTP Request, Modbus Request, Send Email, Play Audio, Calculate, Random): продолжение
  выполняется позже; **параметры предыдущих блоков теряются** — переноси через переменные. Delay не блокирует;
  на TiOS повторный запуск ожидающего Delay перезапускает его. Для отменяемых/повторных ожиданий — таймеры.
- Держи потоки короткими: на TiOS длинный поток задерживает все события.

## 5. Переменные и настройки
- Имя: буквы, цифры, `_`, начинается с буквы, уникально среди переменных, настроек и таймеров.
- Типы: Value(number), String(text), Date Time, Time (у связанных — Boolean, Word…). Min/Max обрезают значение при
  записи (у String Max — длина). Default — значение при загрузке.
- Виды: Project (RAM, сброс при загрузке), Hardware (авто, опрос с Update Interval из Features › Variables; редактор принимает **не меньше 1 с**, проверено на импорте в октябре 2026), Setting (энергонезависимые),
  Timer. Авто-переменные не переименовываются и исчезают вместе с источником.
- Настройка видна пользователю, только если добавлена в группу панели (Web Console, LUIS, DS Manager, меню LCD, Cloud).
  Сетевые и стартовые настройки применяются после перезагрузки.

## 6. Свои плагины (Custom Plugins)
Feature Type: Service (Custom Services), Peripheral, Block (ID начинается с `node_custom_`), Array Sub Item.
Поля: Name, Feature ID, Version, Runtimes (TiOS/MicroPython/Zephyr), Requirements, Dependencies, Provided Capabilities,
Settings (Setting ID, тип Name/Value/Dropdown/Array/Feature/Pin; Data Type String/Byte/Float/Integer/Boolean/DWORD/Long;
Pin Requirement GPIO/Interrupt/PWM/ADC/TX/RX/RTS/CTS/DTR/DSR), Code Blocks (Code или File; Code ID — без дублей),
Variables (выход Block-плагина).
Code Location: Boot, Boot Complete, System Tick, Network Connected, Global Includes, Function Definitions,
Block Triggered (для Block), любой другой маркер сгенерированного кода; в JSON встречается `PRJ_CONF_OVERRIDES` (Kconfig Zephyr).
Шаблоны в коде: `{{feature}}`, `{{feature.id}}`, `{{feature.settings.ID}}` (`.pin` для пинов), `{{parent…}}`,
`{{project}}`, `{{project.device}}`, `{{block.output}}`.
**Маркетплейс плагинов** (Custom › Browse): одобренные Tibbo плагины ставятся в проект одной кнопкой; в октябре 2026 их
три (проверено и 2 ноября 2026: Time to String HH:mm `node_custom_minutes_to_string`, DeadBand Block `node_custom_deadband`, Panasonic AC IR Control `node_custom_panasonic_IR`; автор - Tibbo; список - `GET /cgg/extensions`, api.md), все Block для tios: перевод минут в строку «ЧЧ:ММ», зона нечувствительности (deadband) и ИК-команды кондиционера
Panasonic через Tibbit #26. Формат JSON и разбор на примерах - format.md §5. Свой Block-плагин - когда нужного блока
нет в blocks.md: короткий код Tibbo BASIC в Block Triggered, результат - в Variables, в конце `{{block.output}}`.

## 7. Частые проблемы (docs/tips/troubleshooting)
- Нет вывода в консоль на не-Tibbo плате → Features › General › Debug Print Output.
- Работало и сломалось → Change Log внизу.
- Предупреждения про -SDWN, ±15 В, serial-сокеты — см. §1 (то же проверяет tps_check.py).
- Проверить, что сгенерировалось → Share/Export или просмотр кода внизу.

## 7а. Короткие сигналы
Опрос входов раз в секунду пропускает короткие импульсы (кнопка выхода, датчик прохода, счётчик). Такие линии ставь
на линию прерывания (линия D сокета, INT0–INT5; по одной на сокет) и обрабатывай блоком Interrupt. Если линий
прерываний не хватает — разнеси входы по сокетам или предупреди, что сигнал нужно держать ≥ 1 с.

## 8. Типовые схемы (docs/tips/patterns)
Конечный автомат (переменная state + On Variable Changed + IF), очередь команд в таблице с повторами,
антидребезг (счётчик стабильности), heartbeat по MQTT, circuit breaker, пакетная отправка, ретраи с экспоненциальной
паузой, наблюдатель (несколько On Variable Changed на одну переменную), сторожевой таймер, factory reset по удержанию
кнопки, агрегация телеметрии (min/max/среднее за период), деградация при потере облака/датчика.

**Шкала уровня сигнала TPP2/TPP3 (5 синих LED) из логики** (код драйвера - generated-code.md):
- компактно: блок Custom Function с кодом `signal_strength_set(&h1F)` (все горят) или `signal_strength_set(0)` (все погасли);
  бит 0..4 = LED 1..5 [генерация показала, что код вставляется и процедура объявлена; компиляция в TIDE и железо не проверены];
- только блоками: Digital Line Set 48 (данные: 0 - горит, 1 - не горит), затем 5 пар Digital Line Set 47 = 0 и 47 = 1 (такты) -
  11 блоков на состояние «все одинаково»; линии 46-48 уже выходы благодаря фреймворку [не проверено на железе].

## 9. Проверка железа в редакторе (правила сокетов)
Редактор проверяет раскладку при каждом изменении функцией `getTppProjectWarnings` и рисует **жёлтый треугольник** на
сокете; текст появляется, если навести курсор на Tibbit. **Эти предупреждения не попадают ни в Problems, ни в счётчик
⊗/⚠ строки состояния и не мешают сборке**: проект с «0 ошибок, 0 предупреждений» может быть с треугольниками на плате.
Правила (сняты из кода редактора, октябрь 2026; данные - `data/appblocks_pairs.json`):

| Текст | Когда |
|---|---|
| Incorrect pair | в паре M/C разъём не из списка `mates` M-модуля (таблица редактора, а не документация) |
| Connector required | у модуля есть разрешённые разъёмы, а его C-сокет пуст (у M2 - только первый C) |
| Tibbit required | разъём или C-датчик стоит, M-сокет пуст (#28-#41 ждут #00-3, #49 - #00-1) |
| строка про линию | у сокета нет линии, которую модуль использует (например, -SDWN источника в S27 TPP3) |
| RF Connector Required for Wifi | WA2000U без #37 в RF-сокете |

C2-разъём (#19, #20) снимает «Connector/Tibbit required» в своём тайле, если хотя бы одна пара под ним полная, но не
«Incorrect pair». **Таблица редактора строже документации**: источникам #09, #10, #25, #33 редактор разрешает только
#18 (docs.tibbo.com - ещё #19/#20/#21), у #12 и #23 разрешённых разъёмов нет, #16/#17 - без #19. Поэтому одно из
частых «Incorrect pair» - один #20 на #54 и #09 в тайле S9-S12; замена - #21 для #54 и #18 для #09.
`ab_tool.py check` и `tps_check.py check` (скилл tibbo-firmware) повторяют эту проверку и пишут «плата: …» /
«AppBlocks отметит …»; совпадение с редактором проверено на 60 случайных раскладках TPP2/TPP3.

## 9а. Вид Wiring: схемы Tibbit с номерами контактов
Панель DEVICE → переключатель **Wiring** (вместо Tibbits) рисует на плате схему каждого Tibbit: контакты M-модуля
(1-12), контакты разъёма и номера клемм, кто к чему подключён. Масштаб - кнопкой «+» внизу холста, перемещение -
перетаскиванием. Это самый быстрый способ узнать, на какую клемму #20/#21/#18 выходит конкретная линия модуля:
так установлено, что на TPP2(G2) у #20 в S10+S12 клеммы 1-4 идут на модуль в S9, клемма 5 - земля, клеммы 6-9 - на
модуль в S11 (вход 10-18 В у #09 - клемма 6). Под картинкой холста есть отдельные блоки «Tibbit #NN Wiring (Socket N)».

## 10. Встроенный ИИ-помощник редактора
В редакторе есть свой чат-помощник. Он видит проект не как JSON, а как **текстовый исходник** (каждая feature -
запись `F.<тип>` с полями настроек, картинки - `asset('имя')`), умеет искать по нему, смотреть справку и примеры,
подбирать сокеты, править, переименовывать, **проверять** (ошибки в виде `строка:колонка уровень [feature.ПОЛЕ] текст`)
и прогонять симуляцию, а изменения применяет к проекту только по команде. Сокет Tibbit он может выбрать сам
(`SOCKET: 'auto'`): ставит модуль в свободный подходящий сокет и при необходимости добавляет к нему разъём.
Что из этого следует для работы со скиллом:
- Пользователь может попросить правку у встроенного помощника - это нормальный путь для мелких изменений в открытом
  проекте; для разбора, ревью, массовых правок, схем и API - этот скилл.
- Тексты ошибок помощника и вкладки Problems совпадают по смыслу с `ab_tool.py check` (§4 format.md); если пользователь
  прислал ошибку, которой `check` не ловит, - добавь её в проверку.
- Функции помощника требуют лицензии стороннего компонента (CopilotKit); если он недоступен, это не ошибка проекта.

## 11. Что ещё есть в приложении (ноябрь 2026)
- **Группы логики показываются вкладками** над холстом AppBlocks (Main + по вкладке на группу). Связь между блоками
  разных групп работает и генерируется, но на одном холсте её не видно - общий такт лучше держать в той группе, где
  большинство его получателей, а в описании группы писать, куда он ведёт.
- **Строка состояния** внизу: `Errors: N, Warnings: N` (то же, что вкладка Problems) и число переменных проекта.
  Предупреждения холста Hardware (жёлтые треугольники) сюда не входят - смотри саму плату или `ab_tool.py check`.
- **Web Console → General → Dashboard** - предпросмотр веб-панели с виджетами, без устройства.
- **PCB Designer** (`/pcbs`): свои платы в tscircuit или импорт из KiCad, на них можно начать проект AppBlocks.
- **Plugins Marketplace** (`/marketplace`): одобренные плагины (§6), загрузка своих (Upload Plugin, проходят модерацию).
- Главная страница: поле «What are we building today?» - генерация проекта по описанию встроенным ИИ (§10).

