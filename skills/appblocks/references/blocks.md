# Блоки логики AppBlocks: порты, параметры, настройки

Снято из реестра редактора app.appblocks.io (2026-11-10): 177 типов блоков, из них 132 в палитре и 45 скрытых (служебные и устаревшие, встречаются в старых проектах).
Машинная версия - `data/registry.json` (её использует `ab_tool.py check` и `ab_tool.py lookup`). Пересборка: `scripts/extract_registry.js` в браузере на app.appblocks.io, затем `scripts/build_registry.py`.

**Среда исполнения.** Блоков только для Zephyr - 53 (по разделам палитры: Math - 10, Inputs & I/O - 9, Data & Storage - 7, Strings - 7, Network - 6, Control - 6, Display - 3, Camera - 3, Sound & LED - 2): в столбце «Особенности» у них стоит «только Zephyr». **В проект на TiOS их ставить нельзя** - генератор кода AppBlocks отвечает на такой проект ошибкой 500 без объяснений (проверено блоками Square Root и String Trim); `ab_tool.py check` находит это заранее. «нужно: X» - что должно быть у платы или в проекте (camera, touch, network, TPP ...).

Как читать: **Входы/Выходы** - `portId` для `node_link` (SOURCE_PORT/TARGET_PORT) и параметры, которые порт передаёт следующему блоку (`{{$имя}}`) или принимает в ARGUMENTS (TARGETPARAM). **Настройки** - поля `settings` узла: `ID`→ref - ID элемента этого типа (variable, timer, tbl_table…), [варианты] - допустимые значения (`значение=подпись`), =… - значение по умолчанию. Общие поля (ID, DISPLAY_NAME, X, Y, GROUP, INPUTS, OUTPUTS, ARGUMENTS) не повторяются. **ASYNC** - после блока параметры предыдущих блоков недоступны (editor.md §4). Feature - сервис, который должен быть включён в проекте.

## System

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_system` | On Boot | - | `boot`(boot_reason:integer) | - |  |  |
| `node_debug` | Debug Print | `sys.debugprint`(printstring:string) | `done` | - |  |  |
| `node_label` | Comment | - | - | - |  |  |
| `node_system_reboot` | Reboot | `sys.reboot` | - | - |  |  |
| `node_upgrade_firmware` | Firmware Upgrade | `upgrade_start`(URL:string) | `done` | - |  | нужно: TPP |

## Variables

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_variable_changed` | On Variable Changed | - | `variable_changed` | `VARIABLE`→variable |  |  |
| `node_variable_set` | Variable Set/Math | `set_value`(value:custom) | `variable_set_done` | `VARIABLE`→variable | global_vars |  |

## Logic & Flow

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_command_triggered` | On Command | - | `on_command_triggered`(data:string) | `COMMAND`→command | commands |  |
| `node_comparison` | IF Condition | `comp`(operand1:custom, operator:custom, operand2:custom) | `true_output`, `false_output` | - |  | operator (аргумент): `=`, `<>`, `<`, `<=`, `>`, `>=`; для tios текст уходит в BASIC как есть, `==`/`!=` там нет [генерация 2026-10-22] |
| `node_compound_condition` | IF Compound Condition | `cond` | `true_output`, `false_output` | `EXPRESSIONS`→condition_expression; `OPERATOR` [AND\|OR] =AND |  |  |
| `node_switch` | Switch | `switch_exec` | `switch_default` | `VALUE` stringvariable; `CASES`→node_switch_case |  | порты задаёт проект |
| `node_forloop` | For-Next Loop | `for_loop`(start:dword, end:dword) | `for_loop_iterate`(current_iteration:dword), `for_loop_done` | - |  |  |
| `node_command_trigger` | Execute Command | `command_trigger`(data:string) | `done` | `COMMAND`→command | commands | ASYNC |

## Math

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_arithmetic` | Calculate | `exec`(operand1:custom, operator:custom, operand2:custom) | `answer`(result:float) | `VARIABLE`→variable |  |  |
| `node_bitwise` | Bitwise | `exec` | `answer`(result:integer) | `OPERAND1` stringvariable; `OPERATOR` [AND\|OR\|XOR\|SHL=Left Shift (<<)\|SHR=Right Shift (>>)]; `OPERAND2` stringvariable |  |  |
| `node_math_compound` | Custom Function | `set_value` | `math_done` | `VARIABLE`→variable; `FUNCNAME` name =custom_function; `CODE` code |  | порты задаёт проект; CODE становится телом `function <FUNCNAME>() as string`, блок вызывает её; доступны процедуры фреймворка (например `signal_strength_set`) [генерация 2026-10-22; TIDE не проверен] |
| `node_random` | Random | `exec`(min:integer, max:integer) | `answer`(result:integer) | `VARIABLE`→variable |  | ASYNC |
| `node_trig` | Trigonometry | `exec`(angle:float) | `answer`(result:float) | `VARIABLE`→variable; `FUNCTION` [sin=Sine\|cos=Cosine\|tan=Tangent] =sin; `UNIT` [rad=Radians\|deg=Degrees] =rad |  | только Zephyr |
| `node_inverse_trig` | Inverse Trigonometry | `exec`(value:float) | `answer`(result:float) | `VARIABLE`→variable; `FUNCTION` [asin=Arcsine\|acos=Arccosine\|atan=Arctangent] =asin; `UNIT` [rad=Radians\|deg=Degrees] =rad |  | только Zephyr |
| `node_atan2` | Atan2 | `exec`(y:float, x:float) | `answer`(result:float) | `VARIABLE`→variable; `UNIT` [rad=Radians\|deg=Degrees] =rad |  | только Zephyr |
| `node_power` | Power | `exec`(base:float, exponent:float) | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_sqrt` | Square Root | `exec`(value:float) | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_hypot` | Hypotenuse | `exec`(x:float, y:float) | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_log` | Logarithm / Exponential | `exec`(value:float) | `answer`(result:float) | `VARIABLE`→variable; `FUNCTION` [ln=Natural log (ln)\|log10=Log base 10\|log2=Log base 2\|exp=e to the power (exp)] =ln |  | только Zephyr |
| `node_min_max` | Min / Max | `exec`(a:float, b:float) | `answer`(result:float) | `VARIABLE`→variable; `FUNCTION` [min=Minimum\|max=Maximum] =min |  | только Zephyr |
| `node_rounding` | Rounding | `exec`(value:float) | `answer`(result:float) | `VARIABLE`→variable; `FUNCTION` [round=Round to nearest\|floor=Round down (floor)\|ceil=Round up (ceiling)\|trunc=Drop the fraction (truncate)] =round |  | только Zephyr |
| `node_math_abs` | Absolute Value | `exec`(value:float) | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |

## Control

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_pid` | PID Controller | `exec`(setpoint:float, measurement:float, kp:float, ki:float, kd:float, deriv_tau:float, out_min:float, out_max:float), `reset` | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_clamp` | Clamp | `exec`(value:float, min:float, max:float) | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_map_scale` | Map / Scale | `exec`(value:float, in_min:float, in_max:float, out_min:float, out_max:float) | `answer`(result:float) | `VARIABLE`→variable; `CLAMP` boolean =1 |  | только Zephyr |
| `node_hysteresis` | Hysteresis | `exec`(value:float, low:float, high:float), `reset` | `answer`(result:float) | `VARIABLE`→variable; `INVERT` boolean =0 |  | только Zephyr |
| `node_lowpass_filter` | Low-pass Filter | `exec`(value:float, tau:float), `reset` | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |
| `node_rate_limiter` | Rate Limiter | `exec`(target:float, rise_rate:float, fall_rate:float), `reset` | `answer`(result:float) | `VARIABLE`→variable |  | только Zephyr |

