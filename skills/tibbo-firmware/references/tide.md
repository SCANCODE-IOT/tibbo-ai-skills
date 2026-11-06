# TIDE: сборка, загрузка, ошибки компилятора

Как собирать и загружать проекты Tibbo без ручной работы в окне TIDE и как читать ошибки компилятора.
Инструмент: `scripts/tibbo_build.py`. Данные о командной строке TIDE сняты с TIDE 2023 (tmake, tupload v5.04.50).

## 1. Что нужно от пользователя

| Что хотим | Что нужно | Как проверить |
|---|---|---|
| Проверить код компилятором Tibbo | **Вариант А:** TIDE установлен на этом компьютере с Windows (агент работает там же). **Вариант Б:** любой компьютер с интернетом и **согласие пользователя** отправить файлы проекта на сервер Tibbo (облачный компилятор AppBlocks). | `python3 scripts/tibbo_build.py --doctor` |
| Получить готовый `.tpc` | То же, что выше. `--release` - для работы без TIDE. | `tibbo_build.py <проект> --release` |
| Загрузить `.tpc` в устройство | Windows + TIDE (`tupload.exe`), устройство в той же сети (или по COM-порту), **явное «да» пользователя** на каждую загрузку. | `tibbo_build.py --upload app.tpc --target <адрес> --yes` |
| Отлаживать по шагам, смотреть переменные | Только в окне TIDE (Debug). Агент с управлением компьютером может работать в окне TIDE, остальные - объясняют шаги. | - |

Настройки:
- `TIDE_DIR` - папка TIDE, если не `C:\Program Files (x86)\Tibbo\TIDE`.
- `TIBBO_CLOUD_BUILD=yes` - согласие на облачную сборку для всех проектов (иначе - ключ `--cloud-ok` после вопроса).
- Облачная сборка ходит на `api.appblocks.io`. В облачной песочнице агента этот адрес должен быть в списке разрешённых
  сайтов (как для скилла appblocks). Ошибка сертификата на Windows: `pip install truststore`.
- Ключ AppBlocks для сборки не нужен; если задан `APPBLOCKS_API_KEY`, он передаётся.

**Правило согласия.** Облачная сборка отправляет весь проект на сервер Tibbo. Перед первой облачной сборкой в разговоре
спроси пользователя одной фразой («Собрать проект облачным компилятором Tibbo? Файлы проекта уйдут на сервер
AppBlocks.») и запускай с `--cloud-ok` только после «да». Если пользователь отказался - только `tibbo_lint.py`, и
честно напиши, что компиляции не было. Чужой проект (заказчика) без явного разрешения в облако не отправляй.

## 2. Проект TIDE (.tpr)

INI-файл; пробелы вокруг `=` допустимы (старые проекты пишут `platform = EM2000W`).

```ini
[project]
platform=TPP3W(G2)        ; точное имя платформы - папка в TIDE\Platforms
src_lib_ver=2_01_05       ; версия библиотек Tibbo: TIDE\Platforms\src\<версия>
output=app.tpc            ; имя результата
debug=on                  ; on - отладочный .tpc (ждёт TIDE), off - рабочий
defines= /dOBJECT_FD=FD_ENABLED   ; дополнительные #define проекта
transport=udp_broadcast   ; как TIDE ищет устройство: udp_broadcast | udp_winpcap
[address1]
address=0.36.119.87.32.2  ; адрес выбранного устройства (MAC в виде десятичных байт через точку)
[file1]
path=main.tbs             ; файл проекта
type=basic                ; basic | header | c | binary | xtext ...
location=                 ; пусто/без файла в папке - файл библиотеки из TIDE\Platforms\src\<src_lib_ver>
```

- Файлы библиотек подключаются двумя способами: копией в проекте (`libraries/sock/sock.tbs`, так делает AppBlocks) или
  путём внутрь TIDE (`sock\trunk\sock.tbs` при `src_lib_ver`). Облачный компилятор и `tmake` находят оба.
- В TIDE этого компьютера лежат версии библиотек 0_00 … 2_01_05; новые проекты - `2_01_05`.
- Файл, которого нет в `[fileN]`, в сборку не попадёт, даже если лежит в папке (кроме `include` из исходников).

## 3. Сборка

`tibbo_build.py` выбирает способ сам: есть TIDE - локально (`tmake.exe`), нет - облако (после согласия).

