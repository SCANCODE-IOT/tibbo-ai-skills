# Каталог узлов и Tibbit в проектах appblocks.io (снимок 78 проектов; полный список проектов - examples-index.md; `https://appblocks.io/projects/<имя>.json`)

Платы: {'TPP2W(G2)': 75, 'TPP3W(G2)': 3}. Runtime: {'(нет)': 39, 'tios': 34, 'zephyr': 5}.

## Узлы: порты и поля (в скобках — сколько связей в примерах)

| Тип | Входы | Выходы | ARGUMENTS | Свои поля | Где встречается |
|---|---|---|---|---|---|
| `node_arithmetic` | exec(9) | answer(6) | operand1, operand2, operator | VARIABLE | blockstacking, hydroponics, tripwire |
| `node_beep` | beep.play(63) | done(44) | patternstring | CANINT, FREQ | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_button` | — | on_button_pressed(15) | — | — | conditions, helloworld, http-post-tls |
| `node_button_released` | — | on_button_released(6) | — | — | lcd-widgets, modbusmqtt, settingsinit |
| `node_command_trigger` | command_trigger(62) | done(6) | data | COMMAND | http-server-tls, hydroponics, modbusgateway |
| `node_command_triggered` | — | on_command_triggered(68) | — | COMMAND | accesscontrol3, accesscontrol4, accesscontrol5 |
| `node_comparison` | comp(165) | true_output(155), false_output(67) | operand1, operand2, operator | — | accesscontrol3, accesscontrol4, accesscontrol5 |
| `node_compound_condition` | cond(1) | true_output(2), false_output(1) | — | EXPRESSIONS, OPERATOR | modbusgateway |
| `node_cron_event` | — | cron_expired(17) | — | SCHEDULE | datetimeformatting, hydroponics, scheduler |
| `node_datetime` | timestamp_get(21) | timestamp_now(26) | — | — | accesscontrol4, accesscontrol5, accesscontrol6 |
| `node_datetime_format` | time_format(1) | time_str(1) | time_variable | FORMAT | datetimeformatting |
| `node_debug` | sys.debugprint(136) | done(24) | printstring | — | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_forloop` | for_loop(1) | for_loop_iterate(1) | end, start | — | sprinkler6 |
| `node_group` | — | — | — | — | hydroponics, modbusmqtt, modbuspump |
| `node_http` | http_request_start(2) | http_data_arrival(2), http_complete(2), http_error(2) | data | CERTIFICATEFILE, HEADERS, METHOD, URL | http-post-tls, http-request |
| `node_http_server_endpoint` | — | http_requested(2) | — | ENDPOINT | http-server-tls |
| `node_interrupt` | — | on_io_int(1) | — | INTLINE | accesscontrol6 |
| `node_keypad` | — | on_kp(34) | — | BUTTON | accesscontrol2, accesscontrol3, accesscontrol4 |
| `node_label` | — | — | — | — | blockstacking, bp01, dashboard-command |
| `node_lcd_graph_widget` | lcd_print_line(2) | — | — | VALUE, WIDGET | bpsensorstoabc, bpsensortolcdgraph |
| `node_lcd_image_widget` | lcd_image(24) | — | — | IMG, WIDGET | lcd-widgets, tripwire |
| `node_lcd_menu` | lcd_menu_enter(3) | — | — | — | lcd-menu, lcd-widgets, water_level_control_cloud |
| `node_lcd_set_screen` | set_screen(2) | — | — | SCREEN | tbt26_temp_control |
| `node_lcd_text_widget` | lcd_print_text(49) | done(12) | text | VISIBLE, WIDGET | distance-meter, lcd-widgets, modbusgateway |
| `node_log_add` | add_to_log(15) | — | — | PAIRS | accesscontrol5, accesscontrol6, bpsensorstolog |
| `node_math` | set_value(2) | math_done(3) | value | VARIABLE | blockstacking |
| `node_math_compound` | set_value(1) | math_done(1) | — | CODE, FUNCNAME, VARIABLE | pwmlights2 |
| `node_modbus_register` | modbus_poll(1) | done(1) | data, device_id, register_address | DEVICE, FUNCTIONCODE, SERIAL_PORT | modbusscan |
| `node_modbus_response` | — | response(2) | — | — | modbusscan, tbt26_temp_control |
| `node_modbus_timeout` | — | — | — | — | water_level_control_cloud |
| `node_modbus_write` | modbus_poll(4) | modbus_response(4), modbus_timeout(4) | — | DATA, DEVICE, DEVICEID, DEVICEIP, DEVICEPORT, ENDIAN, FUNCTIONCODE, LENGTH, PROTOCOL, REGISTER_ADDRESS, SERIAL_PORT, VARTYPE | modbusmqtt |
| `node_mqtt_pub` | mqtt_publish(13) | done(1) | publish_data, qos, retain, topic | — | 4gswitchover, bpsensorstomqtt, modbusmqtt |
| `node_mqtt_sub` | — | callback_mqtt_notif(1) | — | TOPIC | mqtt-pub-sub |
| `node_network_changed` | — | network_changed(4) | — | NETWORK_EVENT, NETWORK_TYPE | modbusgateway |
| `node_pat` | pat.play(73) | done(22) | patternstring | CANINT | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_ser_data_arrival` | — | data_available(32) | — | MODE, PACKET_END, PACKET_START, SERIAL_PORT | distance-meter, hydroponics, rs232_dispatcher |
| `node_ser_data_send` | data_send(13) | — | — | DATA, SERIAL_PORT | hydroponics, rs232_dispatcher |
| `node_settings_init` | stg_init(2) | done(2) | — | — | modbusmqtt, settingsinit |
| `node_socket_data_arrival` | — | sock_data_arrival(4) | — | SOCKET | modbusgateway |
| `node_socket_event` | — | sock_connection_event(16) | — | EVENT_TYPE, SOCKET | modbusgateway |
| `node_switch` | switch_exec(1) | <case ID>(4) | — | CASES, VALUE | modbusmqtt |
| `node_system` | sys.halt, sys.reboot | boot(51), on_sys_timer | — | — | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_system_reboot` | sys.reboot(2) | — | — | — | modbusmqtt, settingsinit |
| `node_table` | tbl_record_find(20) | tbl_record_found(32), tbl_record_not_found(9) | field_value, find_index | FIELD_NAME, OPERATOR, TABLE, WRAPAROUND | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_table_insert` | tbl_add(4) | — | NAME, TS, VALUE, timestamp, value | TABLE | modbusgateway, modbusmqtt |
| `node_table_row_count` | tbl_count(2) | tbl_count_result(2) | — | TABLE | modbusmqtt |
| `node_table_update` | tbl_update(1) | — | — | FIELDS, FIELD_NAME, OPERATOR, TABLE, VALUE | modbusmqtt |
| `node_tibbit_26_end` | tbt26_get_data(1), sys.halt, sys.reboot | tibbit26_data(1), boot, on_sys_timer | — | ENCODING, TIBBIT | tbt26_temp_control |
| `node_tibbit_26_send` | tbt26_play_back(4), sys.halt, sys.reboot | boot, on_sys_timer | data | ENCODING, TIBBIT | tbt26_temp_control |
| `node_tibbit_26_start` | tbt26_start_recording(1), sys.halt, sys.reboot | boot, on_sys_timer | — | TIBBIT | tbt26_temp_control |
| `node_time_delay` | delay_start(10) | delay_elapsed(10) | — | DURATION | hydroponics, modbusmqtt, smart_plants |
| `node_time_interval` | — | timer_tick(70) | — | INTERVAL | 4gswitchover, bp01, bp05 |
| `node_timer_completed` | — | timer_complete(26) | — | TIMER | accesscontrol1, accesscontrol2, accesscontrol3 |
| `node_timer_start` | timer_start(11) | done(2) | time | REPEAT, TIMER | modbusgateway, modbusmqtt, remote-reboot |
| `node_timer_stop` | timer_stop(2) | done(2) | — | TIMER | timerscontinued, timersstartstop2 |
| `node_variable_changed` | — | variable_changed(56) | — | VARIABLE | hydroponics, lcd-menu, luis |
| `node_variable_set` | set_value(389) | variable_set_done(238) | value | VARIABLE | 4gswitchover, accesscontrol1, accesscontrol2 |
| `node_wiegand` | — | data_available(19) | — | FORMAT, TIBBIT | accesscontrol1, accesscontrol2, accesscontrol3 |

## Tibbit: поля и сокеты в примерах

| Feature | Поля | (плата, сокет)×раз |
|---|---|---|
| `tibbit_00_1` | INTEDGE, L1MODE, L1NAME, L2MODE, L2NAME, L3MODE, L3NAME, L4MODE, L4NAME, NAME | TPP2W(G2) S7×1, TPP2W(G2) S1×1 |
| `tibbit_00_3` | L1MODE, L1NAME, L2MODE, L2NAME, NAME | TPP2W(G2) S1×6, TPP2W(G2) S3×2, TPP3W(G2) S7×1, TPP3W(G2) S3×1 |
| `tibbit_01` | BAUD, BITS, FLOWCONTROL, NAME, PARITY, RXBUF, TXBUF | TPP3W(G2) S9×2, TPP3W(G2) S5×2, TPP2W(G2) S1×1, TPP3W(G2) S1×1 |
| `tibbit_02` | BAUD, BITS, FLOWCONTROL, MODE, NAME, PARITY, RXBUF, TXBUF | TPP3W(G2) S1×1 |
| `tibbit_03_1` | L1NAME, L2NAME, NAME | TPP2W(G2) S5×14, TPP3W(G2) S15×1, TPP3W(G2) S11×1, TPP2W(G2) S1×1 |
| `tibbit_05` | BAUD, BITS, FLOWCONTROL, MODE, NAME, PARITY, RXBUF, TXBUF | TPP2W(G2) S1×17, TPP2W(G2) S3×2, TPP3W(G2) S5×1, TPP3W(G2) S13×1 |
| `tibbit_06` | L1NAME, L2NAME, NAME | TPP3W(G2) S17×1 |
| `tibbit_08` | MODE, NAME, RXBUF, TXBUF | TPP2W(G2) S3×7 |
| `tibbit_09` | — | TPP2W(G2) S11×6 |
| `tibbit_10` | — | TPP2W(G2) S11×56, TPP2W(G2) S9×3, TPP3W(G2) S27×1, TPP2W(G2) S1×1 |
| `tibbit_12` | — | TPP2W(G2) S9×1 |
| `tibbit_16` | FREQUENCY, L1NAME, L2NAME, L3NAME, NAME, PIC_CLOCK_SPEED, USESSI | TPP2W(G2) S9×2, TPP2W(G2) S7×1 |
| `tibbit_17` | FREQUENCY, L1NAME, L2NAME, L3NAME, NAME, PIC_CLOCK_SPEED, USESSI | TPP2W(G2) S3×1, TPP2W(G2) S5×1 |
| `tibbit_18` | — | TPP2W(G2) S12×62, TPP2W(G2) S10×3, TPP3W(G2) S26×1, TPP3W(G2) S28×1 |
| `tibbit_19` | — | TPP3W(G2) S2×2, TPP3W(G2) S6×1, TPP3W(G2) S10×1, TPP3W(G2) S14×1 |
| `tibbit_20` | — | TPP2W(G2) S2×17, TPP2W(G2) S6×16, TPP3W(G2) S6×1, TPP3W(G2) S10×1 |
| `tibbit_21` | — | TPP2W(G2) S2×16, TPP2W(G2) S10×2, TPP2W(G2) S12×1, TPP2W(G2) S4×1 |
| `tibbit_22` | CONV, MAX_NUM, NAME, SENSOR, TEMP_NAME, USESSI | TPP2W(G2) S1×1 |
| `tibbit_26` | NAME | TPP2W(G2) S1×1 |
| `tibbit_28` | LIGHT_NAME | TPP2W(G2) S2×2 |
| `tibbit_29` | TEMP_NAME | TPP2W(G2) S2×2 |
| `tibbit_30` | HUM_NAME, TEMP_NAME | TPP2W(G2) S2×2 |
| `tibbit_33` | GENERAL, PF | TPP2W(G2) S11×3, TPP3W(G2) S25×1 |
| `tibbit_45_2` | — | TPP2W(G2) S5×1 |
| `tibbit_54` | INTEDGE, L1MODE, L1NAME, L2MODE, L2NAME, L3MODE, L3NAME, L4MODE, L4NAME, NAME | TPP2W(G2) S1×2 |
| `tibbit_61_1` | ADVANCED, GENERAL, IIN1, IIN2, MODE, NAME, VIN1M, VIN1P, VIN2M, VIN2P | TPP3W(G2) S21×1, TPP2W(G2) S5×1 |
| `tibbit_62` | NAME | TPP2W(G2) S1×1 |
| `tibbit_63_1` | INTERRUPT, NAME | TPP2W(G2) S1×1 |

## Прочие feature (сколько проектов)

`linked_setting` 114, `boardsetting` 78, `net` 78, `general` 78, `global_vars` 78, `tbl` 78, `log` 78, `datetime` 78, `time` 78, `timers` 76, `stg` 76, `cron` 76, `commands` 76, `cell` 76, `bt` 76, `httpserver` 76, `modbus_master` 76, `mqtt` 76, `sntp` 76, `web_dashboard` 76, `luis` 76, `ds_man` 76, `sock` 75, `modbus_slave` 74, `lcd` 73, `lcd_graph` 73, `wifi` 70, `unowiresensors` 69, `dhcp` 59, `lcd_menu` 54, `dns` 50, `http` 45, `fd` 42, `filenum` 42, `cgg` 39, `firmware_upgrade` 36, `custom_features` 36, `wln` 25, `stgcmd_lib` 22, `display_lib` 21, `modbus` 20, `beep` 19, `kp` 16, `wireless_module` 12, `mqtt_lib` 12, `socket` 10, `flash_devices` 5, `peripheral_wiring` 5, `mbedtls` 5, `variable` 5, `snmp_agent` 2, `smtp_client` 2, `custom_feature_id` 2, `files` 1, `datasheet_pages` 1, `azure_command` 1, `azure` 1