## Time & Scheduling

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_timer_completed` | On Timer Completed | - | `timer_complete` | `TIMER`→timer | timers |  |
| `node_time_interval` | On Time Period | - | `timer_tick` | `INTERVAL` number =1 (0.1..65535) |  | срабатывает каждые N+1 тиков по 10 мс: 0,5 с -> 0,51 с (generated-code.md) [генерация 2026-10-22] |
| `node_cron_event` | On Scheduled Event | - | `cron_expired` | `SCHEDULE`→crontab | cron | только TiOS, Zephyr |
| `node_timer_start` | Timer Start | `timer_start`(time:word) | `done` | `TIMER`→timer; `REPEAT` [false=No\|true=Yes] =false |  |  |
| `node_timer_stop` | Timer Stop | `timer_stop` | `done` | `TIMER`→timer |  |  |
| `node_time_delay` | Delay (seconds) | `delay_start` | `delay_elapsed` | `DURATION` stringvariable =1 (0.1..65535) |  | ASYNC |
| `node_datetime` | Get Current DateTime | `timestamp_get` | `timestamp_now`(time_now:datetime) | - |  |  |
| `node_datetime_format` | DateTime/Time Formatter | `time_format`(time_variable:datetime) | `time_str`(time_str:string) | `FORMAT` =YYYY-MM-DD hh:mm:ss tt |  |  |

## Inputs & I/O

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_button_input_pressed` | On Button Pressed | - | `on_button_pressed` | `BUTTON`→button |  | нужно: button |
| `node_button_input_released` | On Button Released | - | `on_button_released` | `BUTTON`→button |  | нужно: button |
| `node_lcd_button` | On LCD Button | - | `on_lcd_button_pressed`, `on_lcd_button_released` | `WIDGET`→lcd_button_widget | display_lib | только Zephyr |
| `node_lcd_checkbox` | On LCD Checkbox Changed | - | `on_lcd_checkbox`(checked:integer) | `WIDGET`→lcd_checkbox_widget | display_lib | только Zephyr; нужно: touch |
| `node_lcd_switch` | On LCD Switch Changed | - | `on_lcd_switch`(on:integer) | `WIDGET`→lcd_switch_widget | display_lib | только Zephyr; нужно: touch |
| `node_lcd_arc` | On LCD Arc Changed | - | `on_lcd_arc`(value:integer) | `WIDGET`→lcd_arc_widget | display_lib | только Zephyr; нужно: touch |
| `node_lcd_dropdown` | On LCD Dropdown Selected | - | `on_lcd_dropdown`(index:integer) | `WIDGET`→lcd_dropdown_widget | display_lib | только Zephyr; нужно: touch |
| `node_lcd_roller` | On LCD Roller Selected | - | `on_lcd_roller`(index:integer) | `WIDGET`→lcd_roller_widget | display_lib | только Zephyr; нужно: touch |
| `node_lcd_spinbox` | On LCD Spinbox Changed | - | `on_lcd_spinbox`(value:integer) | `WIDGET`→lcd_spinbox_widget | display_lib | только Zephyr; нужно: touch |
| `node_keypad` | On Button Pressed | - | `on_kp` | `BUTTON` |  | нужно: TPP |
| `node_keypad_released` | On Button Released | - | `on_kp_released` | `BUTTON` |  | нужно: TPP |
| `node_button` | On MD Button Pressed | - | `on_button_pressed` | - |  | нужно: md_button |
| `node_button_released` | On MD Button Released | - | `on_button_released`(pressed_time:byte) | - |  | нужно: md_button |
| `node_interrupt` | On Interrupt | - | `on_io_int`(intcount:word) | `INTLINE` |  | только TiOS, Zephyr |
| `node_wiegand` | On Wiegand | - | `data_available`(wiegand_data:string, facility_code:string, card_code:string, id_code:string) | `TIBBIT`→tibbit_08; `FORMAT` [binary=Binary\|hex=Hex\|dec=Decimal] =binary |  | нужно: TPP |
| `node_ir_received` | On IR Received | - | `ir_received`(data:string) | `IR_PORT` |  | только Zephyr |
| `node_digital_line_set` | Digital Line Set | `digital_line_set` | `done` | `LINE_NUMBER` stringvariable; `VALUE` [1=HIGH\|0=LOW] =0 |  | LINE_NUMBER - номер линии числом (`48`), не имя константы: в код идёт `io.lineset("48", "0")` в кавычках; `PL_IO_NUM_48` даст строку, которая при преобразовании в число станет 0. Линию в выход блок не переводит (generated-code.md) [генерация 2026-10-22; TIDE и железо не проверены] |
| `node_ir_send` | IR Send | `ir_send`(data:string) | `done` | `IR_PORT` |  | только Zephyr |