```text
python3 scripts/tibbo_build.py <папка проекта или .tpr>            # как задано в .tpr (debug on/off)
python3 scripts/tibbo_build.py <проект> --release --out app.tpc    # рабочая прошивка
python3 scripts/tibbo_build.py <проект> --cloud --cloud-ok          # принудительно облако
python3 scripts/tibbo_build.py <проект> --json                      # ошибки списком для разбора
```
Коды выхода: 0 - собрано, 1 - ошибки компилятора, 2 - неверный ввод, 3 - нет способа сборки или согласия, 4 - сеть.
`--release`/`--debug` не меняют проект пользователя: локально сборка идёт во временной копии.
Файлы в старой кодировке (cp1251, Big5 в комментариях) уходят в облако байт в байт, как их читает TIDE.
Облачная сборка проверена на 15 проектах tibbotech (TPP2W/TPP3W G2 и G3, EM2000W, EM500W; BASIC и C).
Локальная (`tmake`) и загрузка (`tupload`) собраны по справке самих программ и **ещё не проверены на Windows**.

Командная строка TIDE (Windows), если нужно вызвать вручную:
```text
"%TIDE%\Bin\tmake.exe" project.tpr -p"%TIDE%\Platforms" -r
```
Ключи tmake (пишутся слитно с путём: `-pC:\...`): `-p` папка платформ (в ней `lib` и платформы), `-b` папка двоичных файлов, `-r` полная пересборка (Rebuild All), `-l` версия
библиотек вместо `src_lib_ver`, `-j` число потоков, `-w` без предупреждений, `-v` подробно, `-m` расход памяти.

**Debug и release.** Debug-`.tpc` после загрузки не запускается сам: ждёт команд TIDE (Run, шаги, точки останова).
Release-`.tpc` запускается сразу после загрузки и при каждом включении, отладка в нём выключена. Устройство «молчит»
после загрузки - первым делом проверь, не debug ли это.

**Предупреждения.** `C1006 preprocessor redefinition of 'OBJECT_FD'` и подобные из `Platforms\<платформа>\*.tph`
появляются, когда `defines=` проекта повторяет то, что уже задано платформой: безвредны. Остальные предупреждения читай.

## 4. Загрузка в устройство (Windows + TIDE)

```text
python3 scripts/tibbo_build.py --upload app.tpc --target 0.36.119.87.32.2 --yes          # по сети (UDP)
python3 scripts/tibbo_build.py --upload app.tpc --target COM3 --serial --yes             # по COM-порту
```
Под капотом: `tupload.exe --loader taiko.udpdevice|taiko.serialdevice --target <адрес> --app <файл>`; ещё есть
`--no-build-id-check` (загрузить, даже если такая сборка уже стоит) и `--no-platform-version-check`.
- Адрес по сети - MAC устройства десятичными байтами через точку, как в `address=` проекта и в Device Explorer TIDE.
- **Перед загрузкой** спроси пользователя: какое устройство, что на нём сейчас работает (загрузка останавливает
  программу и меняет поведение выходов - реле, двигатели). Без `--yes` скрипт не загружает.
- Загрузка по сети и по COM-порту через `tupload` из скилла **пока не проверена на устройстве**: при первой загрузке
  попроси пользователя убедиться в результате (Device Explorer, поведение устройства) и сообщи разработчикам скилла.

## 5. Сообщения компилятора: причина и что делать

Формат: `файл(строка): error C1013: текст`. Номер строки - в файле из начала сообщения; ошибки в
`Platforms\...` обычно значат неверную платформу или `defines`. Исправляй **первую** ошибку и собирай заново:
следующие часто её следствие.