## Strings

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_num_round` | Number Round Decimal Points | `round` | `result`(result_str:string) | `INPUT` stringvariable; `DECIMAL_PLACES` number =0 |  | только TiOS, Zephyr |
| `node_number_to_fixed` | Number To Fixed | `tofixed` | `result`(result_str:string) | `INPUT` stringvariable; `DECIMAL_PLACES` number =2 |  | только Zephyr |
| `node_string_index_of` | String Index Of | `find` | `result`(index:integer) | `INPUT` stringvariable; `SEARCH` stringvariable; `START` number =0 |  | только Zephyr |
| `node_string_substring` | Substring | `substring` | `result`(result_str:string) | `INPUT` stringvariable; `START` number =0; `MODE` [end=To End of String\|length=Fixed Length] =end; `LENGTH` number =1 |  | только Zephyr |
| `node_string_trim` | String Trim | `trim` | `result`(result_str:string) | `INPUT` stringvariable; `MODE` [both=Both Ends\|start=Start Only\|end=End Only] =both |  | только Zephyr |
| `node_string_pad` | String Pad | `pad` | `result`(result_str:string) | `INPUT` stringvariable; `DIRECTION` [start=Start (Pad Start)\|end=End (Pad End)] =start; `LENGTH` number =0; `PAD_CHAR` stringvariable =  |  | только Zephyr |
| `node_string_replace` | String Replace | `replace` | `result`(result_str:string) | `INPUT` stringvariable; `SEARCH` stringvariable; `REPLACE` stringvariable; `MODE` [all=All Occurrences\|first=First Occurrence Only] =all |  | только Zephyr |
| `node_base64` | Base64 | `convert` | `result`(result_str:string) | `INPUT` stringvariable; `MODE` [encode=Encode\|decode=Decode] =encode |  | только Zephyr |

## Display

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_lcd_set_screen` | LCD Set Screen | `set_screen` | `done` | `SCREEN`→display_screen | display_lib | только TiOS, Zephyr |
| `node_lcd_menu` | Enter LCD Menu | `lcd_menu_enter` | `done` | - | display_lib | нужно: TPP2W(G2) или TPP2W(G3) или lcd_menu |
| `node_lcd_text_widget` | LCD Text Widget | `lcd_print_text`(text:string) | `done` | `WIDGET`→lcd_text_widget; `VISIBLE` [1=Visible\|0=Hidden] =1 | display_lib |  |
| `node_lcd_image_widget` | LCD Image Widget | `lcd_image` | `done` | `WIDGET`→lcd_image_widget; `IMG`→lcd_image; `IMAGE_BUFFER` | display_lib | только TiOS, Zephyr |
| `node_lcd_set_widget_property` | LCD Set Widget Property | `lcd_set_widget_property`(value:string) | `done` | `WIDGET`; `PROPERTY` | display_lib | только Zephyr |
| `node_lcd_graph_widget` | LCD Line Graph Add Point | `lcd_print_line` | `done` | `WIDGET`→lcd_graph_widget; `VALUE` stringvariable; `VALUE_2` stringvariable; `VALUE_3` stringvariable; `VALUE_4` stringvariable |  |  |
| `node_lcd_graph_widget_clear` | LCD Line Graph Clear | `lcd_graph_clear` | `done` | `WIDGET`→lcd_graph_widget |  |  |
| `node_lcd_chart_load_table` | LCD Line Graph Load From Table | `lcd_chart_load` | `done` | `WIDGET`→lcd_graph_widget; `SERIES_SOURCES`→lcd_chart_series_source; `TIME_RANGE` stringvariable =3600; `END_TIME` stringvariable; `X_LABELS` [HH:mm=Hours and minutes\|HH:mm:ss=Hours, minutes and seconds\|MM/DD=Month/Day\|MM/DD HH:mm=Month/Day Hours:minutes\|=None] =HH:mm |  | ASYNC; только Zephyr |
| `node_lcd_snapshot` | LCD Screenshot | `lcd_snapshot` | `done` | `FILENAME` =lcd_screenshot; `QUALITY` [JPEGE_Q_BEST=Best (largest file)\|JPEGE_Q_HIGH=High\|JPEGE_Q_MED=Medium\|JPEGE_Q_LOW=Low (smallest file)] =JPEGE_Q_HIGH | lcd | только Zephyr |

## Camera

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_camera_frame` | On Camera Frame | - | `camera_frame`(frame:buffer, width:word, height:word, size:dword, seq:dword) | `MAX_FPS` number =5 (..30) | camera_sensor | только Zephyr; нужно: camera |
| `node_camera_capture` | Capture Frame | `camera_capture` | `captured`(frame:buffer, width:word, height:word, size:dword, seq:dword), `failed` | `TIMEOUT` number =500 (..10000) | camera_sensor | только Zephyr; нужно: camera |
| `node_camera_set_property` | Set Camera Property | `camera_set_property`(value:integer) | `done`, `failed` | `PROPERTY` | camera_sensor | только Zephyr; нужно: camera |

## Sound & LED

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_pat` | LED Pattern | `pat.play`(patternstring:string) | `done` | `CANINT` [PL_PAT_NOINT=Cannot Interrupt\|PL_PAT_CANINT=Can Interrupt] =PL_PAT_CANINT |  |  |
| `node_beep` | Buzzer Pattern | `beep.play`(patternstring:string) | `done` | `CANINT` [PL_PAT_NOINT=Cannot Interrupt\|PL_PAT_CANINT=Can Interrupt] =PL_PAT_CANINT; `FREQ` stringvariable =2700 |  | только TiOS, Zephyr; нужно: TPP |
| `node_play_sound` | Play Audio File | `play_sound` | `done` | `FILEPATH` stringvariable =/SD:/; `LOOP` boolean =0; `VOLUME` number =100 (..100) |  | ASYNC; только Zephyr; нужно: audio_out |
| `node_stop_sound` | Stop Audio | `stop_sound` | `done` | - |  | только Zephyr; нужно: audio_out |
| `node_tibbit_26_start` | Tibbit 26 Start | `tbt26_start_recording` | `done` | `TIBBIT`→tibbit_26 |  |  |
| `node_tibbit_26_end` | Tibbit 26 End Recording | `tbt26_get_data` | `tibbit26_data`(data:string) | `TIBBIT`→tibbit_26 |  |  |
| `node_tibbit_26_send` | Tibbit 26 Send | `tbt26_play_back`(data:string) | `done` | `TIBBIT`→tibbit_26 |  |  |