| Сообщение | Причина в Tibbo | Что делать |
|---|---|---|
| `'X' is not member of 'sock' object` (C1013) | Выдуманное или опечатанное свойство/метод объекта TiOS, или его нет на этой платформе. | `tibbo_lint.py --platform` подскажет похожее имя; сверить с tios-api.md. |
| `'X' is not member of 'T'` | Нет такого поля в структуре `type`. | Проверить объявление `type ... end type`. |
| `undeclared identifier 'X'` | Не подключён `.tbh` библиотеки, опечатка, константа не той платформы, нет `declare`. | `include` нужного заголовка, файл в `[fileN]` проекта, `PL_*` из platforms.md. |
| `identifier 'X' is not constant, variable, property or function` | Имя занято чем-то другим (тип, метка) или не объявлено. | Переименовать, проверить объявление. |
| `unable to find include file 'X'` | Файла нет в проекте или нет такой версии библиотек. | Добавить файл в проект / проверить `src_lib_ver` и путь. |
| `platform does not export 'X' syscall` | Функции нет на этой платформе (например, на G2 нет того, что есть на G3). | Другая функция или другая платформа; см. platforms.md. |
| `recursive calls are not supported` | Рекурсия (в т.ч. через цепочку процедур). | Переписать циклом или очередью. |
| `string capacity must not exceed 255` | `dim s as string(300)`. | Строка ≤ 255; длинные данные - буферы/массивы байт. |
| `type mismatch - unable to copy 'A' into 'B'` | Присваивание несовместимых типов (строка в число и т.п.). | Явное преобразование: `str()`, `val()`, `lval()`. |
| `type mismatch - unable to perform ... with 'X'` | Арифметика/сравнение с неподходящим типом. | Привести типы. |
| `argument count mismatch for 'X'` / `function 'X' does not take N arguments` | Не то число аргументов. | Сверить с объявлением или tios-api.md. |
| `function 'X' byref argument type mismatch` | В `byref` передан другой тип. | Передать переменную нужного типа. |
| `argument 'X' mismatches previous declaration` / `retval of function 'X' mismatches previous declaration` | `declare` и тело расходятся. | Синхронизировать `declare` и реализацию. |
| `function 'X' previously declared as subroutine, now is seen as function` (и наоборот) | `declare sub` vs `function`. | Привести к одному виду. |
| `functions must have return values` / `subroutines cannot have return values` | `function` без `as тип` или `sub` с `as тип`. | Исправить объявление. |
| `subroutines cannot be used in expressions` / `subroutine cannot be r-value` | `x = my_sub()`. | Сделать `function` или вызвать отдельно. |
| `event handlers cannot be called` | Прямой вызов `on_sock_event(...)` и т.п. | Вынести код в отдельную процедуру и вызывать её. |
| `'X' is already defined` / `redefinition of identifier 'X'` | Двойное объявление: две копии библиотеки, `dim` в .tbh без `#ifndef`, одинаковые имена. | Убрать дубликат; глобальные `dim` - в одном .tbs, в .tbh - `declare`. |
| `'X' already has body` | Процедура определена дважды (часто два одинаковых обработчика событий). | Объединить обработчики; библиотеки звать через `*_proc_*`. |
| `property 'X' is read-only` / `write-only` | Запись в свойство только для чтения (например, `sock.state`). | Нужен метод (`sock.connect`, `sock.close`). |
| `on the left of '=' there must be a variable or a property` | Присваивание константе или выражению. | Исправить левую часть. |
| `array index 'N' is out of bounds` | Индекс константой вне массива. | Проверить размер `dim a(N)` (индексы с 0). |
| `constant expression expected` / `constant numeric expression expected` | В размере массива/строки или `case` не константа. | `const`/`#define`. |
| `integer constant is too big` / `floating-point constant is too big` | Число вне диапазона типа. | Другой тип (`dword`, `real`). |
| `invalid expression (unexpected 'X')` / `'X' expected` / `identifier expected` | Синтаксис: незакрытая скобка, `elseif`, лишний символ. | Проверить строку выше; `else if` раздельно. |
| `newline in constant` | Незакрытая строка `"`. | Закрыть кавычку. |
| `matching '#endif' not found` / `unexpected '#endif'` | Непарные `#if/#endif`. | Проверить препроцессор. |
| `preprocessor loop detected` / `include depth limit exceeded` | Взаимные `include`. | Защитные `#ifndef` или убрать цикл. |
| `division or modulo by zero` | Деление на константу 0. | Исправить выражение. |
| Компоновщик: `Compiled binary file is too large to fit on currently selected target` | Программа больше ROM платформы. | Убрать неиспользуемые библиотеки, ресурсы, вывод отладки; платформа с большей памятью. |
| Компоновщик: `Your project requires more variable memory (RAM) than available` | Глобальные переменные не влезают в RAM. | Уменьшить массивы и строки (`string(32)` вместо 255), буферы; см. память платформы в platforms.md. |
| `Unable to find library 'X'` | Нет версии библиотек `src_lib_ver` в этом TIDE. | Указать установленную версию (`-l` или правка `.tpr`). |

Полный список текстов сообщений взят из компилятора TIDE (`tbc.exe`); номера `C####` компилятор ставит сам.

## 6. Работа в окне TIDE

Для людей и для агентов, которые управляют компьютером. Порядок для проверки прошивки на устройстве:
1. **Device Explorer** (панель TIDE) - найти устройство в сети, выбрать его как цель (Set as target). Устройство и
   компьютер - в одной сети; при `udp_winpcap` нужен WinPcap/Npcap.
2. **Build → Rebuild All** - полная сборка; ошибки - в панели Output, двойной щелчок ведёт к строке.
3. **Debug → Run (F5)** - собрать, загрузить и запустить. Debug-сборка управляется из TIDE: пауза, шаги, точки
   останова, просмотр переменных (Watch).
4. Рабочая прошивка: в Project Settings переключить на Release, **Build → Rebuild All and Upload**.
5. Прошивка вместе с TiOS одним файлом для производства - см. docs.tibbo.com/guide_tide_releasing.

Агенту с управлением компьютером: сначала собери `tibbo_build.py` (быстро, текстом), в окно TIDE переходи для загрузки,
отладки и того, чего нет в командной строке. Любую загрузку в устройство - только после «да» пользователя.