## Data & Storage

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_table` | Table Lookup | `tbl_record_find`(field_value:string, find_index:byte) | `done`, `tbl_record_found`(row_index:word, <поля таблицы>), `tbl_record_not_found` | `TABLE`→tbl_table; `WRAPAROUND` [0=Disabled\|1=Enabled] =0; `FIELD_NAME`; `OPERATOR` [PL_FD_FIND_EQUAL=Equals\|PL_FD_FIND_NOT_EQUAL=Not Equal\|PL_FD_FIND_GREATER=Greater Than\|PL_FD_FIND_GREATER_EQUAL=Greater Than Equal To\|PL_FD_FIND_LESSER=Less Than\|PL_FD_FIND_LESSER_EQUAL=Less Than Equal To] == |  | только TiOS, Zephyr |
| `node_table_lookup_v2` | Table Lookup Compound | `tbl_record_find`(find_index:byte) | `done`, `tbl_record_found`(row_index:word, <поля таблицы>), `tbl_record_not_found` | `TABLE`→tbl_table; `WRAPAROUND` [0=Disabled\|1=Enabled] =0; `QUERY_TERMS`→table_update_query_term |  | только Zephyr |
| `node_table_insert` | Table Insert Row | `tbl_add` | `done` | `TABLE`→tbl_table |  | только TiOS, Zephyr |
| `node_table_update` | Table Update Row | `tbl_update` | `done` | `TABLE`→tbl_table; `FIELD_NAME`; `OPERATOR` [PL_FD_FIND_EQUAL=Equals\|PL_FD_FIND_NOT_EQUAL=Not Equal\|PL_FD_FIND_GREATER=Greater Than\|PL_FD_FIND_GREATER_EQUAL=Greater Than Equal To\|PL_FD_FIND_LESSER=Less Than\|PL_FD_FIND_LESSER_EQUAL=Less Than Equal To] ==; `VALUE` stringvariable; `FIELDS`→table_update_field_value |  | только TiOS, Zephyr |
| `node_table_update_v2` | Table Update Row Compound | `tbl_update` | `done` | `TABLE`→tbl_table; `QUERY_TERMS`→table_update_query_term; `FIELDS`→table_update_field_value |  | только Zephyr |
| `node_table_delete` | Table Delete Row | `tbl_delete` | `done` | `TABLE`→tbl_table; `FIELD_NAME`; `OPERATOR` [PL_FD_FIND_EQUAL=Equals\|PL_FD_FIND_NOT_EQUAL=Not Equal\|PL_FD_FIND_GREATER=Greater Than\|PL_FD_FIND_GREATER_EQUAL=Greater Than Equal To\|PL_FD_FIND_LESSER=Less Than\|PL_FD_FIND_LESSER_EQUAL=Less Than Equal To] ==; `VALUE` stringvariable |  | только TiOS, Zephyr |
| `node_table_clear` | Clear Table | `tbl_clear` | `done` | `TABLE`→tbl_table |  | только TiOS, Zephyr |
| `node_table_row_count` | Table Row Count | `tbl_count` | `tbl_count_result`(rows:word) | `TABLE`→tbl_table |  | только TiOS, Zephyr |
| `node_log_add` | Add to Event Log | `add_to_log` | `done` | `PAIRS`→log_key_value | log | только TiOS, Zephyr |
| `node_settings_init` | Initialize Settings | `stg_init` | `done` | - |  |  |
| `node_json_get_string` | JSON Get String | `json_get_string` | `value_output`(json_value:string) | `JSON_STRING` stringvariable; `KEY` stringvariable |  |  |
| `node_luis` | LUIS On/Off | `luis_enable`(on_off:boolean) | `done` | - | luis | только TiOS, Zephyr; нужно: bluetooth |
| `node_file_write` | Write File | `file_write` | `done`(size:dword), `failed`(error:integer) | `BUFFER`; `PATH` stringvariable =/lfs/capture.jpg; `MODE` [overwrite=Overwrite\|append=Append] =overwrite | fd | только Zephyr |
| `node_buffer_from_text` | Text to Buffer | `buffer_from_text` | `done`(text_buffer:buffer) | `TEXT` stringvariable |  | только Zephyr |
| `node_buffer_jpeg` | JPEG | `jpeg_convert` | `done`(jpeg:buffer, size:dword), `failed` | `MODE` [encode=Encode (RGB565 to JPEG)\|decode=Decode (JPEG to RGB565)] =encode; `BUFFER`; `QUALITY` [JPEGE_Q_BEST=Best\|JPEGE_Q_HIGH=High\|JPEGE_Q_MED=Medium\|JPEGE_Q_LOW=Low] =JPEGE_Q_HIGH; `MAX_SIZE` number =32768 (4096..131072); `SCALE` [fit=Fit Max Image Size\|0=Full size\|1=1/2\|2=1/4\|3=1/8] =fit; `MAX_IMAGE_SIZE` number =38400 (1024..1048576) |  | только Zephyr |
| `node_buffer_collect` | Collect Buffer | `collect_append`, `collect_finish`, `collect_clear` | `finished`(collected:buffer, size:dword), `overflow` | `BUFFER`; `MAX_SIZE` number =4096 (16..262144); `FORMAT` [=Same as appended\|bytes=Bytes\|text=Text\|jpeg=JPEG image] |  | только Zephyr |
| `node_disk_usage` | Disk Usage | `disk_usage_get` | `disk_usage_result`(total_kb:dword, used_kb:dword, free_kb:dword, used_percent:byte), `disk_usage_error`(error_code:integer) | `MOUNT_POINT` [/lfs] =/lfs |  | только Zephyr |

## Serial & SMS

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_ser_data_arrival` | On Serial Data Received | - | `data_available`(data:string, complete_data:string, bytes:buffer) | `SERIAL_PORT`; `MODE` [0=Raw Data\|1=Packet] =0; `PACKET_START`; `PACKET_END` |  | только TiOS, Zephyr |
| `node_sms_recv` | On SMS Received | - | `sms_received`(phone_number:string, message:string) | - | cell |  |
| `node_ser_data_send` | Serial Data Send | `data_send` | `done` | `SERIAL_PORT`; `DATA` stringvariable; `SEND_BUFFER` |  | только TiOS, Zephyr |
| `node_sms_send` | Send SMS | `data_send` | `done` | `NUMBER` stringvariable (1..); `DATA` stringvariable (..160) | cell |  |

## Network

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_network_changed` | On Network Changed | - | `network_changed` | `NETWORK_TYPE` [1=Ethernet\|2=WiFi\|3=Cellular] =1; `NETWORK_EVENT` [1=Connected\|0=Disconnected] =1 |  | нужно: network |
| `node_socket_data_arrival` | On Socket Data Received | - | `sock_data_arrival`(data:string) | `SOCKET`→socket_connection | socket | только TiOS, Zephyr |
| `node_socket_event` | On Socket Connection Event | - | `sock_connection_event`(ipaddress:string) | `SOCKET`→socket_connection; `EVENT_TYPE` [CONNECTED=Connected\|DISCONNECTED=Disconnected] =CONNECTED | socket | только TiOS, Zephyr |
| `node_http_server_endpoint` | On HTTP Request | - | `http_requested`(data:string) | `ENDPOINT`→http_server_endpoint | httpserver | нужно: network |
| `node_snmp_object_set` | On SNMP Object Set | - | `snmp_object_set`(value:string) | `OBJECT`→snmp_object | snmp_agent | только Zephyr |
| `node_socket_connect` | Socket Connect | `connect` | `done` | `SOCKET`→socket_connection | socket | только TiOS, Zephyr |
| `node_socket` | Socket Send | `sock_send` | `done` | `SOCKET`→socket_connection; `DATA` stringvariable |  |  |
| `node_http` | HTTP Request | `http_request_start`(data:string) | `http_data_arrival`(data:string, bytes:buffer), `http_complete`, `http_error`(error_message:string) | `URL` stringvariable; `METHOD` [HTTP_GET=GET\|HTTP_HEAD=HEAD\|HTTP_POST=POST\|HTTP_PUT=PUT\|HTTP_DELETE=DELETE\|HTTP_PATCH=PATCH] =HTTP_GET; `BODY_BUFFER`; `HEADERS`→http_header; `CERTIFICATEFILE` file (..102400) | http | ASYNC; нужно: network |
| `node_http_server_response` | HTTP Response | `http_response` | `done` | `STATUS_CODE` stringvariable =200; `RESPONSE_DATA` stringvariable | httpserver | нужно: network |
| `node_http_respond_buffer` | Respond with Buffer | `respond_buffer` | `done` | `BUFFER` | httpserver | только Zephyr; нужно: network |
| `node_snmp_set_value` | Set SNMP Object Value | `snmp_set_value` | `done` | `OBJECT`→snmp_object; `VALUE` stringvariable | snmp_agent | только Zephyr |
| `node_snmp_get_value` | Get SNMP Object Value | `snmp_get_value` | `done`(value:string) | `OBJECT`→snmp_object | snmp_agent | только Zephyr |
| `node_snmp_send_trap` | Send SNMP Trap | `snmp_send_trap` | `done` | `DESTINATION_IP` stringvariable; `PORT` number =162 (1..65535); `COMMUNITY` =public; `TRAP_OID` =1.3.6.1.4.1.0.0.1; `OBJECT`→snmp_object | snmp_agent | только Zephyr |
| `node_smtp_send` | Send Email | `smtp_send` | `success`, `failure` | `TO` stringvariable; `SUBJECT` stringvariable; `BODY` stringvariable | smtp_client | ASYNC; только Zephyr |

## Cloud

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_mqtt_sub` | On MQTT Notification | - | `callback_mqtt_notif`(data:string, topic:string) | `TOPIC`→mqtt_topic | mqtt | нужно: network |
| `node_mqtt_change` | On MQTT Change | - | `mqtt_state_change` | `CHANGE_TYPE` [1=Connected\|0=Disconnected] =1 | mqtt_lib | нужно: network |
| `node_mqtt_pub` | MQTT Publish | `mqtt_publish`(topic:string, publish_data:string, qos:custom, retain:custom) | `done`, `ack` | `PAYLOAD_BUFFER` | mqtt | нужно: network |
| `node_azure` | Azure | - | `done` | - | azure | нужно: azure |
| `node_azure_telemetry` | Azure Telemetry | `azure_pub` | `done` | `TELEMETRY_ID`; `TELEMETRY_VALUE` stringvariable | azure |  |
| `node_azure_command` | Azure Command | - | `azure_cmd`(param:string) | `CMD`→azure_command | azure |  |
| `node_cgg_telemetry` | AppBlocks Cloud Metric | `cgg_pub`(event_name:string, publish_data:string) | `done` | - | cgg | нужно: network |

## Modbus

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_modbus_slave_register` | On Modbus Receive | - | `modbus_value`(data:float) | `REGISTER`→modbus_table_item |  | только TiOS, Zephyr |
| `node_modbus_response` | On Modbus Response | - | `response`(<параметры регистра>) | - | modbus_master | только TiOS, Zephyr |
| `node_modbus_timeout` | On Modbus Timeout | - | `response`(device_id:word, register_address:word) | - | modbus_master | только TiOS, Zephyr |
| `node_modbus_write` | Modbus Request | `modbus_poll` | `modbus_response`(response_data:word, device_id:word, register_address:word), `modbus_timeout` | `DEVICE`→modbus_device; `PROTOCOL` [modbus_TCP=TCP\|modbus_RTU=Serial] =modbus_RTU; `SERIAL_PORT`; `DEVICEIP` stringvariable =1.0.0.1; `DEVICEPORT` stringvariable =502 (..65535); `FUNCTIONCODE` [ReadCoilStatus=Read COIL/Output (0x01)\|ReadInputStatus=Read Contact/Discrete Input (0x02)\|ReadHoldingRegisters=Read Holding Register (0x03)\|ReadInputRegisters=Read Input Register (0x04)\|WriteSingleCoil=Write Single Coil (0x05)\|PresetSingleRegister=Write Single Register (0x06)] =ReadCoilStatus; `DEVICEID` stringvariable; `REGISTER_ADDRESS` stringvariable; `LENGTH` number =1 (..125); `VARTYPE` [INTEGER=Unsigned Integer\|SIGNED_INTEGER=Signed Integer\|FLOAT=Floating Point Number] =INTEGER; `ENDIAN` [BIG=Big Endian (ABCD)\|LITTLE=Little Endian (CDAB)] =BIG; `DATA` stringvariable | modbus_master | ASYNC; только TiOS, Zephyr |

## Скрытые и служебные (нет в палитре)

| Блок | Название | Входы | Выходы | Настройки | Feature | Особенности |
|---|---|---|---|---|---|---|
| `node_link` | Block Link | - | - | `SOURCE`; `SOURCE_FEATURE`; `SOURCE_PORT`; `TARGET`; `TARGET_FEATURE`; `TARGET_PORT` |  |  |
| `node_argument` | Node Argument | - | - | `ARGVALUE` dynamic; `TARGETPARAM` |  |  |
| `node_port` | Node Port | - | - | `NAME`; `PORTID`; `PARAMS`→node_parameter |  |  |
| `node_parameter` | Node Parameter | - | - | `NAME`; `DATATYPE` [byte=Byte\|integer=Integer\|short=Short\|word=Word\|long=Long\|dword=DWord\|real=Real\|float=Float\|string=String\|boolean=Boolean\|custom=Custom]; `DEFAULT` |  |  |
| `node_switch_case` | Case | - | - | `VALUE` |  |  |
| `node_group` | Tab | - | `done` | - |  | порты задаёт проект |
| `node_group_input` | Group Input | - | `output` | - |  | порты задаёт проект |
| `node_group_output` | Group Output | `input` | `done` | - |  | порты задаёт проект |
| `node_tibbit_01` | Tibbit 01 | `serial_send`(senddata:string) | `serial_data`(serdata:string) | - |  |  |
| `node_tibbit_02` | Tibbit 02 | `serial_send`(senddata:string) | `serial_data`(serdata:string) | - |  |  |
| `node_tibbit_16` | Tibbit 16 | `pwm_set` | `done` | `TIBBIT`→tibbit_16; `FREQUENCY` number =1000 (500..500000); `CHANNEL` [1=Channel 1\|2=Channel 2\|3=Channel 3] =1 |  |  |
| `node_tibbit_17` | Tibbit 17 | `pwm_set` | `done` | `TIBBIT`→tibbit_17; `FREQUENCY` number =1000 (500..500000); `CHANNEL` [1=Channel 1\|2=Channel 2\|3=Channel 3] =1 |  |  |
| `node_tibbit_39_1` | Tibbit 39_1 | `tibbit39_on_off`(state:boolean) | `done` | `TIBBIT`→tibbit_39_1 | tibbit_39_1 |  |
| `node_tibbit_39_2` | Tibbit 39_2 | `tibbit39_on_off`(state:boolean) | `done` | `TIBBIT`→tibbit_39_2 | tibbit_39_2 |  |
| `node_tibbit_39_3` | Tibbit 39_3 | `tibbit39_on_off`(state:boolean) | `done` | `TIBBIT`→tibbit_39_3 | tibbit_39_3 |  |
| `node_tibbit_39_4` | Tibbit 39_4 | `tibbit39_on_off`(state:boolean) | `done` | `TIBBIT`→tibbit_39_4 | tibbit_39_4 |  |
| `node_tibbit_40_1` | Tibbit 40_1 | `tibbit40_set_ohm`(impedance:dword) | `done` | `TIBBIT`→tibbit_40_1 | tibbit_40_1 |  |
| `node_tibbit_40_2` | Tibbit 40_2 | `tibbit40_set_ohm`(impedance:dword) | `done` | `TIBBIT`→tibbit_40_2 | tibbit_40_2 |  |
| `node_tibbit_40_3` | Tibbit 40_3 | `tibbit40_set_ohm`(impedance:dword) | `done` | `TIBBIT`→tibbit_40_3 | tibbit_40_3 |  |
| `node_tibbit_40_4` | Tibbit 40_4 | `tibbit40_set_ohm`(impedance:dword) | `done` | `TIBBIT`→tibbit_40_4 | tibbit_40_4 |  |
| `node_tibbit_43_1` | Tibbit 43_1 | `tibbit_43_read_channel_1`, `tibbit_43_read_channel_2`, `tibbit_43_read_channel_3`, `tibbit_43_read_channel_4` | `channel1Data`(data:string, channel:byte), `channel2Data`(data:string, channel:byte), `channel3Data`(data:string, channel:byte), `channel4Data`(data:string, channel:byte) | `TIBBIT`→tibbit_43_1 | tibbit_43_1 |  |
| `node_tibbit_43_2` | Tibbit 43_2 | `tibbit_43_read_channel_1`, `tibbit_43_read_channel_2`, `tibbit_43_read_channel_3`, `tibbit_43_read_channel_4` | `channel1Data`(data:string, channel:byte), `channel2Data`(data:string, channel:byte), `channel3Data`(data:string, channel:byte), `channel4Data`(data:string, channel:byte) | `TIBBIT`→tibbit_43_2 | tibbit_43_2 |  |
| `node_tibbit_63_1` | Tibbit 63_1 | `get_line` | `lineState`(state:byte) | `TIBBIT`→tibbit_63_1 |  |  |
| `node_tibbit_63_2` | Tibbit 63_2 | `get_line` | `lineState`(state:byte) | `TIBBIT`→tibbit_63_2 |  |  |
| `node_modbus_register` | Modbus Write | `modbus_poll`(device_id:byte, register_address:word, data:string) | `done` | `DEVICE`→modbus_device; `SERIAL_PORT`; `FUNCTIONCODE` [ReadCoilStatus=Read COIL/Output (0x01)\|ReadInputStatus=Read Contact/Discrete Input (0x02)\|ReadHoldingRegisters=Read Holding Register (0x03)\|ReadInputRegisters=Read Input Register (0x04)\|WriteSingleCoil=Write Single Coil (0x05)\|PresetSingleRegister=Write Single Register (0x06)\|WriteMultipleCoils=Write Multiple Coils (0x0F)\|PresetMultipleRegisters=Write Multiple Registers (0x10)] =ReadCoilStatus |  |  |
| `node_system_halt` | Halt | `sys.halt` | `done` | - |  |  |
| `node_mqtt_connected` | On MQTT Connected | - | `mqtt_connected` | - | mqtt_lib | нужно: network |
| `node_variable_updated` | On Variable Updated | - | `variable_updated` | `VARIABLE`→variable |  |  |
| `node_azure_property` | Azure Property | `azure_pub` | `done` | `PROPERTY_ID`; `PROPERTY_VALUE` stringvariable | azure |  |
| `node_wm2000ev_light` | WM2000 Light Sensor | `wm2000ev_read` | `wm2000ev_data`(data:word) | - | wm2000ev_light |  |
| `node_wm2000ev_temp` | WM2000 Temp Sensor | `wm2000ev_read` | `wm2000ev_data`(data:float) | - | wm2000ev_temp |  |
| `node_lcd_graph` | LCD Graph | `lcd_graph_add`(point:integer) | `done` | - | lcd_graph |  |
| `node_lcd` | LCD Print | `lcd_print`(text:string) | `done` | `FONT` [LCD_STD_FONT=Standard Font\|LCD_SMALL_FONT=Small Font] =LCD_STD_FONT; `COLOR` COLOR =#ffffff; `BACKCOLOR` COLOR =#000000; `ALIGNMENT` [PL_LCD_TEXT_ALIGNMENT_TOP_LEFT=Top Left\|PL_LCD_TEXT_ALIGNMENT_TOP_CENTER=Top Center\|PL_LCD_TEXT_ALIGNMENT_TOP_RIGHT=Top Right\|PL_LCD_TEXT_ALIGNMENT_MIDDLE_LEFT=Middle Left\|PL_LCD_TEXT_ALIGNMENT_MIDDLE_CENTER=Middle Center\|PL_LCD_TEXT_ALIGNMENT_MIDDLE_RIGHT=Middle Right\|PL_LCD_TEXT_ALIGNMENT_BOTTOM_LEFT=Bottom Left\|PL_LCD_TEXT_ALIGNMENT_BOTTOM_CENTER=Bottom Center\|PL_LCD_TEXT_ALIGNMENT_BOTTOM_RIGHT=Bottom Right] =PL_LCD_TEXT_ALIGNMENT_TOP_LEFT; `ORIENTATION` [PL_LCD_TEXT_ORIENTATION_0=At 0 Degrees\|PL_LCD_TEXT_ORIENTATION_90=At 90 degrees\|PL_LCD_TEXT_ORIENTATION_180=At 180 degrees\|PL_LCD_TEXT_ORIENTATION_270=At 270 degrees] =PL_LCD_TEXT_ORIENTATION_0; `VERTICAL_SPACING` number =1 (..255); `HORIZONTAL_SPACING` number =1 (..255); `PX` number =0 (..320); `PY` number =0 (..240); `WIDTH` number =50 (..320); `HEIGHT` number =20 (..240) | lcd |  |
| `node_lcd_card_widget` | LCD Card Widget | `lcd_print_card` | `done` | `WIDGET` | lcd |  |
| `node_disconnected_network` | On Network Disconnected | - | `disconnected_network` | `NETWORK_TYPE` [net=Ethernet\|wifi=WiFi] =net |  |  |
| `node_sleep` | Sleep | `sleep_for` | `done` | `DAYS` number =0; `MINUTES` number =0; `SECONDS` number =60 | wifiwm2000 | нужно: WM2000 или WM2000EV или WS1102 |
| `node_wifiwm2000` | Wi-Fi | - | `wifiwm2000_connected` | - | wifiwm2000 | нужно: WM2000 |
| `node_wifi` | Wi-Fi Connected | - | `wifi_connected` | - | wifi | нужно: WM2000 |
| `node_ser` | Serial | `serial_send`(senddata:string) | `serial_data`(serdata:string) | - | ser | только TiOS |
| `node_wm2000ev_led` | WM2000 PWM LED | `wm2000ev_led_set`(red:byte, green:byte, blue:byte) | `done` | - | wm2000ev_pwm_led | нужно: WM2000EV |
| `node_abs` | Absolute Value | `call`(input:float) | `answer`(absolute_value_answer:float) | - |  |  |
| `node_custom` | Custom Function | - | `done` | `NAME` name =custom_function; `CODE` code =sys.debugprint(param1) |  | порты задаёт проект |
| `node_pico_led` | LED | `ledState` | `done` | `STATE` [OFF\|ON] =OFF |  | нужно: RPPICOW |
| `node_condition` | IF Condition (Advanced) | `cond` | `true_output`, `false_output` | `CODE` code =1=1 |  |  |
| `node_math` | Math | `set_value`(value:custom) | `math_done` | `VARIABLE`→variable |  |  |
