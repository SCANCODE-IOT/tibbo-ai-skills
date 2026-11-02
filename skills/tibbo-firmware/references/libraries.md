# Tibbo BASIC libraries (auto-extracted from github.com/tibbotech/libraries)

How libraries work: add the library's .tbh/.tbs files to the project (TIDE: Add existing file / libraries come with
TIDE in Platforms/src/<ver>/), `include` its .tbh from global.tbh, set configuration `#define`s in global.tbh
BEFORE the include (each lib uses `#ifndef X / #define X default`), call `<lib>_start()` style init from
on_sys_init, and IMPLEMENT every `callback_*` sub/function the library declares (empty body is OK when unused) —
otherwise the project fails to link. Many libs require the timer/event hooks listed in their .tbs (e.g. calls
from on_sys_timer, on_sock_data_arrival, on_sock_event, on_wln_event) — check the lib .tbs header comments.

Practical notes (checked by building in TIDE with libraries 2_01_05, October 2026):
- `*_proc_timer()` of dhcp/dns/mqtt/sntp count timeouts in calls and expect the default on_sys_timer period (0.5 s);
  with a faster `sys.onsystimerperiod` call them through a divider.
- Tibbit drivers from the latest tibbotech/libraries (tbt13, tbt14, tbt29, cellular) can be copied into the project
  folder and used with TIDE libraries 2_01_05, but: include `super_i2c.tbh` BEFORE `ssi.tbh` (otherwise
  `SSI_MAX_SIGNATURE_LEN` is redefined); the latest `cellular` calls `fstr()`, which TIDE 2_01_05 does not have -
  replace it with an own wrapper over `ftostr`.


## aggregate/aggregate.tbh

Config defines (set before include):
- `AGG_DEBUG_PRINT` = 0 — AGGREGATE AGENT LIBRARY
- `AGG_LOGIN_CONTROL` = 0
- `AGG_TABLE_CONTROL` = 0
- `AGG_SETTING_CONTROL` = 0
- `AGG_DESCRIPTOR_FILE` = "aggregate.txt"
- `AGG_MAX_CONTEXT_NAME_LEN` = 4
- `AGG_MAX_SCRIPT_LINE_NAME_LEN` = 12
- `AGG_MAX_NUM_ENTITY_TYPES` = 2
- `AGG_MAX_NUM_SCRIPT_LINES` = 0
- `AGG_TEMP_TABLE_NAME` = "Tmp"
- `AGG_MAX_RECONNECTION_DELAY` = 15
- `AGG_MAX_FUNCTION_NAME_LEN` = 12
- `AGG_MULTI_CONTEXT` = 0
- `AGG_SEND_WAIT_TIME` = 0
- `AGG_MAX_NUM_STORED_EVENTS` = 0
- `AGG_STORED_EVENT_LVL_FIELD` = "AEL"
- `AGG_REMOTE_FIRMWARE_UPLOAD` = 1
- `AGG_CUSTOM_RTC` = 0
- `AGG_KEEPALIVE_TMR_CTR` = 20

API:
- `function agg_start(interface as pl_sock_interfaces, byref onwer_name as string, byref device_name as string, byref password as string, byref agg_server_ip as string, agg_server_port as word, agg_server_tout as word, auto_reg as no_yes) as en_agg_status_codes`
- `sub agg_stop()`
- `sub agg_fire_instant_event(byref context_name as string, byref event_name as string, byref event_string as string, event_level as en_agg_event_levels)`
- `sub agg_get_connection_state(byref link_state as en_agg_link_states, byref sock_state as pl_sock_state_simple)`
- `sub agg_proc_timer()`
- `sub agg_proc_data()`
- `sub agg_proc_sock_event(sock_state as pl_sock_state, sock_state_simple as pl_sock_state_simple)`
- `function agg_record_decode(byref encode_string as string, field_index as byte) as string`
- `sub agg_record_encode(byref encode_string as string, byref field_value as string)`
- `sub agg_keep_alive()`
- `sub agg_proc_stored_events()`
- `sub agg_proc_data_sent()`
- `sub agg_stored_event_added(byref event_name as string)`

Callbacks YOU must implement:
- `function callback_agg_external_data_source(byref source_type as string, byref parameter1 as string, byref parameter2 as string, byref parameter3 as string, rw as en_agg_rdwr)as ok_ng` — Callback procedure, to allow the possibility of reading and writing to a user defined data structure which is not part of our libraries. Procedure body has to b
- `function callback_agg_external_data_modtime_sg(byref source_type as string, byref item_name as string, byref date_time as string, op as en_agg_rdwr) as ok_ng` — Callback procedure, to allow the possibility of reading and writing to the modtime of a user defined data structure. Procedure body has to be created elsewhere 
- `function callback_agg_get_firmware_version() as string` — Callback procedure, reads firmware version, firmware version could be used by multiple modules, therefore should not be included in the library. Procedure body 
- `sub callback_agg_pre_buffrq(required_buff_pages as byte)` — Callback procedure, informs of the insufficient number of free buffer pages available for use by the library. Procedure body has to be created elsewhere in the 
- `sub callback_agg_buff_released()` — Callback procedure, informs of the release of buffer pages by the library. Procedure body has to be created elsewhere in the project (externally with respect to
- `sub callback_agg_error(failure_code as en_agg_status_codes, byref error_item as string)` — Callback procedure, informs of the error happened during AggreGate related operations. Procedure body has to be created elsewhere in the project (externally wit
- `function callback_agg_device_function(byref function_name as string ,byref context_name as string, byref function_input as string, byref function_output as string) as ok_ng` — Callback procedure, calls user defined operations, allows users to expend the functions that can be called from AggreGate Server. Procedure body has to be creat
- `sub callback_agg_synchronized()` — Callback procedure, informs of the success of data synchronization with AggreGate Server. Procedure body has to be created elsewhere in the project (externally 
- `sub callback_agg_rtc_sg(byref wdaycount as word, byref wmincount as word, byref bsec as byte, byref wmilsec as word, op as en_agg_rdwr)` — Callback procedure, reads and sets external RTC, instead of using the onboard RTC IC Procedure body has to be created elsewhere in the project (externally with 
- `function callback_agg_setting_saved(byref setting_name as string,index as byte, byref setting_val as string) as en_stg_status_codes` — Callback procedure, informs settings has been modified by AggreGate Server Procedure body has to be created elsewhere in the project (externally with respect to
- `sub callback_agg_setting_error(byref setting_name as string, error_code as en_stg_status_codes)` — Callback procedure, informs of errors happened during accessing settings by AggreGate Server. Procedure body has to be created elsewhere in the project (externa
- `function callback_agg_convert_setting(byref setting_name as string, index as byte, byref setting_value as string, op as en_agg_rdwr) as ok_ng` — Callback procedure, allows settings to be converted, in the case that settings stored in device and on AggreGate Server are in different format. Procedure body 
- `sub callback_agg_table_error(byref table_name as string, error_code as en_tbl_status_codes)` — Callback procedure, informs of errors happened during accessing tables by AggreGate Server. Procedure body has to be created elsewhere in the project (externall
- `sub callback_agg_convert_table_field(byref table_name as string, byref field_name as string, byref field_value as string, op as en_agg_rdwr)` — Callback procedure, allows table fields to be converted, in the case that table fields stored in device and on AggreGate Server are in different format. Procedu
- `sub callback_agg_firmware_upload_progress(total_size as dword, remain_size as dword)`

Enums: `en_agg_rdwr`(EN_AGG_GET, EN_AGG_SET); `en_agg_status_codes`(EN_AGG_STATUS_OK, EN_AGG_STATUS_NOT_STARTED, EN_AGG_STATUS_WRONG_DESCRIPTOR, EN_AGG_STATUS_OUT_OF_SOCKETS, EN_AGG_STATUS_INVALID_INTERFACE, EN_AGG_STATUS_INSUFFICIENT_BUFFER_SPACE, EN_AGG_STATUS_CONNECTION_LOST, EN_AGG_STATUS_UNABLE_TO_CONNECT, EN_AGG_STATUS_SETTING_ERROR, EN_AGG_STATUS_TABLE_ERROR, EN_AGG_STATUS_FUNCTION_ERROR, EN_AGG_STATUS_ITEM_NOT_FOUND); `en_agg_link_states`(EN_AGG_LINK_STATE_IDLE, EN_AGG_LINK_STATE_CONNECTING, EN_AGG_LINK_STATE_SYNCRONIZING, EN_AGG_LINK_STATE_DISCONNECTED, EN_AGG_LINK_STATE_ESTABLISHED); `en_agg_event_levels`(EN_AGG_EVENT_LEVEL_NONE, EN_AGG_EVENT_LEVEL_NOTICE, EN_AGG_EVENT_LEVEL_INFO, EN_AGG_EVENT_LEVEL_WARNING, EN_AGG_EVENT_LEVEL_ERROR, EN_AGG_EVENT_LEVEL_FATAL, EN_AGG_EVENT_LEVEL_USE_DEFAULT)

## azure/azure.tbh

Config defines (set before include):
- `AZURE_DEBUG_PRINT` = 0

API:
- `function azure_update_json(byref original as string, byref attribute as string, byref value as string) as string`
- `sub azure_start(byref device_id as string, byref scope_id as string, byref dps_url as string, byref symmetricKey as string, interface as pl_sock_interfaces)`
- `sub azure_proc_timer()`
- `sub azure_on_connected()`
- `sub azure_device_lookup()`
- `sub azure_on_disconnected()`
- `sub azure_proc_mqtt_msg(byref topic as string, byref data as string)`
- `sub azure_mqtt_sub_ok()`
- `sub azure_command_respond(byref command as string, byref returns as string, rid as string, result as en_azure_command_codes)`
- `sub azure_on_telemetry_sent()`
- `sub azure_set_datetime(byref dt_string as string)`
- `sub iot_send_headers()`
- `sub azure_content_arrival(data as string)`
- `sub azure_http_request_complete()`
- `sub iot_header_arrival(header_type as string, header_value as string)`
- `sub azure_send_telemetry()`
- `sub azure_send_property(prop_name as string, prop_value as string)`
- `sub azure_store_telemetry(message_type as string, message_value as string)`

Callbacks YOU must implement:
- `sub callback_azure_command_triggered(byref command as string, byref param as string, rid as string)`
- `sub callback_azure_property_desired(byref property_name as string, byref property_value as string)`
- `sub callback_azure_device_assigned(byref assigned_hub as string)`
- `sub callback_on_telemetry_sent()`

Enums: `en_azure_command_codes`(EN_AZURE_OK, EN_AZURE_ACCEPTED, EN_AZURE_BAD_REQUEST, EN_AZURE_UNAUTHORIZED); `en_azure_states`(EN_AZURE_NOT_CONNECTED, EN_AZURE_DEVICE_LOOKUP, EN_AZURE_NOT_PROVISIONED, EN_AZURE_PROVISIONING, EN_AZURE_CONNECTED)

## cell/cell.tbh

Config defines (set before include):
- `CELL__DEBUG_PRINT` = 0 — CELLULAR LIBRARY
- `CELLULAR_AVAILABLE` = 1
- `CELL__PING_IP` = "8.8.8.8"
- `CELL_BANDTYPE` = "3"
- `CELL__PPP_MODE_ISENABLED` = 1 — CELL MODES---------------------------------------------------------- PPP
- `CELL__AT_USERMODE_ISENABLED` = 1 — COMMAND
- `CELL__GPS_MODE_ISENABLED` = 1 — GPS
- `CELL__AUTO_POLARITY_ADJUST_ISENABLED` = 1 — AUTO-POLARITY-ADJUST
- `CELL__DEBUGPRINT_UDP_ISENABLED` = 0 — UDP DEBUGPRINT--------------------------------------------------- 1: Enable print in debugmode 0: Disable print in debugmode
- `CELL__DEBUGPRINT_SERPORT_ISENABLED` = 0 — SERIAL DEBUGPRINT--------------------------------------------------- 1: Enable print in debugmode 0: Disable print in debugmode
- `CELL__DEBUGPRINT_PWR_ISENABLED` = 1 — POWER DEBUGPRINT----------------------------------------------------
- `CELL__DEBUGPRINT_AT_ISENABLED` = 1 — AT DEBUGPRINT-------------------------------------------------------
- `CELL__DEBUGPRINT_PPP_ISENABLED` = 1
- `CELL__DEBUGPRINT_GPS_ISENABLED` = 1
- `CELL__AT_FAST_LOAD_ISENABLED` = 1 — AT FAST LOAD-------------------------------------------------------- 1: Enable 0: Disable REMARK: for NB-IOT, this option should be ENABLED. Otherwise the PPP-connection may fail.
- `CELL__PPP_FAST_LOAD_ISENABLED` = 1 — PPP FAST LOAD------------------------------------------------------- 1: Enable 0: Disable REMARK: for NB-IOT, this option should be ENABLED. Otherwise the PPP-connection may fail.
- `CELL__ON` = HIGH — LINE DEFINITION-----------------------------------------------------
- `CELL__OFF` = (CELL__ON - 1)
- `CELL__PAYLOAD_SIZE` = 4 — PAYLOAD SIZE-------------------------------------------------------- UDP and TCP Payload Size expressed in 256-byte per page. REMARK: do not set the payload size >4 or <1.
- `CELL__INTERCHAR_DELAY_VAL` = 10 — PORT ASSIGNMENTS---------------------------------------------------- SERIAL PORTS interchardelay
- `CELL__DEBUGPRINT_SER_PORT` = 0 — Assign Serial-ports
- `CELL__DATA_SER_PORT` = 2
- `CELL__CTS_LINENUM` = CELL__DATA_SER_PORT — CTS (Clear To Send) serial Port Selection NOTE: CTS LINE is always linked to an INTERRUPT LINE

API:
- `sub cell__callback_powering_onoff_failed()` — <b>METHOD. </b><br><br> Callback to notify that the connectivity hardware has failed to power on or off.
- `sub cell__callback_get_into_rdy_state_failed()` — <b>METHOD. </b><br><br> Callback to notify that the modem has failed to get into the RDY state.
- `sub cell__callback_modem_restart_failed()` — <b>METHOD. </b><br><br> Callback to notify that modem failed to restart.
- `sub cell__callback_modem_on()` — <b>METHOD. </b><br><br> Callback to notify that the modem has been activated successfully and its state is Active.
- `sub cell__callback_modem_off()` — <b>METHOD. </b><br><br> Callback to notify that the modem has been deactivated successfully and its state is Inactive.
- `sub cell__callback_insufficient_buffer_pages()` — <b>METHOD. </b><br><br> Callback to notify that the buffer pages allocated for data serial port, UDP, and TCP operations are insufficient to initialize the libr
- `sub cell__callback_at_reply()` — <b>METHOD. </b><br><br> Callback to show the parsed AT reply.
- `sub cell__callback_at_reply_contains_error()` — <b>METHOD. </b><br><br> Callback to notify that AT reply contains an ERROR.
- `sub cell__callback_ppp_fcs_is_bad()` — <b>METHOD. </b><br><br> Callback to notify that FCS is bad.
- `sub cell__callback_ppp_missing_address_field()` — <b>METHOD. </b><br><br> Callback to notify that the <i>address</i> field is not present.
- `sub cell__callback_ppp_missing_control_field()` — <b>METHOD. </b><br><br> Callback to notify that the <i>control</i> field is not present.
- `sub cell__callback_ppp_lcp_msg_length_not_matching()` — <b>METHOD. </b><br><br> Callback to notify that the LCP message <i>length</i> does not match the expected result.
- `sub cell__callback_ppp_lcp_successful()` — <b>METHOD. </b><br><br> Callback to notify that LCP negotiation was successful.
- `sub cell__callback_ppp_lcp_disreq_from_peer()` — <b>METHOD. </b><br><br> Callback to notify that an LCP discard request was received from peer.
- `sub cell__callback_ppp_lcp_disreq_from_sender()` — <b>METHOD. </b><br><br> Callback to notify that an LCP discard request was received from sender.
- `sub cell__callback_ppp_retry_exceeded()` — <b>METHOD. </b><br><br> Callback to notify that the number of PPP reconnection attempts has exceeded the maximum allowed quota.
- `sub cell__callback_ppp_pap_successful()` — <b>METHOD. </b><br><br> Callback to notify that PAP negotiation was successful.
- `sub cell__callback_ppp_pap_nego_failed()` — <b>METHOD. </b><br><br> Callback to notify that PAP negotiation was unsuccessful.
- `sub cell__callback_ppp_ipcp_successful()` — <b>METHOD. </b><br><br> Callback to notify that IPCP negotiation was successful.
- `sub cell__callback_ppp_connection_to_server_successful()` — <b>METHOD. </b><br><br> Callback to notify that connection to specified server was successful.
- `sub cell__callback_ppp_connection_to_server_retry()` — <b>METHOD. </b><br><br> Callback to notify that system is attempting to connect to the specified server.
- `sub cell__callback_ppp_connection_to_server_failed()` — <b>METHOD. </b><br><br> Callback to notify that the connection to the specified server has failed.
- `sub cell__callback_ppp_ipcp_disreq_from_peer()` — <b>METHOD. </b><br><br> Callback to notify that an IPCP discard request was received from peer.
- `sub cell__callback_ppp_ipcp_disreq_from_sender()` — <b>METHOD. </b><br><br> Callback to notify that an IPCP discard request was received from sender.
- `sub cell__callback_ppp_ping_successful()` — <b>METHOD. </b><br><br> Callback to notify that the ping was successful.
- `sub cell__callback_ppp_ping_failed()` — <b>METHOD. </b><br><br> Callback to notify that the ping failed.
- `sub cell__callback_ppp_link_established()` — <b>METHOD. </b><br><br> Callback to notify that a PPP link has been established.
- `sub cell__callback_after_switching_from_DATA_to_CMD()` — <b>METHOD. </b><br><br> Callback to notify after switching from Data-mode or PPP-mode to Command-mode.
- `sub cell__callback_after_switching_from_CMD_to_DATA()` — <b>METHOD. </b><br><br> Callback to notify after switching from Command-mode to Data-mode or PPP-mode.
- `sub cell__callback_gps_siv()` — <b>METHOD. </b><br><br> Callback to show the Satellites in View (SIV).
- `sub cell__callback_gps_position()` — <b>METHOD. </b><br><br> Callback to show the GPS position.
- `sub cell__callback_at_notification()` — <b>METHOD. </b><br><br> Callback to notify that manual AT command mode is enabled and ready.
- `sub cell__callback_at_usermode_cmd_input()` — <b>METHOD. </b><br><br> Callback that provides area for users to place their AT commands.
- `sub cell__callback_at_usermode_sms_message_length_exceeded_error()` — <b>METHOD. </b><br><br> Callback to notify that the to-be-sent SMS-message exceeds the maximum allowed 160 characters. <br><br>
- `sub cell__callback_at_usermode_sms_sent_notif()` — <b>METHOD. </b><br><br> Callback to notify that an SMS-message has been sent.
- `sub cell__callback_at_usermode_sms_rcv_notif()` — <b>METHOD. </b><br><br> Callback to notify that an SMS-message has been received.
- `sub cell__callback_at_usermode_sms_auto_reply()` — <b>METHOD. </b><br><br> Callback to autoreply for the received SMS-message.
- `sub cell__callback_at_usermode_sms_storage_full_notif()` — <b>METHOD. </b><br><br> Callback to notify that the SMS-storage is full.
- `sub cell__callback_at_storage_full()` — <b>METHOD. </b><br><br> Callback to notify that AT command storage is full.
- `function cell__start(byref pin as string(CELL__16b_LEN), byref apn as string,` — <b>METHOD. </b><br><br> Callback to notify that AT command storage is full. DECLARATIONS--------------------------------------------------------
- `sub cell__graceful_shutdown()` — <b>METHOD. </b><br><br> Powers off modem gracefully.<br><br> <b>REMARKS: </b><br> <ul> <li>can be called from any mode (<font color="gray">e.g., Command-, Data-
- `function cell__stop(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Powers off modem gracefully.<br><br> <b>REMARKS: </b><br> <ul> <li>can be called from any mode (<font color="gray">e.g., Command-, Data-
- `function cell__buffersize_isSufficient() as boolean` — <b>METHOD. </b><br><br> Calculates whether the buffers allocated for the data serial port and PPP operations are within acceptable limits. One page equals 256 b
- `function cell__calc_timediff_16b(tstart as word, tend as word) as word` — <b>METHOD </b><br><br> Calculates the elapsed time between two points of time (in 500 millisecond increments).<br><br> <b>Input parameters:</b> <ul> <li>tstart<
- `sub cell__ltrim_crlf(byref inputdata as string)` — <b>METHOD. </b><br><br> Trims <font color="dodgerblue">leading</font> CR and LF.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magenta"> - </f
- `sub cell__rtrim_crlf(byref inputdata as string)` — <b>METHOD. </b><br><br> Trims <font color="dodgerblue">trailing</font> CR and LF.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magenta"> - </
- `sub cell__trim_lstring(byref inputdata as string, byref lstring as string(CELL__128b_LEN))` — <b>METHOD. </b><br><br> Trims <font color="dodgerblue">leading</font> string as specified.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magen
- `sub cell__substitute_char(byref inputdata as string, byref oldchar as string(CELL__1b_LEN), byref newchar as string(CELL__1b_LEN))` — <b>METHOD. </b><br><br> Replaces one character with another.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magenta"> - </font><i>Data to be pa
- `function cell__get_string_between_2chars( byref inputdata as string, nth_occur as byte,` — <b>METHOD. </b><br><br> Replaces one character with another.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magenta"> - </font><i>Data to be pa
- `sub cell__debugprint_thru_udp(byref msg as string)` — <b>METHOD. </b><br><br> Prints debug messages via a specified UDP port.<br><br> <b>Input parameters:</b> <ul> <li>msg<font color="magenta"> - </font><i>Debug me
- `sub cell__debugprint_thru_serport(byref msg as string)` — <b>METHOD. </b><br><br> Prints debug messages via a specified serial port.<br><br> <b>Input parameters:</b> <ul> <li>msg<font color="magenta"> - </font><i>Debug
- `sub cell__debugprint_status(select_phase as en_cell__status_phases, byref msg as string)` — <b>METHOD. </b><br><br> Prints the modem's status after it is powered on.<br><br> <b>Input parameters:</b> <ul> <li>select_phase<font color="magenta"> - </font>
- `sub cell__debugprint_pwr_phase(select_phase as en_cell__op_pwr_phases,` — <b>METHOD. </b><br><br> Prints the modem's status after it is powered on.<br><br> <b>Input parameters:</b> <ul> <li>select_phase<font color="magenta"> - </font>
- `sub cell__debugprint_at_phase(select_phase as en_cell__op_at_phases, byref atcmd as string, byref msg as string)` — <b>METHOD. </b><br><br> Prints AT-related debug messages.<br><br> <b>Input parameters:</b> <ul> <li>select_phase<font color="magenta"> - </font><i>Specifies at 
- `sub cell__debugprint_ppp_phase(select_phase as en_cell__op_ppp_phases,`
- `sub cell__debugprint_gps_phase(select_phase as en_cell__op_gps_phases,`
- `sub cell__update_op_next_phases(new_pwr_phase as en_cell__op_pwr_phases, new_at_phase as en_cell__op_at_phases,`
- `sub cell__init(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Updates the operational <font color="dodgerblue">POWER</font>, <font color="dodgerblue">AT</font>, <font color="dodgerblue">PPP</font>, 
- `sub cell__deinit(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Initializes the connectivity hardware.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"> - </font><i>Next P
- `sub cell__init_param_var_bool()` — <b>METHOD. </b><br><br> Initializes parameters, variables and booleans.
- `sub cell__init_io()` — <b>METHOD. </b><br><br> Sets and enables I/O lines as input/output.<br>
- `sub cell__init_at_cmd_storArray()` — <b>METHODE. </b><br><br> Initializes USERMODE-related variables (Array and Index)
- `sub cell__reverse_polarity(byref pwr_object as en_cell__pwr_objects, rev_polarity as no_yes)` — <b>METHOD. </b><br><br> Changes the polarity of a specified power-related object.<br><br> <b>Input parameters:</b> <ul> <li>pwr_object<font color="magenta"> - <
- `sub cell__init_debugprint_udp(byref primary_ip as string(CELL__16b_LEN), byref secondary_ip as string(CELL__16b_LEN), targetport as word)` — <b>METHOD. </b><br><br> Initializes UDP port for debug printing.<br><br> <b>Input parameters:</b> <ul> <li>primary_ip<font color="magenta"> - </font><i>Primary 
- `sub cell__init_debugprint_ser()` — <b>METHOD. </b><br><br> Initializes a serial port for debug printing.
- `sub cell__init_ser()` — <b>METHOD. </b><br><br> Initializes serial-port related parameters and variables.
- `sub cell__deinit_ser()` — <b>METHOD. </b><br><br> De-initializes serial-port related parameters and variables.
- `sub cell__init_ppp()` — <b>METHOD. </b><br><br> Initializes the varables used for the PPP connection status check.<br><br>
- `sub cell__deinit_ppp()` — <b>METHOD. </b><br><br> De-initializes PPP-related variables and parameters (including sockets).
- `sub cell__modem_restart(next_pwr_phase as en_cell__op_pwr_phases)` — <b>METHOD. </b><br><br> Sets the required settings before initiating a modem-restart. <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"> - <
- `sub cell__reset_on(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Sets the required settings before initiating a modem-restart. <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"> - <
- `sub cell__reset_wait(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Sets the RESET line to <font color="green">active</font>. <br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"
- `sub cell__reset_retry()` — <b>METHOD. </b><br><br> Retries to power the connectivity hardware <font color="green">on</font>/<font color="tomato">off</font> via reset.<br><br>
- `sub cell__reset_off(next_pwr_on_phase as en_cell__op_pwr_phases, next_pwr_off_phase as en_cell__op_pwr_phases,` — <b>METHOD. </b><br><br> Retries to power the connectivity hardware <font color="green">on</font>/<font color="tomato">off</font> via reset.<br><br>
- `sub cell__shdn_off(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Sets the RESET line back to <font color="tomato">Inactive</font>.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_on_phase<font color
- `sub cell__shdn_wait(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Powers <font color="tomato">off</font> the power regulator.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta
- `sub cell__shdn_retry()` — <b>METHOD. </b><br><br> Retries to power the connectivity hardware <font color="green">on</font>/<font color="tomato">off</font> via shutdown.<br><br>
- `sub cell__shdn_on(next_pwr_on_phase as en_cell__op_pwr_phases, next_pwr_off_phase as en_cell__op_pwr_phases,` — <b>METHOD. </b><br><br> Retries to power the connectivity hardware <font color="green">on</font>/<font color="tomato">off</font> via shutdown.<br><br>
- `sub cell__pwrkey_on(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Powers <font color="green">on</font> the power regulator.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_on_phase<font color="magent
- `sub cell__pwrkey_off(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Sets power switch to <font color="green">on</font>.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"> - </f
- `sub cell__pwrkey_retry()` — <b>METHOD. </b><br><br> Retries to power <font color="green">on</font>/<font color="tomato">off</font> the connectivity hardware via PWRKEY.<br><br>
- `sub cell__powering_onoff(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Retries to power <font color="green">on</font>/<font color="tomato">off</font> the connectivity hardware via PWRKEY.<br><br>
- `sub cell__powering_onoff_wait(next_pwr_on_phase as en_cell__op_pwr_phases, next_pwr_off_phase as en_cell__op_pwr_phases,` — <b>METHOD. </b><br><br> Provides notification on whether the connectivity hardware is powering <font color="green">on</font> or <font color="tomato">off</font>.
- `sub cell__check_rdy_state(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Waits for the STATUS line to change from <font color="green">active</font> to <font color="tomato">inactive</font> or vice-versa.<br><br
- `sub cell__modem_onoff(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Checks and waits until the serial port is <font color="dodgerblue">RDY</font>.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<
- `sub cell__flush_all_data()` — <b>METHOD. </b><br><br> Flushes all garbage data.
- `sub cell__ser_port_flush_specified_amountOf_data(garbage_data_len as byte)` — <b>METHOD. </b><br><br> Flushes a specified amount of garbage data which are present in the serial-port.<br><br> <b>Input parameters:</b> <ul> <li>datalen<font 
- `sub cell__ser_port_flush_all()` — <b>METHOD. </b><br><br> Flushes all data which are present in the serial-port.
- `sub cell__sock_release_all()` — <b>METHOD. </b><br><br> Releases all socks.
- `sub cell__sock_flush_all()` — <b>METHOD. </b><br><br> Flushes all data which are present in the sock.
- `sub cell__at_cmd_exec(byref atcmd as string,` — <b>METHOD. </b><br><br> Flushes all data which are present in the sock.
- `sub cell__sleeptimer(sleeptime as word)` — <b>METHOD. </b><br><br> Waits for a specified number of seconds.<br><br> <b>Input parameters:</b> <ul> <li>sleeptime<font color="magenta"> - </font><i>waiting-t
- `sub cell__at_send(atcmd as string)` — <b>METHOD. </b><br><br> Sends AT command.<br><br> <b>Input parameters:</b> <ul> <li>atcmd<font color="magenta"> - </font><i>Full AT command (<font color="dodger
- `sub cell__at_usermode_send(atcmd as string)` — <b>METHOD. </b><br><br> Sends AT command when in user mode.<br><br> <b>Input command:</b> <ul> <li>atcmd<font color="magenta"> - </font><i>Full AT command (<fon
- `sub cell__at_parse_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Sends AT command when in user mode.<br><br> <b>Input command:</b> <ul> <li>atcmd<font color="magenta"> - </font><i>Full AT command (<fon
- `sub cell__at_get_cleandata(byref atreply_checkitem as string(CELL__16b_LEN))` — <b>METHOD. </b><br><br> Gets a clean AT reply message without leading AT command, CR, and LF.<br><br> <b>Input parameters:</b> <ul> <li>atreply_checkitem<font c
- `sub cell__at_get_cleandata_filter(good_data_len as byte)` — <b>METHOD. </b><br><br> Retrieves only useful data and flushes all other (garbage) data.<br><br> <b>Input parameters:</b> <ul> <li>good_data_len<font color="mag
- `sub cell__at_parse_message_retry(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Retrieves only useful data and flushes all other (garbage) data.<br><br> <b>Input parameters:</b> <ul> <li>good_data_len<font color="mag
- `sub cell__at_get_voltage()` — <b>METHOD. </b><br><br> Gets the battery voltage.<br><br>
- `sub cell__at_send_multiple_commands_without_timeout(byref atcmd as string, numOf_times as byte,` — <b>METHOD. </b><br><br> Gets the battery voltage.<br><br>
- `sub cell__ppp_at_cgpaddr_retrieve_ip()` — <b>METHOD. </b><br><br> Gets the PPP remote IP address via the <font color="dodgerblue">AT+CGPADDR</font> command.</li>
- `function cell__ppp_generate_fcs(byref ppp_packet_format as string(CELL__128b_LEN)) as word` — <b>METHOD. </b><br><br> Generates an FCS based on the input value. For the generation of an FCS, the <font color="dodgerblue">CRC-16-CCITT 0x8408</font> polynom
- `sub cell__ppp_append_fcs(byref ppp_packet_format as string(CELL__128b_LEN), fcs as word)` — <b>METHOD. </b><br><br> Appends the generated FCS to the PPP packet format.<br><br> <b>Input parameters:</b> <ul> <li>ppp_packet_format<font color="magenta"> - 
- `sub cell__ppp_insert_escapechar(byref ppp_packet_format as string)` — <b>METHOD. </b><br><br> Inserts an escape character <font color="dodgerblue">0x7D</font> in the following situations: <ul> <li>chr(0x7E) is replaced as: <i>chr(
- `sub cell__ppp_increment_id()` — <b>METHOD. </b><br><br> Increments the identifier.<br><br>
- `sub cell__ppp_send_data(ppp_protocol as word, ppp_code as en_cell__op_ppp_codes, ppp_sender_id as byte, byref data_packet_format as string,` — <b>METHOD. </b><br><br> Increments the identifier.<br><br>
- `sub cell__ppp_ipcp_send_confreq(ppp_protocol as word, ppp_code as en_cell__op_ppp_codes, ppp_sender_id as byte, byref data_packet_format as string(CELL__128b_LEN),` — <b>METHOD. </b><br><br> Sends a PPP packet in the following format.<br> +------+------------+-----------+-----------+---------------------------+-------+------+
- `function cell__ppp_ping_generate_checksum(byref icmp_packet_format as string(CELL__32b_LEN), icmp_isSent as boolean) as dword` — <b>METHOD. </b><br><br> Generates 'Frame Check Sequence.<br><br> <b>Input parameters:</b> <ul> <li>icmp_packet_format<font color="magenta"> - </font><i>ICMP Mes
- `sub cell__ppp_ping_insert_checksum(byref icmp_packet_format as string(CELL__32b_LEN), fcs as dword)` — <b>METHOD. </b><br><br> Overwrites the Checksum with the generated Frame Check Sequence.<br><br> <b>Input parameters:</b> <ul> <li>icmp_packet_format<font color
- `sub cell__ppp_ping_send(ppp_protocol as word, ppp_code as en_cell__op_ppp_codes, ppp_sender_id as byte, byref icmp_packet_format as string(CELL__32b_LEN),` — <b>METHOD. </b><br><br> Overwrites the Checksum with the generated Frame Check Sequence.<br><br> <b>Input parameters:</b> <ul> <li>icmp_packet_format<font color
- `sub cell__ppp_substitute_data(byref sender_data as string(CELL__128b_LEN),` — <b>METHOD. </b><br><br> Sends a ping from Source IP to Destination IP.<br><br> <b>Input parameters:</b> <ul> <li>ppp_protocol<font color="magenta"> - </font><i>
- `sub cell__ppp_parse_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Replaces one data value (<font color="gray">e.g., CHAP: 0x0304 C223</font>) with another (<font color="gray">e.g., PAP: 0x0304 C023</fon
- `function cell__ppp_parse_message_func() as string(CELL__128b_LEN)` — <b>METHOD. </b><br><br> Parses a received PPP message and outputs <font color="dodgerblue">cell__reply</font>. Parsing process is as follows: <ul> <li>Strips of
- `sub cell__ppp_parse_message__retry()` — <b>METHOD. </b><br><br> Retries to parse a received message.
- `sub cell__ppp_proc_parsed_lcp_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Retries to parse a received message.
- `function cell__ppp_proc_parsed_lcp_confreq_message_result(byref parsed_message as string, byref confrej_str as string) as en_cell__op_ppp_sender_codes` — <b>METHOD. </b><br><br> Processes a parsed LCP CONFREQ message.<br><br> <b>Input parameters:</b> <ul> <li>parsed_message<font color="magenta"> - </font><i>Parse
- `sub cell__ppp_proc_parsed_lcp_message_confack_handler(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Processes a parsed LCP CONFREQ message.<br><br> <b>Input parameters:</b> <ul> <li>parsed_message<font color="magenta"> - </font><i>Parse
- `sub cell__ppp_proc_parsed_pap_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Handles the processes upon a CONFACK.<br><br> <b>Input args:</b> <ul> <li>next_pwr_phase: <i>next POWER phase</i> <li>next_at_phase: <i>
- `sub cell__ppp_proc_parsed_ipcp_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Processes received PAP parse messages.<br><br> <b>Input args:</b> <ul> <li>next_pwr_phase: <i>next POWER phase</i> <li>next_at_phase: <i
- `function cell__ppp_proc_parsed_ipcp_confreq_message_result(byref parsed_message as string(CELL__128b_LEN),` — <b>METHOD. </b><br><br> Processes received IPCP parse messages.<br><br> <b>Input args:</b> <ul> <li>next_pwr_phase: <i>next POWER phase</i> <li>next_at_phase: <
- `sub cell__ppp_proc_parsed_ipcp_message_confack_handler(ppp_peer_data as string, next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Processes a parsed IPCP CONFREQ message.<br><br> <b>Input parameters:</b> <ul> <li>parsed_message<font color="magenta"> - </font><i>Pars
- `sub cell__ppp_proc_parsed_ping_message(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Handles the processes upon a CONFACK.<br><br> <b>Input args:</b> <ul> <li>next_pwr_phase: <i>next POWER phase</i> <li>next_at_phase: <i>
- `sub cell_ppp_enable()` — <b>METHOD. </b><br><br> Enables PPP and sets all phases to IDLE-mode.
- `sub cell__ppp_link_to_tower()` — <b>METHOD. </b><br><br> Links to the Tower and sends a call-back.
- `sub cell__ppp_connection_status(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Links to the Tower and sends a call-back.
- `sub cell__ppp_check_connection_status(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD </b><br><br> Checks the PPP connection by trying to connect to a specific server.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color=
- `sub cell__gps_parse_message()` — <b>METHOD. </b><br><br> Gets and shows AT reply.
- `sub cell__gps_get_position(byref inputdata as string)` — <b>METHOD. </b><br><br> Extracts the latitude and longitude from the data.<br><br> <b>Input parameters:</b> <ul> <li>inputdata<font color="magenta"> - </font><i
- `sub cell__at_usermode_cmd_input(byref atcmd as string)` — <b>METHOD. </b><br><br> Gather AT command input.
- `sub cell__at_usermode_get_cmd_fifo()` — <b>METHOD. </b><br><br> Gets the oldest AT command first.
- `sub cell__at_usermode_go_into_idle(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,` — <b>METHOD. </b><br><br> Gets the oldest AT command first.
- `sub cell__at_notification(next_pwr_phase as en_cell__op_pwr_phases, next_at_phase as en_cell__op_at_phases,`
- `sub cell__at_usermode_sms_send(byref phonenumber as string(CELL__16b_LEN), byref sms_message_total as string,` — <b>METHOD. </b><br><br> Notifies that AT manual command mode is enabled.<br><br> <b>Input parameters:</b> <ul> <li>next_pwr_phase<font color="magenta"> - </font
- `sub cell__at_usermode_sms_receive(byref cpms_mem1_stor_type as string(CELL__2b_LEN),` — <b>METHOD. </b><br><br> Sends SMS messages to a specified phone-number.<br><br> <b>Input parameters:</b> <ul> <li>phonenumber<font color="magenta"> - </font><i>
- `sub cell__at_usermode_sms_parse()` — <b>METHOD. </b><br><br> Parses at-reply SMS messages.<br><br>
- `sub cell__proc_sys_timer()` — <b>METHOD. </b><br><br> Checks and handles <font color="dodgerblue">processes</font> periodically.
- `sub cell__isretry_inprogr_in_idlemode()` — <b>METHOD. </b><br><br> Checks whether there are any retries in progress while in IDLE-mode.
- `function cell__retry_in_progress() as boolean` — <b>METHOD. </b><br><br> Checks whether there are any retries in progress.
- `function cell__all_phases_are_idle() as boolean` — <b>METHOD. </b><br><br> Checks whether all the phases are set to IDLE.
- `sub cell__on_ser_data_arriv_not_trigg()` — <b>METHOD. </b><br><br> Checks whether on-ser-data-arrival is NOT triggered.
- `sub cell__pwr_proc_sys_timer()` — <b>METHOD. </b><br><br> Checks and handles <font color="dodgerblue">power processes</font> periodically.
- `sub cell__at_proc_sys_timer()` — <b>METHOD. </b><br><br> Checks and handles <font color="dodgerblue">AT processes</font> periodically.
- `sub cell__ppp_proc_sys_timer()` — <b>METHOD. </b><br><br> Checks and handles <font color="dodgerblue">PPP processes</font> periodically.
- `sub cell__gps_proc_sys_timer()` — <b>METHOD. </b><br><br> Checks and handles <font color="dodgerblue">GPS processes</font> periodically.
- `sub cell__proc_on_ser_data_arrival()` — <b>METHOD. </b><br><br> Processes data arriving via the data serial port.

Enums: `en_cell__status_phases`(CELL__START_INITIATED, CELL__STOP_INITIATED, CELL__START_BUFFER_SIZE_IS_SUFFICIENT, CELL__START_BUFFER_SIZE_IS_INSUFFICIENT); `en_cell__pwr_objects`(STATUS, PWRKEY, RESET, SHDN); `en_cell__op_pwr_phases`(PHASE_PWR_DONOT_CHANGE, PHASE_PWR_INIT, PHASE_PWR_DEINIT, PHASE_PWR_RESET_ON, PHASE_PWR_RESET_WAIT, PHASE_PWR_RESET_RETRY, PHASE_PWR_RESET_OFF, PHASE_PWR_PWRKEY_ON, PHASE_PWR_PWRKEY_OFF, PHASE_PWR_POWERING_ONOFF, PHASE_PWR_POWERING_ONOFF_WAIT, PHASE_PWR_POWERING_ONOFF_RETRY…); `en_cell__op_at_phases`(PHASE_AT_DONOT_CHANGE, PHASE_AT_INIT, PHASE_AT_AT, PHASE_AT_AMPERSAND_E1, PHASE_AT_AMPERSAND_C0, PHASE_AT_CPSMS_0, PHASE_AT_AMPERSAND_D0, PHASE_AT_CMNB, PHASE_AT_CGMM, PHASE_AT_CBC, PHASE_AT_CNMP, PHASE_AT_ATE1…); `en_cell__op_ppp_phases`(PHASE_PPP_DONOT_CHANGE, PHASE_PPP_LCP_PARSE_PROCESSING, PHASE_PPP_LCP_NEGOTIATION, PHASE_PPP_LCP_SEND, PHASE_PPP_MSG_LEN_NOTMATCH, PHASE_PPP_FCS_ISBAD, PHASE_PPP_ADDRESS_FIELD_NOTPRESENT, PHASE_PPP_CONTROL_FIELD_NOTPRESENT, PHASE_PPP_LCP_NEGO_SUCCESS, PHASE_PPP_RETRY_ERROR, PHASE_PPP_LCP_DISCREQ_BY_PEER, PHASE_PPP_LCP_DISCREQ_FROM_SENDER…); `en_cell__op_gps_phases`(PHASE_GPS_DONOT_CHANGE, PHASE_GPS_PARSE_MESSAGE, PHASE_GPS_CGPSNMEA, PHASE_GPS_CGPSHOR, PHASE_GPS_CGPS_ENABLE, PHASE_GPS_CGPSINFOCFG_START, PHASE_GPS_WAITFORDATA, PHASE_GPS_SIV, PHASE_GPS_POS, PHASE_GPS_IDLE); `en_cell__op_parse_phases`(PHASE_PARSE_DONOT_CHANGE, PHASE_PARSE_AT_MESSAGE, PHASE_PARSE_PPP_MESSAGE, PHASE_PARSE_GPS_MESSAGE, PHASE_PARSE_SMS_MESSAGE, PHASE_PARSE_IDLE); `en_cell__op_ppp_codes`(PPP_CONFREQ, PPP_CONFACK, PPP_CONFNAK, PPP_CONFREJ, PPP_ECHOREQ, PPP_DISREQ); `en_cell__op_ppp_peer_codes`(PPP_PEER_CONFREQ, PPP_PEER_CONFACK, PPP_PEER_CONFNAK, PPP_PEER_CONFREJ, PPP_PEER_DISREQ); `en_cell__op_ppp_sender_codes`(PPP_SENDER_CONFACK, PPP_SENDER_CONFNAK, PPP_SENDER_CONFREJ, PPP_SENDER_DISREQ); `en_cell__op_ppp_lcp_config_options`(CONFIG_OPTION_MRU, CONFIG_OPTION_ACCM, CONFIG_OPTION_AUTH, CONFIG_OPTION_MAGIC, CONFIG_OPTION_PFC, CONFIG_OPTION_ACFC); `en_cell__op_https_servers`(SERVER_GOOGLE, SERVER_TIBBO); `en_cell__op_ppp_ipcp_config_options`(CONFIG_OPTION_IP_COMPRESSION, CONFIG_OPTION_IP, CONFIG_OPTION_PRI_DNS, CONFIG_OPTION_SEC_DNS); `en_cell__pwr_callbacks`(CALLBACK_IS_POWERING_ONOFF_FAILED, CALLBACK_AT_CHECK_RDY_STATE, CALLBACK_IS_ON_AND_RDY, CALLBACK_IS_OFF, CALLBACKERR_INSUFFICIENT_BUFFER_SIZE); `en_cell__at_callbacks`(CALLBACK_AT_REPLY, CALLBACK_AT_REPLY_ERROR, CALLBACK_AT_NOTIFICATION, CALLBACK_AT_STORAGE_FULL, CALLBACK_AT_SMS_NOTIFICATION); `en_cell__ppp_callbacks`(CALLBACK_PPP_PARSE_MSG_NOT_FOUND, CALLBACK_PPP_MSG_LEN_NOTMATCH, CALLBACK_PPP_FCS_ISBAD, CALLBACK_PPP_ADDRESS_FIELD_NOTPRESENT, CALLBACK_PPP_CONTROL_FIELD_NOTPRESENT, CALLBACK_PPP_PROTOTYPE_ISNOT_LCP, CALLBACK_PPP_LCP_SUCCESSFUL, CALLBACK_PPP_RETRY_ERROR, CALLBACKERR_PPP_LCP_DISCREQ_BY_PEER, CALLBACKERR_PPP_LCP_DISCREQ_FROM_SENDER, CALLBACK_PPP_PAP_SUCCESSFUL, CALLBACK_PPP_PAP_FAILED…); `en_cell__gps_callbacks`(CALLBACK_GPS_SIV_OK, CALLBACK_GPS_POS_OK)

## cellular/cellular.tbh

Config defines (set before include):
- `CELL_COMMAND_QUEUE_SIZE` = 10
- `CELL_ECHO_MODE` = 1
- `LOG_ERROR` = 0
- `LOG_WARNING` = 1
- `LOG_INFO` = 2
- `LOG_DEBUG` = 3
- `CELL_LOG_LEVEL` = LOG_INFO

API:
- `sub cell_proc_timer()`
- `sub cell_init(byref apn as string, byref username as string, byref password as string, byref pin as string)`
- `sub cell_start()`
- `sub cell_stop()`
- `sub cell_proc_data()`
- `sub cell_send_sms(phone_number as string, message as string)`
- `sub cell_proc_sock_event(newstate as pl_sock_state, newstatesimple as pl_sock_state_simple)`
- `function cell_get_ip_address() as string`
- `function cell_get_operator() as string`
- `function ppp_create_frame(protocol as word, code as byte, id as byte, data as string) as string`
- `function cell_gps_get_data() as cell_gps_data_struct` — GPS functions
- `function cell_gps_is_fixed() as boolean`
- `sub cell_gps_enable()`
- `sub cell_gps_disable()`
- `function cell_gps_nmea_to_decimal(nmea_coord as string, direction as string) as float`

Callbacks YOU must implement:
- `sub callback_ppp_disconnected()`
- `sub callback_ppp_connected()`
- `sub callback_gps_data_updated()`
- `sub callback_sms_received(phone_number as string, message as string)`

Enums: `en_cell_states`(CELL_STATE_IDLE, CELL_STATE_POWER1, CELL_STATE_POWER2, CELL_STATE_POWER3, CELL_STATE_INIT, CELL_STATE_AT_TRY, CELL_STATE_GPS_ON, CELL_STATE_GPS_CHECK, CELL_STATE_ACTIVATE_MODEM, CELL_STATE_SET_CONNECT_RESULT_INFO, CELL_STATE_SET_CONNECT_RESULT_FORMAT, CELL_STATE_SET_BAUD…); `en_cell_gps_status`(GPS_STATUS_OFF, GPS_STATUS_SEARCHING, GPS_STATUS_FIXED, GPS_STATUS_ERROR); `en_cell_preferred_mode`(CELL_MODE_AUTO, CELL_MODE_GSM, CELL_MODE_WCDMA, CELL_MODE_LTE, CELL_MODE_TDS_CDMA, CELL_MODE_CDMA, CELL_MODE_EVDO, CELL_MODE_GSM_WCDMA, CELL_MODE_CDMA_EVDO, CELL_MODE_NO_LTE, CELL_MODE_GSM_TDSCDMA, CELL_MODE_GSM_WCDMA_TDSCDMA…); `en_cell__op_ppp_sender_codes`(PPP_SENDER_CONFACK, PPP_SENDER_CONFNAK, PPP_SENDER_CONFREJ, PPP_SENDER_DISREQ); `en_cell__op_ppp_peer_codes`(PPP_PEER_CONFREQ, PPP_PEER_CONFACK, PPP_PEER_CONFNAK, PPP_PEER_CONFREJ, PPP_PEER_DISREQ)

## cgg/cgg.tbh

Config defines (set before include):
- `CGG_DEBUG_PRINT` = 0 — Tibbo Congregate IOT Platform LIBRARY
- `CGG_MAX_SETTING_NAME_LENGTH` = 0
- `CGG_MAX_SETTINGS` = 0
- `CGG_DEVICE_PORT` = 3536
- `CGG_DESCRIPTOR_FILE` = "cgg.xtxt"

API:
- `sub cgg_start(byref server_address as string, byref device_token as string, byref device_name as string, target_interface as pl_sock_interfaces)`
- `sub cgg_soi_connect(server_address as string, device_token as string, target_interface as pl_sock_interfaces, ser_num as byte)`
- `sub cgg_send(name as string, value as string)`
- `sub cgg_proc_sock_event(newstate as pl_sock_state,newstatesimple as pl_sock_state_simple)`
- `sub cgg_proc_timer()`
- `sub cgg_proc_ser_data()`
- `sub cgg_proc_sock_data()`
- `sub cgg_proc_mqtt_notif(byref topic as string, byref data as string)`
- `sub cgg_proc_attribute_update(byref data as string)`
- `sub cgg_mqtt_ok()`
- `sub cgg_stg_post_set(byref stg_name_or_num as string, index as byte,byref stg_value as string)`

Callbacks YOU must implement:
- `sub callback_cgg_attribute_received(byref key as string, byref value as string)`

## dhcp/dhcp.tbh

Config defines (set before include):
- `DHCP_DEBUG_PRINT` = 0 — DHCP LIBRARY (Works with NET, WLN) 1- debug output in console. 0- no debug output.
- `DHCP_MAX_RETRIES` = 3 — The number of retries in a single batch of retries
- `DHCP_WAIT_TIME` = 2 — Maximum waiting time (in seconds) for the DHCP server to reply
- `DHCP_MAX_RETRY_DELAY` = 10 — Max delay (in seconds) between retries in a batch of retries (it is randomized between 1 and this constant for each retry)
- `DHCP_POST_FAIL_DELAY` = 60 - Delay (in seconds) between the batches of retries **[docs.tibbo.com: default = 180 с (lib_dhcp_defines)]**
- `DHCP_MAX_HOST_NAME_LEN` = 0 — Max device (host) name length

API:
- `function dhcp_get_info(info_element as dhcp_info_elements, byref extra_data as string) as string`
- `function dhcp_start(interface as pl_sock_interfaces, byref requested_ip as string, byref host_name as string) as en_dhcp_status_codes`
- `function dhcp_stop(interface as pl_sock_interfaces) as en_dhcp_status_codes`
- `sub dhcp_set_link_disconnect_behavior(interface as pl_sock_interfaces, behavior as no_yes)`
- `sub dhcp_proc_timer()`
- `sub dhcp_proc_data()`

Callbacks YOU must implement:
- `sub callback_dhcp_ok(renew as no_yes, interface as pl_sock_interfaces, byref ip as string, byref gateway_ip as string, byref netmask as string, lease_time as dword)` — Callback procedure, informs of the successul procurement of configuration parameters from the DHCP server. Procedure body has to be created elsewhere in the pro
- `sub callback_dhcp_failure(interface as pl_sock_interfaces,failure_code as en_dhcp_status_codes)` — Callback procedure, informs of the failure to procure configuration parameters from the DHCP server after DHCP_MAX_RETRIES. Procedure body has to be created els
- `sub callback_dhcp_pre_clear_ip(interface as pl_sock_interfaces)` — Callback procedure, informs of the fact that the IP address of the specified interface will be cleared to 0.0.0.0 and all socket connections currently operating
- `sub callback_dhcp_pre_buffrq(required_buff_pages as byte)` — Callback procedure, informs of the insufficient number of free buffer pages available for use by the library. Procedure body has to be created elsewhere in the 
- `sub callback_dhcp_buff_released()` — Callback procedure, informs of the release of buffer pages by the library. Procedure body has to be created elsewhere in the project (externally with respect to

Enums: `en_dhcp_status_codes`(DHCP_STATUS_OK, DHCP_STATUS_OUT_OF_SOCKETS, DHCP_STATUS_INVALID_INTERFACE, DHCP_STATUS_INSUFFICIENT_BUFFER_SPACE, DHCP_STATUS_FAILURE); `dhcp_info_elements`(DHCP_INFO_ELEMENT_REQUIRED_BUFFERS)

## dns/dns.tbh

Config defines (set before include):
- `DNS_DEBUG_PRINT` = 0 — DNS LIBRARY
- `DNS_DEFAULT_SERVER` = "8.8.8.8"
- `DNS_MAX_RETRIES` = 3
- `DNS_REPLY_TIMEOUT` = 10

API:
- `function dns_start(dns_sock_num as byte) as en_dns_status_codes`
- `function dns_connect(interface as pl_sock_interfaces, byref dns_server_ip as string, dns_port as word) as en_dns_status_codes`
- `function dns_current_domain() as string`
- `sub dns_disconnect()`
- `sub dns_query(byref question as string)`
- `sub dns_proc_data()`
- `sub dns_proc_timer()`
- `sub dns_stop()`

Callbacks YOU must implement:
- `sub callback_dns_failure(status as en_dns_status_codes)`
- `sub callback_dns_answer_acquired(return_type as en_dns_return_type, byref return_string as string)`
- `sub callback_dns_ok()`
- `sub callback_dns_pre_buffrq(num_of_pages_required as byte)`
- `sub callback_dns_buff_released()`

Enums: `en_dns_status_codes`(EN_STATUS_DNS_OK, EN_STATUS_DNS_NOT_STARTED, EN_STATUS_DNS_INVALID_SOCKET, EN_STATUS_DNS_INVALID_INTERFACE, EN_STATUS_DNS_INSUFFICIENT_BUFFER_SPACE, EN_STATUS_DNS_CONNECTION_TIMEOUT, EN_STATUS_DNS_REPLY_TIMEOUT, EN_STATUS_DNS_RECURSIVE_UNAVALIABLE, EN_STATUS_DNS_NAME_ERROR, EN_STATUS_DNS_NO_ANSWER, EN_STATUS_DNS_BAD_ANSWER, EN_STATUS_DNS_REQUEST_IN_PROGRESS…); `en_dns_return_type`(EN_DNS_RET_IP, EN_DNS_RET_NAME_SERVER, EN_DNS_RET_CANONICAL_NAME, EN_DNS_RET_POINTER_RECORD, EN_DNS_RET_HOST_INFO, EN_DNS_RET_MAIL_EXCHANGE_SERVER)

## dsman/net_cmd.tbh

Config defines (set before include):
- `LOGIN_TOUT_CONST` = 600 — ============================================================= NET_CMD.TBS =============================================================
- `MAX_NUM_SDF_LINES` = 14
- `MAX_NET_CMD_LEN` = 131
- `MAX_NET_RPL_LEN` = 255
- `NUM_VSPD_SER_PORTS` = 0
- `SDF_FILE` = "sdf.xtxt"
- `NCMD_TX_BUF_SIZE` = 2
- `NCMD_RX_BUF_SIZE` = 2

API:
- `sub net_cmd_init`
- `sub net_cmd_proc(cmd_mode as cmd_modes, error_mode as no_yes)`
- `sub sock_closed_check_net_login(sock_num as byte)`

## filenum/filenum.tbh

Config defines (set before include):
- `FILENUM_DEBUG_PRINT` = 0 — FILE NUMBER ALLOCATION LIBRARY
- `FILENUM_MAX_SIGNATURE_LEN` = 0 — Maximum length of the file number user's signature string
- `FILENUM_MAX_FILENAME_LEN` = 0
- `FILENUM_MAX_FILES` = 32

API:
- `function filenum_open(byref signature as string, byref filename as string, byref status as pl_fd_status_codes) as byte`
- `function filenum_get(byref signature as string) as byte`
- `function filenum_who_uses(file_num as byte) as string`
- `sub filenum_release(file_num as byte)`

## gprs/gprs.tbh

Config defines (set before include):
- `SUPPORTS_GPRS` = 0 — GPRS LIBRARY (Works with TELIT GC864 GPRS module) 0- GPRS disabled (library code won't be compiled into the project) 1- GPRS enabled
- `GPRS_DEBUG_PRINT` = 0 — 0- no debug output. 1- debug output in console.
- `GPRS_SEND_PING` = 0 — 0- suppress pinging. 1- ping GPRS_PING_IP in the end of PPP link establishment (as a proof of success).
- `GPRS_PING_IP` = "0.0.0.0" — This is the IP address that will be pinged when GPRS_SEND_PING is set. Only relevant when GPRS_SEND_PING is 1.
- `GPRS_SER_PORT` = 3 — The serial port to which the GPRS modem is connected. Default=3. Like with ser.num, serial ports are numbered from 0. Keep at default value for NB1010 and DS101x devices.
- `GPRS_MODULE_EXTERNAL` = 0 - 0- the GPRS module is external, GPRS_SWITCH and GPRS_RESET GPIO lines are not in use, there is no startup delay- the GPRS module is supposed to be up and running by the time gprs_start() is called 1- the GPRS module is i **[docs.tibbo.com: смысл значений обратный: 0 - модуль встроенный (NB1010, DS101x), линии GPRS_SWITCH/GPRS_RESET используются, есть сброс и задержка старта; 1 - внешний модуль, линии не используются (lib_gprs_defines). Сверь с комментарием в своей gprs.tbh]**
- `GPRS_SWITCH` = 54 - GPIO line that, when set LOW, diverts traffic on GPRS_SER_PORT to the GPRS module. When the line is HIGH or disabled, serial port traffic goes elsewhere in the device. Only relevant when GPRS_MODULE_EXTERNAL is 0 Define **[docs.tibbo.com: там же описан `GPRS_RESET` (default = 55): HIGH - модуль в сбросе, LOW - работа; только при GPRS_MODULE_EXTERNAL = 0. А также `GPRS_SER_PORT_RTSMAP`/`GPRS_SER_PORT_CTSMAP` - линии RTS/CTS порта модема, по умолчанию равны номеру GPRS_SER_PORT]**
- `GPRS_PAYLOAD_SIZE` = 4 — Size of TCP and UDP packets that the GPRS interface will be able to carry, expressed in 256-byte units. Do not set >4 or <1.

API:
- `function gprs_get_info(info_element as gprs_info_elements, byref extra_data as string) as string`
- `function gprs_start(byref at_dt_command_param as string, byref apn as string, byref username as string, byref password as string) as en_gprs_status_codes`
- `sub gprs_stop()`
- `sub gprs_proc_ser_data()`
- `sub gprs_proc_sock_data()`
- `sub gprs_proc_timer()`

Callbacks YOU must implement:
- `sub callback_gprs_pre_buffrq(required_buff_pages as byte)` — Callback procedure, informs of the insufficient number of free buffer pages available for use by the library. Procedure body has to be created elsewhere in the 
- `sub callback_gprs_ok()` — Callback procedure, informs of the successul establishment of the PPP link. Procedure body has to be created elsewhere in the project (externally with respect t
- `sub callback_gprs_failure()` — Callback procedure, informs that PPP login/configuration or established link failed. Procedure body has to be created elsewhere in the project (externally with 

Enums: `en_gprs_status_codes`(GPRS_STATUS_OK, GPRS_STATUS_INSUFFICIENT_BUFFER_SPACE); `gprs_info_elements`(GPRS_INFO_ELEMENT_REQUIRED_BUFFERS)

## http/http.tbh

Config defines (set before include):
- `HTTP_DNS_SERVER` = "8.8.8.8"
- `HTTP_TX_BUFF` = 2
- `HTTP_RX_BUFF` = 2
- `HTTP_TIMEOUT` = 30
- `HTTP_MAX_QUEUE` = 5
- `HTTP_TLS_BUFF_PAGES` = 40
- `SUPPORTS_TLS` = 1

API:
- `function http_request(method as HTTP_REQUEST_METHODS, byref url as string, interface as pl_sock_interfaces, byref data as string, id as word) as byte`
- `function http_request_long(method as HTTP_REQUEST_METHODS, byref url as string, interface as pl_sock_interfaces, request_length as dword, id as word) as byte`
- `function http_encode_url(unencoded_url as string) as string`
- `function http_decode(encoded_string as string) as string`
- `function http_send_post_data(byref data as string) as word`
- `function http_get_domain_name(url as string) as string`
- `sub http_start()`
- `sub http_stop()`
- `sub http_proc_data()`
- `sub http_sock_state_update(newstatesimple as enum pl_sock_state_simple)`
- `sub http_on_sock_data_sent()`
- `sub http_proc_timer()`
- `sub http_dns_failure()`
- `sub http_dns_answer_acquired(return_type as en_dns_return_type, byref return_string as string)`
- `sub http_send_headers(header_name as string, header_value as string)`
- `sub http_on_sock_data_sent()`

Callbacks YOU must implement:
- `function callback_http_open_romfile() as dword` — open the romfile that contains the certificate for the current domain
- `sub callback_http_header_arrival(byref header_type as string, byref header_value as string)` — open the romfile that contains the certificate for the current domain
- `sub callback_http_content_arrival(byref data as string)`
- `sub callback_http_send_post_data(remaining_content_length as dword)`
- `sub callback_http_post_data_sent_ok()`
- `sub callback_http_response_code_arrival(byref http_response as string)`
- `sub callback_http_headers_complete()`
- `sub callback_http_request_complete()`
- `sub callback_http_request_failed(byref error_message as string)`
- `sub callback_http_send_headers()`

Enums: `HTTP_REQUEST_METHODS`(HTTP_GET, HTTP_HEAD, HTTP_POST, HTTP_PUT, HTTP_DELETE, HTTP_PATCH); `http_reply_states`(FREE, DNS_NOT_COMPLETE, DNS_REQUEST_SENT, DNS_COMPLETE, REQUEST_SENT, HTTP_RESPONSE_PROCESSED, HTTP_RESPONSE_HEADER_NAME, HTTP_RESPONSE_HEADER_VALUE, HTTP_HEADERS_PROCESSED)

## http_server/http_server.tbh


API:
- `sub http_server_start()`
- `sub http_server_proc_sock_data()`
- `sub http_server_proc_sock_event(newstate as pl_sock_state,newstatesimple as pl_sock_state_simple)`
- `sub http_server_proc_timer()`
- `sub http_server_proc_sock_data_sent()`
- `sub http_server_response_status(code as word)`
- `sub http_server_response_header(byref header as string(50), byref value as string)`
- `sub http_server_response_header_end()`
- `sub http_server_proc_timer()`
- `function http_server_decode(byref encoded_string as string) as string`
- `function http_server_find_param(byref http_req_string as string, byref argument as string) as string`
- `function http_server_get(socket_num as byte) as byte`

Callbacks YOU must implement:
- `sub callback_http_server_header_received(byref server as http_server_state, byref header as string, byref value as string)`
- `sub callback_http_server_body_received(byref server as http_server_state, byref body as string)`
- `function callback_http_server_endpoint_called(byref server as http_server_state) as boolean`

Enums: `http_server_op_state`(HTTP_SERVER_STATE_IDLE, HTTP_SERVER_STATE_RQ_METHOD, HTTP_SERVER_STATE_RQ_URI, HTTP_SERVER_STATE_RQ_PROTOCOL, HTTP_SERVER_STATE_RQ_HEADER, HTTP_SERVER_STATE_RQ_BODY, HTTP_SERVER_STATE_RS_HEADER_START, HTTP_SERVER_STATE_RS_HEADER, HTTP_SERVER_STATE_RS_BODY, HTTP_SERVER_STATE_RS_BODY_CONTENT, HTTP_SERVER_STATE_END)

## lcd/lcd_graph.tbh

Config defines (set before include):
- `LCD_GRAPH_LABELS` = 10
- `LCD_GRAPH_MAX_POINTS` = 30

API:
- `sub lcd_graph_start(min as real, max as real)`
- `sub lcd_graph_init(byref widget as lcd_graph_widget)`
- `sub lcd_graph_add_point(y as real)`
- `sub lcd_draw_graph(byref widget as lcd_graph_widget)`
- `sub lcd_graph_clear()`

## luis/luis.tbh

Config defines (set before include):
- `LUIS_DEBUG_PRINT` = 0 — LUIS LIBRARY 1- debug output in console. 0- no debug output.
- `LUIS_BT_RX_BUF_SIZE` = 5 — Size of Bluetooth RX Buffer (in pages)
- `LUIS_BT_TX_BUF_SIZE` = 5 — Size of Bluetooth TX Buffer (in pages)
- `LUIS_HTML_FILE` = "luis.html"
- `LUIS_BT_ENABLED` = 1

API:
- `function luis_start(byref bt_name as string) as en_luis_status_codes` — Boots the WA2000, enables Bluetooth, and sets the advertised name of the device
- `sub luis_stop()` — disables LUIS library
- `function luis_on_bt_data_arrival() as en_luis_status_codes` — Call this from on_bt_data_arrival()
- `sub luis_on_bt_data_sent()` — Call this from on_bt_data_sent()
- `sub luis_on_bt_event(bt_event as enum pl_bt_events)` — Call this from on_bt_event()

Callbacks YOU must implement:
- `sub callback_luis_bt_connected()` — Callback procedure, a host device has connected via Bluetooth.<br/> Procedure body has to be created elsewhere in the project (externally with respect to the li
- `sub callback_luis_bt_disconnected()` — Callback procedure, a host device has disconnected.<br/> Procedure body has to be created elsewhere in the project (externally with respect to the library).
- `sub callback_luis_bt_enabled()` — Callback procedure, Bluetooth has been enabled successfully.<br/> luis_start() is partially asynchronous. This sub is called after Bluetooth interface becomes r
- `sub callback_luis_bt_disabled()` — Callback procedure, indicates that the Bluetooth has failed. Call luis_start() to restart it.<br/> Procedure body has to be created elsewhere in the project (ex
- `function callback_luis_read(byref name as string, byref value as string) as boolean` — Callback procedure, indicates that the Bluetooth has failed. Call luis_start() to restart it.<br/> Procedure body has to be created elsewhere in the project (ex
- `function callback_luis_write(byref name as string, byref value as string) as boolean`

Enums: `en_luis_status_codes`(EN_LUIS_STATUS_OK, EN_LUIS_STATUS_NOT_STARTED, EN_LUIS_BT_FAILURE, EN_LUIS_FILE_HTML_ERROR, EN_LUIS_FILE_CONFIG_ERROR)

## modbus/modbus.tbh

Config defines (set before include):
- `MODBUS_TIMEOUT` = 500
- `MODBUS_MAX_REQUESTS` = 20
- `MODBUS_DEBUG_PRINT` = 0
- `MODBUS_FRAME_DELAY_MS` = 10

API:
- `function modbus_initialize() as boolean`
- `function modbus_callback_ReadCoilStatus(address as word) as boolean`
- `function modbus_callback_ReadInputStatus(address as word) as boolean`
- `function modbus_callback_WriteSingleCoil(address as word, value as low_high) as byte`
- `function modbus_callback_ReadHoldingRegister(address as word) as word`
- `function modbus_callback_ReadInputRegister(address as word) as word`
- `function modbus_callback_set_holding_register(address as word, data as word) as boolean`
- `function modbus_read_word(byref bytes as byte(255), start as byte) as word`
- `function modbus_queue_get_count() as byte`
- `function modbus_crc16(data as byte(255), byte_cnt as byte) as word`
- `function modbus_queue_pop() as modbus_request_item`
- `function modbus_print_packet(byref s as string) as string`
- `sub modbus_master_receive(recv_data as string, protocol as modbusProtocol)`
- `sub modbus_slave_receive(byref recv_data as string, interface_number as byte, protocol as modbusProtocol)`
- `sub modbus_master_request(devaddr as byte, request as byte, start as word, count as word, regdata as string, interface_number as byte, protocol as modbusProtocol, transactionId as word)`
- `sub modbus_queue_clear()`
- `sub modbus_proc_timer()`
- `sub modbus_proc_ser_data_sent()`
- `sub modbus_send(interface_number as byte, protocol as modbusProtocol, transactionId as word, protocolId as word, modbusUnitId as byte, modbusFunction as modbusFunc, byref data as string)`
- `sub modbus_master_send_next()`
- `function modbus_parse_response(byref data as string, data_type as modbusDataType, endianness as modbusEndianness) as float`
- `function modbus_request_exists(request_function as byte, device_id as byte, start_register as word, count as word, interface_number as byte, protocol as modbusProtocol) as no_yes`

Callbacks YOU must implement:
- `sub callback_modbus_slave_reply(byref request_item as modbus_request_item, byref reply as string)`
- `sub callback_modbus_slave_reply_timeout(byref request_item as modbus_request_item)`

Enums: `modbusProtocol`(modbus_TCP, modbus_RTU); `modbusFunc`(ReadCoilStatus, ReadInputStatus, ReadHoldingRegisters, ReadInputRegisters, WriteSingleCoil, PresetSingleRegister, WriteMultipleCoils, PresetMultipleRegisters); `modbusDataType`(modbus_float, modbus_signed, modbus_unsigned); `modbusEndianness`(modbus_big, modbus_little)

## mqtt/mqtt.tbh

**Предел сообщения.** `mqtt_publish(byref topic, byref data, …)` строит пакет одной строкой `chr(0)+chr(len(topic))+topic+data`
(`dim buf as string`, 255 байт): данные длиннее ~(253 - длина топика) обрезаются без ошибки, `MQTT_LARGE_PACKETS` и
`MQTT_TX_BUFF` этого не меняют. Длинную телеметрию шли несколькими сообщениями (проверено на коде библиотеки из AppBlocks, ноябрь 2026).

Config defines (set before include):
- `MQTT_LARGE_PACKETS` = 0 — MQTT Library
- `MQTT_DEBUG_PRINT` = 0
- `MQTT_RX_BUFF` = 16 **[docs.tibbo.com: в старой версии библиотеки default = 1 страница; размер подбирай под длину топиков и сообщений]**
- `MQTT_TX_BUFF` = 16 **[docs.tibbo.com: в старой версии default = 1]**
- `MQTT_TLS_BUFF_PAGES` = 40
- `MQTT_PING_TIMER` = 60
- `MQTT_CONNECTION_TIMER` = 30
- `MQTT_RECONNECT_TIME` = 10

API:
- `sub mqtt_start(target_interface as pl_sock_interfaces, byref server as string,dst_port as word,byref user as string,byref password as string,byref client_id as string, encrypted as boolean)` — API procedure, starts the MQTT library. MUST be called first, before any other procedure in this library is used.
- `function mqtt_connect() as ok_ng` — API function, instructs the library to connect to the MQTT server (broker).<br><br> <b>dst_ip</b>- the IP address of the MQTT server,<br> <b>dst_port</b>- targe
- `sub mqtt_disconnect()` — API procedure, disconnects the device from the MQTT server (broker).
- `sub mqtt_publish(byref topic as string, byref data as string, qos as en_qos_choices, retain as boolean)` — API procedure, publishes a <b>topic</b> and its <b>data</b> to the MQTT server (broker).
- `sub mqtt_sub(byref topic as string, qos as en_qos_choices)` — API procedure, subscribes the device to the specified topic on the MQTT server (broker).<br><br> <b>topic</b>- the topic to subscribe to,<br> <b>qos</b>- reques
- `sub mqtt_unsub(byref topic as string)` — API procedure, unsubscribes the device from the specified topic.<br><br> <b>topic</b>- message to unsubscribe from.
- `sub mqtt_dns_answer_acquired(return_type as en_dns_return_type, byref return_string as string)` — API procedure, unsubscribes the device from the specified topic.<br><br> <b>topic</b>- message to unsubscribe from.
- `sub mqtt_proc_timer()` — Event procedure, call it from the on_sys_timer() event handler.
- `sub mqtt_proc_data()` — Event procedure, call it from the on_sock_data_arrival event handler.
- `sub mqtt_start_publish(byref topic as string, qos as en_qos_choices, length as dword, retain as boolean)` — API procedure, starts the procedure of publishing to the MQTT server (broker). Must be called before calling mqtt_continue_publish(). <b>topic</b> - Name of the
- `sub mqtt_continue_publish(byref data as string)` — API procedure, continues publishing to the MQTT server (broker). Must be called until the number of bytes set in mqtt_start_publish() has been reached. <b>data<
- `sub mqtt_stop()`
- `sub mqtt_sock_event(newstate as enum pl_sock_state, newstatesimple as enum pl_sock_state_simple)`
- `sub mqtt_send_data(data as string)`

Callbacks YOU must implement:
- `sub callback_mqtt_connect_ok()` — MQTT callback procedure. Must be implemented elsewhere in the user's program. Called when the device successfully connects to the MQTT server.
- `sub callback_mqtt_connect_lost()` — MQTT callback procedure. Must be implemented elsewhere in the user's program. Called when connection to the MQTT server is lost.
- `sub callback_mqtt_sub_ok()` — MQTT callback procedure. Must be implemented elsewhere in the user's program. Called on the subscriber when the MQTT server confirms the requested subscription.
- `sub callback_mqtt_notif(byref topic as string,byref data as string,remaining_bytes as dword)` — MQTT callback function. Must be implemented elsewhere in the user's program. Called when the subscriber receives a message from the MQTT server for the topic th

Enums: `en_qos_choices`(QOS_AT_MOST_ONCE, QOS_AT_LEAST_ONCE, QOS_EXACTLY_ONCE); `en_mqtt_states`(EN_MQTT_STATES_IDLE, EN_MQTT_STATES_NOT_CONNECTED, EN_MQTT_STATES_DNS_NOT_COMPLETE, EN_MQTT_STATES_CONNECTING, EN_MQTT_STATES_CONNECTED, EN_MQTT_STATES_LOGGED_IN); `en_mqtt_message_types`(CONNECT, CONNACK, PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP, SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, PINGREQ…); `en_mqtt_proc_data_states`(EN_MQTT_PD_STATES_READING_HEADER, EN_MQTT_PD_STATES_READING_PAYLOAD, EN_MQTT_PD_STATES_READING_PAYLOAD_DATA)

## pic/PIC_HAL.tbh


API:
- `function pic_reg_read(addr as word,length as byte) as string` — Read the specified number of bytes from consequent PIC memory locations beginning from the specified address.
- `function pic_reg_write(addr as word, data as string) as ok_ng` — Write the specified number of bytes into consequent PIC memory locations beginning from the specified address.
- `sub pic_reset(scl as pl_io_num,sda as pl_io_num,rst as pl_io_num)` — Calling this sub will hardware-reset the PIC micro.
- `function pic_get_fw_version() as string` — Call this function to obtain the version string for the firmware currently running on the PIC micro. The version will always be in the NNN Vxx.yy format, where 

Enums: `pic_adc_enum`(PIC_ADC0, PIC_ADC1, PIC_ADC2, PIC_ADC3, PIC_ADC4, PIC_ADC5); `pic_pin_enum`(PIC_PIN0, PIC_PIN1, PIC_PIN2, PIC_PIN3, PIC_PIN4, PIC_PIN5); `pic_pwm_enum`(PIC_PWM0, PIC_PWM1, PIC_PWM2); `pic_prescaler_enum`(PIC_PRE_64, PIC_PRE_16, PIC_PRE_4, PIC_PRE_1); `pic_brate_enum`(PIC_BRATE_300, PIC_BRATE_600, PIC_BRATE_1200, PIC_BRATE_2400, PIC_BRATE_4800, PIC_BRATE_9600, PIC_BRATE_19200, PIC_BRATE_38400, PIC_BRATE_57600)

## pic/PIC_LVP.tbh

Config defines (set before include):
- `PIC_LVP_MAX_DATA_LEN` = 8192
- `PIC_LVP_MAX_EEPROM_LEN` = 256
- `PIC_LVP_MAX_CFG_LEN` = 16
- `PIC_LVP_MAX_USER_ID_LEN` = 4
- `PIC_LVP_MAX_TRY_FLASHING` = 4
- `PIC_LVP_DEBUG_PRINT` = 1

API:
- `sub pic_lvp_start(target as PIC_TYPE, SCL as byte, SDA as byte, MCLR as byte)`
- `function pic_lvp_upload_firmware(byref fwname as string) as boolean`

Enums: `PIC_TYPE`(PIC_16F1826, PIC_16F1827, PIC_16LF1826, PIC_16LF1827, PIC_16F1823, PIC_16LF1823, PIC_12F1822, PIC_12LF1822, PIC_16F1824, PIC_16LF1824, PIC_16F1825, PIC_16LF1825…)

## pic/pic_gra.tbh

Config defines (set before include):
- `PIC_CLK_PIN` = PL_IO_NULL
- `PIC_DATA_PIN` = PL_IO_NULL
- `PIC_RST_PIN` = PL_IO_NULL
- `PIC_INT_PIN` = PL_IO_NULL
- `TBT_CLK_SOURCE` = INTERNAL_OSCILLATOR_FREQ_32MHZ_HF

API:
- `function pic_init(byref signature as string, use_ssi as no_yes, byref fw_str as string, clk_pin as byte, data_pin as byte, rst_pin as byte, int_pin as byte, byref channel as byte)as pic_result_enum` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub pic_config(num as pic_pin_enum, f as pic_func_enum, int_pin as byte, channel as byte)` — Call this sub to define the IO pin function separately for each pin. Note that somes pins do not support all functions: IO -- all pins. ADC -- all pins. PWM -- 
- `sub pic_io_enabled(num as pic_pin_enum, en as no_yes, channel as byte)` — Configures the specified IO pin to be an input (en=NO) or outpur (en=YES). This will only work for pins running in the IO mode [see pic_config()].
- `sub pic_io_set(num as pic_pin_enum, state as low_high, channel as byte)` — Sets the output state of the specified IO pin. This will only work for pins running in the IO mode [see pic_config()] and configured as outputs [see pic_io_enab
- `function pic_io_get(num as pic_pin_enum, channel as byte)as low_high` — Reads the state of the specified IO pin. This will only work for pins running in the IO mode [see pic_config()].
- `sub pic_adc_config( p as pic_adc_ref_positive_voltage,n as pic_adc_ref_negative_voltage,Vfvr as pic_adc_fvr_scale, channel as byte)` — Configures the input range for all four ADC channels. Note that selecting VCC makes inputs "ratiometric" i.e. dependent on the actual VCC voltage value. 2048mV 
- `function pic_adc_get_mv(ch as pic_adc_enum, channel as byte) as word` — Performs ADC conversion for the specified channel and returns conversion result expressed in mV. This will only work for channels whose corresponding pins are r
- `function pic_adc_get(ch as pic_adc_enum, channel as byte) as word` — Performs ADC conversion for the specified channel. This will only work for pins running in the ADC mode [see pic_config()]. The range is from 0 (0V) to 1023 (re
- `sub pic_pwm_config(ch as pic_pwm_enum, pulse_width as word, period as word, prescaler as pic_prescaler_enum, channel as byte)` — Sets the operation parameters for the selected PWM channel. This will only work for channels whose corresponding pins are running in the PWM mode [see pic_confi
- `sub pic_pwm_start(ch as pic_pwm_enum, channel as byte)` — Enables PWM output for the specified PWM channel. This will only work for channels whose corresponding pins are running in the PWM mode [see pic_config()] and w
- `sub pic_pwm_stop(ch as pic_pwm_enum, channel as byte)` — Disables PWM output for the specified PWM channel. This will only work for channels whose corresponding pins are running in the PWM mode [see pic_config()].
- `sub pic_pwm_output(ch as pic_pwm_enum, frequency as float, duty_cycle as byte, channel as byte)` — Disables PWM output for the specified PWM channel. This will only work for channels whose corresponding pins are running in the PWM mode [see pic_config()].
- `sub pic_pwm_duty(ratio0 as word, ratio1 as word, ratio2 as word, channel as byte)` — Simultaneously sets the duty cycle ratio for all three PWM channels. The ratio for each channel is expressed in 0.1% units. This will only work for channels who
- `sub pic_pwm_duty_set(ratio as word, pwm_channel as byte, channel as byte)` — Sets the duty cycle ratio for one PWM channel
- `sub pic_ser_config(br as pic_brate_enum, par as pic_parity_mode_enum, irq_enabled as no_yes, channel as byte)` — Sets the communication parameters for the UART: the baudrate, parity mode, and whether the RX interrupt will be generated on the interface line 3 whenever there
- `sub pic_ser_setsend(data as string, channel as byte)` — Sends the string of data out of the serial port. This is a synchronous call: the sub is exited only after all data is sent out. For this sub to work, UART must 
- `function pic_ser_get(channel as byte) as string` — Reads data from PIC's RX buffer. The buffer is maintained by the GRA firmware and can fit up to 64 bytes. For this sub to work, UART must be preset using pic_se
- `function pic_ser_txlen(channel as byte)as byte` — Returns the number of bytes currently waiting in the TX buffer. The buffer is maintained by the GRA firmware and can fit up to 80 bytes.
- `function pic_ser_rxlen(channel as byte)as byte` — Returns the number of bytes currently waiting in the RX buffer. The buffer is maintained by the GRA firmware and can fit up to 80 bytes.

Enums: `pic_result_enum`(PIC_OK, PIC_NG, PIC_REJ, PIC_FWNG); `pic_adc_ref_positive_voltage`(PIC_PREF_SOURCE_VDD, PIC_PREF_SOURCE_PIN_4, PIC_PREF_SOURCE_FVR_BUF); `pic_adc_ref_negative_voltage`(PIC_NREF_SOURCE_VSS, PIC_NREF_SOURCE_PIN_5); `pic_adc_fvr_scale`(PIC_ADC_FVR_REF_OFF, PIC_ADC_FVR_REF_2048mV, PIC_ADC_FVR_REF_4096mV); `pic_func_enum`(PIC_FUNC_NULL, PIC_FUNC_IO, PIC_FUNC_ADC, PIC_FUNC_PWM, PIC_FUNC_UART); `pic_parity_mode_enum`(PIC_PARITY_NONE, PIC_PARITY_EVEN, PIC_PARITY_ODD, PIC_PARITY_MARK, PIC_PARITY_SPACE)

## pic/tbt_pic_gra.tbh


API:
- `function tbt_pic_gra_reg_read(addr as word,length as byte) as string` — Read the specified number of bytes from consequent PIC memory locations beginning from the specified address.
- `function tbt_pic_gra_reg_write(addr as word, data as string) as ok_ng` — Write the specified number of bytes into consequent PIC memory locations beginning from the specified address.
- `sub tbt_pic_gra_reset(scl as pl_io_num,sda as pl_io_num,rst as pl_io_num)` — Calling this sub will hardware-reset the PIC micro.
- `function tbt_pic_gra_get_fw_version() as string` — Call this function to obtain the version string for the firmware currently running on the PIC micro. The version will always be in the NNN Vxx.yy format, where 
- `function tbt_pic_gra_init(byref signature as string, byref tbt as tbt_pic_gra, use_ssi as no_yes, byref fw_str as string)as tbt_pic_gra_result` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt_pic_gra_debug_print(data as string)`
- `sub tbt_pic_gra_config(byref tbt as tbt_pic_gra, num as tbt_pic_gra_pin_enum, f as tbt_pic_gra_func_enum)` — Call this sub to define the IO pin function separately for each pin. Note that somes pins do not support all functions: IO -- all pins. ADC -- all pins. PWM -- 
- `sub tbt_pic_gra_pwm_config_simple(byref tbt as tbt_pic_gra, ch as tbt_pic_gra_pwm_enum, frequency as real, duty as real)` — Call this sub to define the IO pin function separately for each pin. Note that somes pins do not support all functions: IO -- all pins. ADC -- all pins. PWM -- 

Enums: `tbt_pic_gra_osc_src`(INTERNAL_OSCILLATOR_FREQ_31KHZ_LF, INTERNAL_OSCILLATOR_FREQ_31_25KHZ_MF, INTERNAL_OSCILLATOR_FREQ_31_25KHZ_HF, INTERNAL_OSCILLATOR_FREQ_62_5KHZ_MF, INTERNAL_OSCILLATOR_FREQ_125KHZ_MF, INTERNAL_OSCILLATOR_FREQ_125KHZ_HF, INTERNAL_OSCILLATOR_FREQ_250KHZ_MF, INTERNAL_OSCILLATOR_FREQ_250KHZ_HF, INTERNAL_OSCILLATOR_FREQ_500KHZ_MF, INTERNAL_OSCILLATOR_FREQ_500KHZ_HF, INTERNAL_OSCILLATOR_FREQ_1MHZ_HF, INTERNAL_OSCILLATOR_FREQ_2MHZ_HF…); `tbt_pic_gra_prescaler`(PIC_PRE_64, PIC_PRE_16, PIC_PRE_4, PIC_PRE_1); `tbt_pic_gra_regs`(PIC_PORTA, PIC_PORTC, PIC_PIE1, PIC_OSCCON, PIC_APFCON0, PIC_APFCON1, PIC_ANSELA, PIC_ANSELC, PIC_TRISA, PIC_TRISC, PIC_LATA, PIC_LATC…); `tbt_pic_gra_result`(PIC_OK, PIC_NG, PIC_REJ, PIC_FWNG); `tbt_pic_gra_pin_enum`(PIC_PIN0, PIC_PIN1, PIC_PIN2, PIC_PIN3, PIC_PIN4, PIC_PIN5); `tbt_pic_gra_func_enum`(PIC_FUNC_NULL, PIC_FUNC_IO, PIC_FUNC_ADC, PIC_FUNC_PWM, PIC_FUNC_UART); `tbt_pic_gra_adc_enum`(PIC_ADC0, PIC_ADC1, PIC_ADC2, PIC_ADC3, PIC_ADC4, PIC_ADC5); `tbt_pic_gra_pwm_enum`(PIC_PWM0, PIC_PWM1, PIC_PWM2); `tbt_pic_gra_adc_ref_positive_voltage`(PIC_PREF_SOURCE_VDD, PIC_PREF_SOURCE_PIN_4, PIC_PREF_SOURCE_FVR_BUF); `tbt_pic_gra_adc_ref_negative_voltage`(PIC_NREF_SOURCE_VSS, PIC_NREF_SOURCE_PIN_5); `tbt_pic_gra_adc_fvr_scale`(PIC_ADC_FVR_REF_OFF, PIC_ADC_FVR_REF_2048mV, PIC_ADC_FVR_REF_4096mV)

## pppoe/pppoe.tbh

Config defines (set before include):
- `PPPOE_DEBUG_PRINT` = 0 — PPPOE LIBRARY 1- debug output in console. 0- no debug output.

API:
- `function pppoe_start(byref login as string, byref password as string) as en_pppoe_status_codes`
- `sub pppoe_stop()`
- `sub pppoe_proc_data()`
- `sub pppoe_proc_timer()`

Callbacks YOU must implement:
- `sub callback_pppoe_pre_buffrq(required_buff_pages as byte)`
- `sub callback_pppoe_ok()`
- `sub callback_pppoe_failure(pppoe_code as en_pppoe_status_codes)`

Enums: `en_pppoe_status_codes`(PPPOE_STATUS_OK, PPPOE_STATUS_OUT_OF_SOCKETS, PPPOE_STATUS_INSUFFICIENT_BUFFER_SPACE, PPPOE_TIMEOUT, PPPOE_CONFIGURATION_ERROR, PPPOE_STOPPED); `pppoe_info_elements`(PPPOE_INFO_ELEMENT_REQUIRED_BUFFERS)

## scap/scap.tbh

Config defines (set before include):
- `SCAP_DEBUG_PRINT` = 0 — SCREEN CAPTURE LIBRARY 1- debug output in console. 0- no debug output.
- `SCAP_HTTP_TX_BUFF_PAGES` = 16 — The following will be divided between all sockets allocated by the library. The number of sockets is equal to SCAP_NUM_OF_SOCK (defined in scap.tbs). Allocating fewer pages decreases the performance.
- `SCAP_HTTP_VAR_BUFF_PAGES` = 4 — The following will be divided between all sockets allocated by the library. The number of sockets is equal to SCAP_NUM_OF_SOCK (defined in scap.tbs). Allocating fewer pages decreases the performance.

API:
- `function scap_start() as en_scap_status_codes`
- `sub scap_capture(offsetX as word, offsetY as word, Xsize as word,Ysize as word)`
- `function scap_size_convertion(v as dword) as string(4)`

Enums: `en_scap_status_codes`(EN_SCAP_STATUS_OK, EN_SCAP_STATUS_OUT_OF_SOCKETS)

## settings/settings.tbh

Config defines (set before include):
- `STG_DEBUG_PRINT` = 0 — SETTINGS LIBRARY 1- debug output in console. 0- no debug output.
- `STG_DESCRIPTOR_FILE` = "settings.txt" — Name of the setting descriptor file This file must be in your project and contain correct data!
- `STG_STORAGE_MEMORY` = 0 — 0- non-volatile settings stored in the EEPROM 1- non-volatile settings stored in the file (on the flash disk)
- `STG_FILENAME` = "settings.dat" — When STG_STORAGE_MEMORY= 1 (file), defines the filename in which setting values are stored
- `STG_REDUNDANCY` = 0 — 0- only one copy of data is stored for all settings. 1- two copies of data are stored for non-volatile settings. Only one copy is maintained for volatile settings. 2- two copies of data are stored for non-volatile and vo
- `STG_TIMESTAMP` = 0 — 0- no timestamp is saved with settings 1- each setting keeps its own modification timestamp (one for all members)
- `STG_MAX_NUM_SETTINGS` = 1 — Set this to the actual number of settings in your project Save memory -- set the exact number you need! Range: 1-255
- `STG_RAM_ARRAY_SIZE` = 0 — If there are volatile settings in your project, set this to the necessary amount of RAM needed Save memory -- set the exact number you need!
- `STG_RAM_TYPE` = 0 — 0- volatile settings are saved into the "regular" RAM 1- volatile settings are saved using callback_stg_vm_write() and callback_stg_vm_read()
- `STG_MAX_SETTING_NAME_LEN` = 2 — Specifies maximum setting name lengths Shorter names save memory! Range: 1-255
- `STG_MAX_SETTING_VALUE_LEN` = 16 — Specifies maximum length for the setting value in string form Trancation will occur if this value is insufficient Smaller value saves memory! Range: 1-253 (STG_TIMESTAMP 0) Range: 1-246 (STG_TIMESTAMP 1)
- `STG_ENABLE_VALIDATION_CALLBACK` = 0 — Allows additional validation before settings are stored via callback_stg_validation_check 1- Enable additional validation 0- Disable additional validation

API:
- `function stg_start() as en_stg_status_codes`
- `function stg_start_no_init() as en_stg_status_codes`
- `function stg_start_with_params(init as no_yes) as en_stg_status_codes`
- `function stg_check_all(byref problem_stg as string) as en_stg_status_codes`
- `function stg_get_def(byref stg_name_or_num as string,index as byte,byref def_value as string) as en_stg_status_codes`
- `function stg_restore_member(byref stg_name_or_num as string, index as byte) as en_stg_status_codes`
- `function stg_restore_multiple(init_mode as en_stg_init_modes) as en_stg_status_codes`
- `function stg_get_num_settings() as byte`
- `function stg_get_num_members(byref stg_name_or_num as string, byref num_members as byte) as en_stg_status_codes`
- `function stg_get(byref stg_name_or_num as string, index as byte) as string`
- `sub stg_set(byref stg_name_or_num as string, index as byte, byref stg_value as string)`
- `function stg_sg(byref stg_name_or_num as string,index as byte,byref stg_value as string,op as en_stg_rdwr) as en_stg_status_codes`
- `function stg_set_ts(byref stg_name_or_num as string) as en_stg_status_codes`
- `function stg_find(byref stg_name_or_num as string) as byte`
- `function stg_stype_get(byref stg_name_or_num as string) as byte`

Callbacks YOU must implement:
- `sub callback_stg_error(byref stg_name_or_num as string, index as byte, status as en_stg_status_codes)` — Callback procedure, informs of the error during the execution of stg_get() or set_set(). Procedure body has to be created elsewhere in the project (externally w
- `sub callback_stg_pre_get(byref stg_name_or_num as string, index as byte, byref stg_value as string)` — Callback procedure, informs that the setting member's value is being read through one of the STG library's procedures; allows to update the setting member's val
- `sub callback_stg_post_set(byref stg_name_or_num as string, index as byte, byref stg_value as string)` — Callback procedure, informs that the setting member's value is being written to through one of the STG library's procedures; allows to respond to the value chan
- `sub callback_stg_validation_check(byref stg_name_or_num as string, index as byte, byref stg_value as string) as en_stg_status_codes` — Callback procedure, before writing a value to a setting member, allow doing validation check according to the system rules; For example: validation to a field t
- `function callback_stg_vm_read(address as word) as byte` — Callback procedure, required only when STG_RAM_TYPE=1, used to read one byte from a "custom" volatile memory. Procedure body has to be created elsewhere in the 
- `sub callback_stg_vm_write(data_to_write as byte, address as word)` — Callback procedure, required only when STG_RAM_TYPE=1, used to write one byte to a "custom" volatile memory. Procedure body has to be created elsewhere in the p

Enums: `en_stg_rdwr`(EN_STG_GET, EN_STG_SET); `en_stg_status_codes`(EN_STG_STATUS_OK, EN_STG_STATUS_NOT_STARTED, EN_STG_STATUS_OUT_OF_FILE_NUMBERS, EN_STG_STATUS_WRONG_DEFINE, EN_STG_STATUS_WRONG_DESCRIPTOR, EN_STG_STATUS_UNKNOWN, EN_STG_STATUS_INVALID_INDEX, EN_STG_STATUS_FAILURE, EN_STG_STATUS_INVALID); `en_stg_init_modes`(EN_STG_INIT_MODE_NORMAL, EN_STG_INIT_MODE_OVERRIDE, EN_STG_INIT_MODE_RAM_ONLY, EN_STG_INIT_MODE_RAM_ONLY_OVERRIDE); `en_stg_types`(EN_STG_TYPE_BYTE, EN_STG_TYPE_DOTDECIMAL, EN_STG_TYPE_FLOAT, EN_STG_TYPE_TIME, EN_STG_TYPE_STRING, EN_STG_TYPE_TIMESTAMP, EN_STG_TYPE_WORD)

## smtp/smtp.tbh

Config defines (set before include):
- `SMTP_DEBUG_PRINT` = 1 — SMTP LIBRARY
- `SMTP_REPLY_TIMEOUT` = 30
- `SMTP_MAX_RETRIES` = 3

API:
- `function smtp_start() as en_smtp_status_codes`
- `sub smtp_stop()`
- `sub smtp_init(byref server_domain as string, server_port as word, byref username as string, byref password as string)`
- `function smtp_send_email(byref recipient as string, byref sender as string, byref subject as string, byref body as string, interface as pl_sock_interfaces) as en_smtp_status_codes`
- `sub smtp_proc_data()`
- `sub smtp_proc_timer()`
- `sub smtp_proc_sock_event(newstate as pl_sock_state, newstatesimple as pl_sock_state_simple)`
- `sub smtp_proc_data_sent()`
- `function smtp_get_auth_plain_support() as boolean` — Helper functions to check server AUTH capabilities
- `function smtp_get_auth_login_support() as boolean`
- `function smtp_get_auth_cram_md5_support() as boolean`
- `function smtp_get_auth_xoauth2_support() as boolean`

Callbacks YOU must implement:
- `sub callback_smtp_dns_answer_acquired(return_type as en_dns_return_type, byref return_string as string)`
- `sub callback_smtp_send_complete(status as en_smtp_status_codes)`
- `sub callback_smtp_pre_buffrq(num_of_pages_required as byte)`
- `sub callback_smtp_buff_released()`

Enums: `en_smtp_status_codes`(EN_STATUS_SMTP_OK, EN_STATUS_SMTP_NOT_INITIALIZED, EN_STATUS_SMTP_BUSY, EN_STATUS_SMTP_INVALID_SOCKET, EN_STATUS_SMTP_INVALID_INTERFACE, EN_STATUS_SMTP_DNS_FAILED, EN_STATUS_SMTP_CONNECTION_FAILED, EN_STATUS_SMTP_AUTH_FAILED, EN_STATUS_SMTP_SEND_FAILED, EN_STATUS_SMTP_TIMEOUT, EN_STATUS_SMTP_INSUFFICIENT_BUFFER_SPACE); `en_smtp_response_codes`(SMTP_RESP_NONE, SMTP_RESP_220_READY, SMTP_RESP_221_CLOSING, SMTP_RESP_250_OK, SMTP_RESP_251_FORWARD, SMTP_RESP_354_START_MAIL, SMTP_RESP_421_NOT_AVAILABLE, SMTP_RESP_450_MAILBOX_BUSY, SMTP_RESP_451_ACTION_ABORTED, SMTP_RESP_452_INSUFFICIENT_STORAGE, SMTP_RESP_500_SYNTAX_ERROR, SMTP_RESP_501_PARAMETER_ERROR…); `en_smtp_state`(SMTP_STATE_IDLE, SMTP_STATE_DNS_LOOKUP, SMTP_STATE_CONNECTING, SMTP_STATE_WAIT_GREETING, SMTP_STATE_SEND_EHLO, SMTP_STATE_WAIT_EHLO, SMTP_STATE_SEND_STARTTLS, SMTP_STATE_WAIT_STARTTLS, SMTP_STATE_TLS_HANDSHAKE, SMTP_STATE_SEND_EHLO_TLS, SMTP_STATE_WAIT_EHLO_TLS, SMTP_STATE_SEND_AUTH…)

## snmp/snmp.tbh


API:
- `function snmp_initialize(byref password as string, byref contact as string, byref location as string) as boolean` — Functions & Subs
- `sub snmp_receive(byref data as string)`
- `sub snmp_trap_check_digital(channel as byte)`
- `sub snmp_trap_check_analog(channel as byte, floatPart as boolean)`
- `sub snmp_send_trap(byref trapID as string, specific as byte, typeValue as byte, byref value as string, byref objectID as string)`

Enums: `SNMP_BER_TYPES`(SNMP_INTEGER, SNMP_OCTET_STRING, SNMP_NULL, SNMP_OBJECT_ID, SNMP_SEQUENCE, SNMP_IP_ADDRESS, SNMP_COUNTER, SNMP_TIMETICKS, SNMP_GET_REQUEST_PDU, SNMP_GET_NEXT_REQUEST_PDU, SNMP_GET_RESPONCE_PDU, SNMP_SET_REQUEST_PDU…); `TrapType`(TrapDigital, TrapCounter, TrapAnalog); `TrapDigitalType`(TrapDigitalRise, TrapDigitalEdge); `TrapAnalogType`(TrapAnalogBelow, TrapAnalogAbove, TrapAnalogBetween, TrapAnalogOutOfRange)

## sntp/sntp.tbh

Config defines (set before include):
- `SNTP_DEBUG_PRINT` = 0 — SNTP LIBRARY (Obtains date/time from an SNTP server)
- `SNTP_REPLY_TIMEOUT` = 3
- `SNTP_RETRY` = 3
- `SNTP_OFFSET_CALCULATION` = 0

API:
- `sub sntp_init()`
- `function sntp_start(interface as pl_sock_interfaces,byref server_ip as string,server_port as word,socket as byte) as en_sntp_status_codes`
- `sub sntp_proc_timer()`
- `sub sntp_proc_data()`
- `sub sntp_proc_sock_event(state as pl_sock_state_simple)`

Callbacks YOU must implement:
- `sub callback_sntp_failure(sntp_status as en_sntp_status_codes)`
- `sub callback_sntp_ok(byref w_days as word,byref w_mins as word,byref b_seconds as byte)`
- `sub callback_sntp_pre_buffrq(required_buff_pages as byte)`
- `sub callback_sntp_get_rtc(byref w_days as word,byref w_mins as word,byref b_seconds as byte)`

Enums: `en_sntp_status_codes`(SNTP_STATUS_OK, SNTP_STATUS_INVALID_SOCKET, SNTP_STATUS_INVALID_INTERFACE, SNTP_STATUS_INSUFFICIENT_BUFFER_SPACE, SNTP_STATUS_CONNECTION_TIMEOUT, SNTP_STATUS_REPLY_TIMEOUT, SNTP_STATUS_REPLY_DATA_ERROR)

## sock/sock.tbh

Config defines (set before include):
- `SOCK_DEBUG_PRINT` = 0 — SOCKET ALLOCATION LIBRARY 1- debug output in console. 0- no debug output.
- `SOCK_MAX_SIGNATURE_LEN` = 3 - Maximum length of the socket user's signature string **[docs.tibbo.com: default = 0; >0 - чтобы видеть подписи вызывающих sock_get() через sock_who_uses()]**

API:
- `function sock_get(byref signature as string) as byte`
- `function sock_who_uses(sock_num as byte) as string`
- `sub sock_release(sock_num as byte)`

## ssi/ssi.tbh

Config defines (set before include):
- `SSI_DEBUG_PRINT` = 0 — SSI CHANNEL ALLOCATION LIBRARY 1- debug output in console 0- no debug output
- `SSI_MAX_SIGNATURE_LEN` = 0 — Maximum length of the SSI channel user's signature string

API:
- `function ssi_get(byref signature as string) as byte`
- `function ssi_who_uses(ssi_num as byte) as string`
- `sub ssi_release(ssi_num as byte)`

## stgcmd/stgcmd.tbh


API:
- `function stgcmd_proc_cmd(byref cmd_str as string) as string`

## super_i2c/super_i2c.tbh

Config defines (set before include):
- `SI2C_DEBUG_PRINT` = 0 — 1- debug output in console. 0- no debug output.
- `SI2C_MAX_SIGNATURE_LEN` = SSI_MAX_SIGNATURE_LEN — Maximum length of the I2C user's signature string

API:
- `function si2c_register(byref signature as string,sda as pl_io_num, scl as pl_io_num,use_ssi as no_yes) as byte`
- `function si2c_who_uses(num as byte) as string`
- `sub si2c_release(num as byte)`
- `sub si2c_get(num as byte)`
- `sub si2c_start()`
- `sub si2c_stop()`
- `sub si2c_write(data as byte)`
- `function si2c_read(acknak_request as boolean) as byte`
- `function si2c_is_busy(num as byte)as no_yes`

## super_i2c/super_spi.tbh

Config defines (set before include):
- `SSPI_DEBUG_PRINT` = 0 — 1- debug output in console. 0- no debug output.
- `SSPI_MAX_SIGNATURE_LEN` = SSI_MAX_SIGNATURE_LEN — Maximum length of the SPI user's signature string

API:
- `function sspi_register(byref signature as string,mosi as pl_io_num,miso as pl_io_num, scl as pl_io_num,mode as spi_modes,use_ssi as no_yes) as byte`
- `function sspi_who_uses(num as byte) as string`
- `sub sspi_release(num as byte)`
- `sub sspi_get(num as byte)`
- `sub sspi_write(data as byte)`
- `function sspi_read() as byte`

Enums: `spi_modes`(SPI_MODE_0, SPI_MODE_1, SPI_MODE_2, SPI_MODE_3)

## super_spi/super_spi.tbh

Config defines (set before include):
- `SSPI_DEBUG_PRINT` = 0 — 1- debug output in console. 0- no debug output.
- `SSPI_MAX_SIGNATURE_LEN` = SSI_MAX_SIGNATURE_LEN — Maximum length of the SPI user's signature string

API:
- `function sspi_register(byref signature as string,mosi as pl_io_num,miso as pl_io_num, scl as pl_io_num,mode as spi_modes,use_ssi as no_yes) as byte`
- `function sspi_who_uses(num as byte) as string`
- `sub sspi_release(num as byte)`
- `sub sspi_get(num as byte)`
- `sub sspi_write(data as byte)`
- `function sspi_read() as byte`

Enums: `spi_modes`(SPI_MODE_0, SPI_MODE_1, SPI_MODE_2, SPI_MODE_3)

## tables/tables.tbh

Config defines (set before include):
- `TBL_DEBUG_PRINT` = 0 — TABLES LIBRARY
- `TBL_AGGREGATE_HASH` = 0
- `TBL_DESCRIPTOR_FILE` = "tables.txt"
- `TBL_MAX_TABLE_NAME_LEN` = 2
- `TBL_MAX_FILE_NAME_LEN` = 42
- `TBL_MAX_NUM_TABLES` = 1
- `TBL_MAX_FIELD_NAME_LEN` = 2
- `TBL_MAX_FIELD_DISPLAY_NAME_LEN` = 2
- `TBL_MAX_TOTAL_NUM_FIELDS` = 1
- `TBL_MAX_RECORD_SIZE` = 2
- `TBL_ADJUST_LIST_WHEN_FULL` = 1
- `TBL_DISCARD_OLD_RECORD_WHEN_FULL` = 0
- `TBL_TIME_TYPE_INCLUDED` = 1

API:
- `function tbl_start() as en_tbl_status_codes`
- `function tbl_get_table_info(byref table_name_or_num as string, byref table_metadata as tbl_type) as en_tbl_status_codes`
- `function tbl_get_num_fields(byref table_name_or_num as string) as byte`
- `function tbl_get_field_info(byref table_name_or_num as string, field_index as byte, byref field_metadata as tbl_field_type) as en_tbl_status_codes`
- `function tbl_get_field_def(byref table_name_or_num as string, byref field_name as string, byref def_value as string) as en_tbl_status_codes`
- `function tbl_get_max_field_size(byref table_name_or_num as string) as byte`
- `function tbl_replace(byref old_file_name as string, byref new_file_name as string) as en_tbl_status_codes`
- `function tbl_select(byref table_name_or_num as string, byref file_name as string) as en_tbl_status_codes`
- `function tbl_select_for_read(byref table_name_or_num as string, byref file_name as string) as en_tbl_status_codes`
- `function tbl_schema_check(byref table_name_or_num as string) as en_tbl_status_codes`
- `function tbl_clear() as en_tbl_status_codes`
- `function tbl_get_hash() as string`
- `function tbl_record_sg(byref rec_num as word, op as en_tbl_rdwr) as en_tbl_status_codes`
- `function tbl_record_add(uid as string(32)) as en_tbl_status_codes`
- `function tbl_record_edit(byref rec_num as word) as en_tbl_status_codes`
- `function tbl_record_read_active(byref rec_num as word) as en_tbl_status_codes`
- `function tbl_record_delete(byref rec_num as word) as en_tbl_status_codes`
- `function tbl_record_undelete(byref rec_num as word) as en_tbl_status_codes`
- `function tbl_record_find(record_type as en_tbl_record_states,byref search_data as string,byref field_name as string,byref rec_num as word,direction as en_tbl_search_direction,find_method as pl_fd_find_modes) as en_tbl_status_codes`
- `function tbl_multi_field_record_find(record_type as en_tbl_record_states,byref search_data as string,byref starting_field as string,byref rec_num as word,direction as en_tbl_search_direction,find_method as pl_fd_find_modes) as en_tbl_status_codes`
- `function tbl_get_num_records(byref num_of_records as word, include_deleted as no_yes) as en_tbl_status_codes`
- `function tbl_timestamp_sg(byref timestamp as struct_tbl_timestamp,op as en_tbl_rdwr) as en_tbl_status_codes`
- `function tbl_get_file_name() as string`
- `function tbl_get_table_name() as string`
- `function tbl_is_record_deleted(rec_num as word) as no_yes`
- `function tbl_close(byref file_name as string)as en_tbl_status_codes`
- `function tbl_field_sg_raw(byref field_name as string, byref field_value as string) as en_tbl_status_codes`
- `function tbl_field_sg(byref field_name as string,byref field_value as string,op as en_tbl_rdwr) as en_tbl_status_codes`
- `function tbl_field_get(byref field_name as string) as string`
- `sub tbl_field_set(byref field_name as string, byref field_value as string)`
- `function tbl_is_current_record_deleted() as no_yes`
- `sub tbl_set_to_clean_start(op as no_yes)`

Callbacks YOU must implement:
- `sub callback_tbl_error(status as en_tbl_status_codes)`
- `function callback_tbl_fail_to_open(byref filename as string, status as pl_fd_status_codes, filenum as byte) as no_yes`
- `sub callback_tbl_field_error(byref file_name as string,byref field_name as string,tbl_result as en_tbl_status_codes)`
- `sub callback_tbl_modified(byref file_name as string, modified_operation as en_tbl_modified_operation)`

Enums: `en_tbl_search_direction`(EN_TBL_SEARCH_DOWN, EN_TBL_SEARCH_UP); `en_tbl_rdwr`(EN_TBL_GET, EN_TBL_SET); `en_tbl_field_types`(EN_TBL_FIELD_BYTE, EN_TBL_FIELD_TIMESTAMP, EN_TBL_FIELD_FLOAT, EN_TBL_FIELD_TIME, EN_TBL_FIELD_STRING, EN_TBL_FIELD_TIMESTRING, EN_TBL_FIELD_DWORD, EN_TBL_FIELD_WORD); `en_tbl_status_codes`(EN_TBL_STATUS_OK, EN_TBL_STATUS_NOT_STARTED, EN_TBL_STATUS_OUT_OF_FILE_NUMBERS, EN_TBL_STATUS_WRONG_DEFINE, EN_TBL_STATUS_WRONG_DESCRIPTOR, EN_TBL_STATUS_UNKNOWN_FILE, EN_TBL_STATUS_FAILURE, EN_TBL_STATUS_UNKNOWN_TABLE, EN_TBL_STATUS_UNKNOWN_FIELD, EN_TBL_STATUS_INVALID, EN_TBL_STATUS_FULL, EN_TBL_STATUS_NOT_FOUND…); `en_tbl_struct`(EN_TBL_STRUCT_LIST, EN_TBL_STRUCT_TABLE); `en_tbl_date_time_format`(EN_TBL_DT_DATE, EN_TBL_DT_TIME1, EN_TBL_DT_TIME2, EN_TBL_DT_TIME3, EN_TBL_DT_DATE_TIME1, EN_TBL_DT_DATE_TIME2, EN_TBL_DT_ALL); `en_tbl_record_states`(EN_TBL_RECORD_DELETED, EN_TBL_RECORD_ACTIVE, EN_TBL_RECORD_BOTH); `en_tbl_modified_operation`(EN_TBL_MODIFIED_ADD, EN_TBL_MODIFIED_DELETE, EN_TBL_MODIFIED_UNDELETE, EN_TBL_MODIFIED_EDIT, EN_TBL_MODIFIED_REPLACE, EN_TBL_MODIFIED_CLEAR)

## tables/tables_web.tbh


API:
- `sub tbl_web_start()`
- `sub tbl_web_set(byref tbl_name as string, tbl_enabled as no_yes)`
- `sub tbl_web_get_tables(byref selected_type as string)`
- `sub tbl_web_get_rows(byref table as string)`
- `sub tbl_web_get_rows_by_offset(byref table as string, byref offset as word, byref count as word)`
- `sub tbl_web_get_table_active_rows(byref table as string, byref tbl_rows as word, byref tbl_rows_all as word)`
- `sub tbl_web_get_flds(byref table as string)`
- `function tbl_web_delete_row(byref table as string,row as word) as string`
- `function tbl_web_edit_row(byref table as string,byref index as word,byref row as string) as string`
- `function tbl_web_get_field_def(byref table_name_or_num as string, byref field_name as string) as string`
- `function tbl_web_add_row(byref table as string,byref row as string) as string`
- `function tbl_web_clear_table(byref table as string) as string`
- `function tbl_web_get_header(byref table as string) as string`
- `function tbl_web_get_fld_data(index as word, num_of_fld as byte) as string`
- `function tbl_web_get_fld_data_json(index as word, num_of_fld as byte) as string`

## tibbits/tbt43/tibbit43.tbh

Config defines (set before include):
- `TIBBIT_43_MAX_NO` = 4
- `TIBBIT_43_NO_OF_SAMPLES` = 10
- `TIBBIT_43_RX_BUF` = 32

API:
- `sub tibbit_43_proc_data()`
- `sub tibbit_43_start()`
- `function tibbit_43_init(port as byte) as boolean`
- `function tibbit_43_set_sample_rate(port as byte, rate as integer) as TIBBIT_43_RESULT`
- `function tibbit_43_set_sampling_mode(port as byte, sampmode as TIBBIT43_SAMPLING_MODE) as TIBBIT_43_RESULT`
- `function tibbit_43_set_data_format(port as byte, datamode as TIBBIT43_DATA_FORMAT) as TIBBIT_43_RESULT`
- `function tibbit_43_set_enable_channels(port as byte, channels as string(7)) as TIBBIT_43_RESULT`
- `function tibbit_43_set_A(port as byte, a1 as byte, a2 as byte, a3 as byte, a4 as byte, a5 as byte, a6 as byte) as TIBBIT_43_RESULT`
- `function tibbit_43_set_BP(port as byte, b1 as char, b2 as char, b3 as char, b4 as char, b5 as char, b6 as char) as TIBBIT_43_RESULT`
- `function tibbit_43_set_BN(port as byte, b1 as char, b2 as char, b3 as char, b4 as char, b5 as char, b6 as char) as TIBBIT_43_RESULT`
- `function tibbit_43_reset_settings_to_factory(port as byte) as TIBBIT_43_RESULT`
- `function tibbit_43_store_settings_to_EEPROM(port as byte) as TIBBIT_43_RESULT`
- `function tibbit_43_restore_settings_from_EEPROM(port as byte) as TIBBIT_43_RESULT`
- `function tibbit_43_read_settings_from_EEPROM(port as byte, byref settings as TIBBIT43_SETTINGS) as TIBBIT_43_RESULT`
- `function tibbit_43_read_settings_from_RAM(port as byte, byref settings as TIBBIT43_SETTINGS) as TIBBIT_43_RESULT`
- `function tibbit_43_read_data_ascii(port as byte, channels as string(7)) as TIBBIT_43_RESULT`
- `function tibbit_43_read_data_hex(port as byte, channels as string(7)) as TIBBIT_43_RESULT`
- `function tibbit_43_get_data_ascii(port as byte, channels as string(7)) as string`
- `function tibbit_43_get_data_hex(port as byte, channels as string(7)) as string`
- `function tibbit_43_set_mode(port as byte, mode as TIBBIT43_MODE) as TIBBIT_43_RESULT`

Callbacks YOU must implement:
- `sub callback_tibbit_43_data_arrival(mode as string(12), port as byte, channel1 as string(10), channel2 as string(10), channel3 as string(10), channel4 as string(10))`
- `sub callback_tibbit_43_sampling_completed(samples as TIBBIT43_VALUES(TIBBIT_43_NO_OF_SAMPLES))`

Enums: `TIBBIT43_SAMPLING_MODE`(SAMPLING_SINGLE, SAMPLING_DIFF); `TIBBIT43_MODE`(COMMAND_MODE, DATA_MODE); `TIBBIT43_DATA_FORMAT`(DATA_ASCII, DATA_BIN, DATA_HEX); `TIBBIT_43_RESULT`(RESULT_OK, RESULT_ERROR_SYNTAX, RESULT_ERROR_OUTRANGE, RESULT_ERROR_EXECUTION, RESULT_ERROR_LIBRARY, RESULT_TIBBIT_INVALID)

## tibbits/tbt40/tbt40.tbh

Config defines (set before include):
- `TBT40_CLK_PIN` = PL_IO_NULL
- `TBT40_DATA_PIN` = PL_IO_NULL

API:
- `function tbt40_init(use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte) as tbt40_errcheck` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt40_set_ohm(impedance as dword, range as dword, save_to_eeprom as no_yes, channel as byte)` — Sets the digital potentiometer to the "impedance" value expressed in Ohms.This value will be rounded to the nearest LOWER potentiometer step and limited by the 
- `sub tbt40_set(level as word,save_to_eeprom as no_yes, channel as byte)` — Sets the digital potentiometer to the level (step) in the 0-256 range (there are 257 steps in total). Each step is equal to 1/257th of the IC's range (5K, 10K, 

Enums: `tbt40_errcheck`(TBT40_OK, TBT40_SELFTEST_FAILED, TBT40_NO_SSI_AVAILABLE)

## tibbits/tbt64/tbt64.tbh


API:
- `sub tbtPWM_start()`
- `function tbtPWM_init(signature as string, i2c_id as byte, data_pin as byte, clk_pin as byte, rst_pin as byte, fault_pin as byte, byref tbt_channel as byte, use_ssi as no_yes)as ok_ng`
- `function tbtPWM_check_fault(tbt_channel as byte) as boolean`
- `function tbtPWM_set_range(range as byte, tbt_channel as byte) as ok_ng`
- `function tbtPWM_set_frequency(frequency as word, channel as byte, tbt_channel as byte) as ok_ng`
- `function tbtPWM_set_duty(duty as byte, channel as byte, tbt_channel as byte) as ok_ng`
- `function tbtPWM_set_enable(enable as boolean, channel as byte, tbt_channel as byte) as ok_ng`
- `function tbtPWM_get_fault(channel as byte, tbt_channel as byte) as byte`
- `function tbtPWM_set_i2c_id(new_id as byte, tbt_channel as byte) as ok_ng`
- `function tbtPWM_read_all(tbt_channel as byte) as string`

## tibbits/tbt29/tbt29.tbh


API:
- `function tbt29_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte) as tbt29_errcheck`
- `function tbt29_get_c(byref channel as byte) as real`
- `function tbt29_get(channel as byte) as integer`

Enums: `tbt29_errcheck`(TBT29_OK, TBT29_WRONG_MFGID, TBT29_WRONG_DEVID_REVISION, TBT29_NO_SSI_AVAILABLE)

## tibbits/tbt52/tbt52.tbh


API:
- `function tbt52_init(use_ssi as no_yes,pin_clk as byte,pin_data as byte,pin_mclr as byte,pin_int as byte,byref channel as byte) as ok_ng` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt52_channel_select(channel as tbt52_nums)` — Selects an active ADC channel. Use tbt52_get_volts() for actual conversion.
- `function tbt52_get_volts(pin_int as byte,channel as byte)as real` — Performs ADC conversion for the selected channel and returns PREVIOUS conversion result expressed in mV. Select desired channel using tbt52_channel_select() and
- `sub tbt52_release(channel as byte)` — Performs ADC conversion for the selected channel and returns PREVIOUS conversion result expressed in mV. Select desired channel using tbt52_channel_select() and
- `sub tbt52_compensation_calibrate(pin_int as byte,channel as byte)`

Enums: `tbt52_nums`(ADC_1, ADC_2, ADC_3, ADC_4)

## tibbits/tbt35/tbt35.tbh


API:
- `function tbt35_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte) as ok_ng`
- `function tbt35_get(channel as byte) as word`
- `function tbt35_get_kpa(channel as byte)as float`

## tibbits/tbt61/tbt61.tbh


API:
- `function tbt61_init(signature as string, input_type as TBT61_VOLAGE_TYPE_INPUT, cs as pl_io_num, clk as pl_io_num, mosi as pl_io_num, miso as pl_io_num, scl as pl_io_num, sda as pl_io_num, byref tbt_channel as byte) as TBT61_INIT_RESULT` — <b>FUNCTION</b><br><br> The function initializes Tibbit #61.<br><br> <b>Inputs:</b><br> &emsp;<font color="maroon"><b>signature</b></font> - Text identifier of 
- `sub tbt61_release(tbt_channel as byte)` — <b>SUBROUTINE</b><br><br> The subroutine releases all allocated resources for this Tibbit#61 instance.<br><br> <b>Inputs:</b><br> &emsp;<font color="maroon"><b>
- `sub tbt61_mode(tbt_channel as byte, input_type as TBT61_VOLAGE_TYPE_INPUT)` — <b>SUBROUTINE</b><br><br> This subroutine changes the type of inputs used.<br><br> <b>Inputs:</b><br> &emsp;<font color="maroon"><b>tbt_channel</b></font> - Tib
- `function tbt61_read_adc(tbt_channel as byte, channel as byte, byref flags as byte) as real` — <b>FUNCTION</b><br><br> The function reads the ADC value for the specified channel number. Error flags are also returned.<br><br> <b>Inputs:</b><br> &emsp;<font
- `function tbt61_read_fw_info(tbt_channel as byte) as FW_Info` — <b>FUNCTION</b><br><br> This function returns the <font color="teal"><b>FW_Info</b></font> structure read from the EEPROM of the specified Tibbit#61.<br><br> <b

Enums: `TBT61_INIT_RESULT`(TBT61_INIT_OK, TBT61_INIT_ERROR_SPI_NO_EMPTY_CHANNEL, TBT61_INT_ERROR_NO_TIBBIT_PRESENT, TBT61_INIT_ERROR_NO_VALID_VERSION, TBT61_INIT_ERROR_FAULT_CHECK_POWER, TBT61_INIT_ERROR_EEPROM); `TBT61_VOLAGE_TYPE_INPUT`(TBT61_VOLTAGE_TWO_DIFFERENTIAL, TBT61_VOLTAGE_FOUR_SINGLE)

## tibbits/tbt36/tbt36.tbh

Config defines (set before include):
- `TBT_36_RESOLUTION` = TBT_36_RESOLUTION_FULL
- `TBT_36_RANGE` = TBT_36_RANGE_12G

API:
- `function tbt36_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte)as ok_ng`
- `sub tbt36_get_mg(byref x_value as integer, byref y_value as integer, byref z_value as integer, channel as byte)`
- `sub tbt36_get(byref x_value as integer, byref y_value as integer, byref z_value as integer, channel as byte)`

## tibbits/tbt42/tbt42.tbh


API:
- `function tbt42_init(use_ssi as no_yes,pin_cs as byte,pin_clk as byte,pin_mosi as byte,pin_miso as byte,byref channel as byte)as tbt42_errcheck` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt42_rtc_get(byref wdaycount as word,byref wmincount as word,byref bsec as byte, pin_cs as byte, channel as byte)` — Reads the current daycount, mincount, and seconds from the RTC. Use year(), month(), date(), hours(), minutes(), and weekday() syscalls to convert these values 
- `function tbt42_rtc_set(wdaycount as word,wmincount as word,bsec as byte, pin_cs as byte, channel as byte)as ok_ng` — Writes the specified daycount, mincount, and seconds into the RTC. Use daycount() and mincount() syscalls to convert your date and time into the daycount and mi
- `function tbt42_alarm_set(wdaycount as word, wmincount as word,bsec as byte, enable_alarm as no_yes, pin_cs as byte, channel as byte)as ok_ng` — Sets the alarm if enable_alarm=YES. Disables the alarm if enable_alarm=NO. With alarm enabled...<br> - When wdaycount=0 AND wmincount=0 AND bsec=0 alarm occurs 
- `function tbt42_alarm_waiting(pin_miso as byte, pin_cs as byte, channel as byte)as ok_ng` — Sets the alarm if enable_alarm=YES. Disables the alarm if enable_alarm=NO. With alarm enabled...<br> - When wdaycount=0 AND wmincount=0 AND bsec=0 alarm occurs 
- `function tbt42_alarm_setting_get(byref wdaycount as word, byref wmincount as word, byref bsec as byte, pin_cs as byte, channel as byte)as no_yes` — Returns NO if alarm is disabled or YES if enabled, in which case wdaycout, wmincount, and bsec will contain current alarm settings.
- `sub tbt42_rtc_int_clear(pin_cs as byte, channel as byte)` — Clears the alarm interrupt thus causing the INT line to go HIGH (deactivate).
- `function tbt42_temp_get(pin_cs as byte, channel as byte)as real` — Reads the current temperature. The temperature is measured in steps of 0.25 degrees C. Reading the temperature does not cause the actual temperature measurement
- `function tbt42_nvram_read(address as byte, pin_cs as byte, channel as byte) as byte` — Reads a byte of data from the non-volatile memory at address 0~255.
- `sub tbt42_nvram_write(data_to_write as byte, address as byte, pin_cs as byte, channel as byte)` — Writes a byte of data into the non-volatile memory at address 0~255.

Enums: `tbt42_errcheck`(TBT42_OK, TBT42_SELF_TEST_FAIL, TBT42_NO_SSI_AVAILABLE)

## tibbits/tbt13/tbt13.tbh


API:
- `function tbt13_init(signature as string, data_pin as byte, clk_pin as byte, byref tbt_channel as byte, use_ssi as no_yes) as ok_ng` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt13_channel_select(channel as tbt13_nums, tbt_channel as byte)` — Selects an active ADC channel. Use tbt13_get_prev_mv() or tbt13_get_prev() for actual conversion.
- `function tbt13_get_prev_mv(tbt_channel as byte) as integer` — Performs ADC conversion for the selected channel and returns PREVIOUS conversion result expressed in mV. Select desired channel using tbt13_channel_select() and
- `function tbt13_get_prev(tbt_channel as byte) as word` — Performs ADC conversion for the selected channel and returns PREVIOUS conversion as an unsigned 10-bit value. The range is from 0 (-10V) to 1023 (+10V). Select 

Enums: `tbt13_nums`(ADC_1, ADC_2, ADC_3, ADC_4)

## tibbits/tbt14/tbt14.tbh

Config defines (set before include):
- `TBT14_CLK_PIN` = PL_IO_NULL
- `TBT14_DATA_PIN` = PL_IO_NULL
- `TBT14_LOAD_PIN` = PL_IO_NULL
- `TBT14_BUSY_PIN` = PL_IO_NULL

API:
- `function tbt14_init(signature as string, data_pin as byte, clk_pin as byte, load_pin as byte, busy_pin as byte, byref tbt_channel as byte, use_ssi as no_yes) as ok_ng` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `sub tbt14_set_mv(n as dac_nums, mv as integer, load_pin as byte, busy_pin as byte, tbt_channel as byte)` — Sets the outputs of one DAC channel to output voltage expressed in mV.
- `sub tbt14_set(n as dac_nums,v as word, load_pin as byte, busy_pin as byte, tbt_channel as byte)` — Programs a 12-bit value into one DAC channel. The range is from 0 (-10V) to 4095 (+10V).

Enums: `dac_nums`(DAC_1, DAC_2, DAC_3, DAC_4)

## tibbits/tbt62/tbt62.tbh


API:
- `function tbt62_init(signature as string, data_pin as byte, clk_pin as byte, reset_pin as byte, busy_pin as byte, units as EN_TBT62_UNITS, byref tbt_channel as byte, use_ssi as no_yes) as EN_TBT62_INIT_RESULT`
- `function tbt62_send_command(command as byte, tbt_channel as byte) as boolean`
- `function tbt62_send_data(command as byte, rom as string(8), data as string(16), tbt_channel as byte) as boolean`
- `function tbt62_read_data(byref data as string, data_len as byte, tbt_channel as byte) as boolean`
- `function tbt62_check_mode(mode as EN_TBT62_MODE, channel as EN_TBT62_CHANNEL, tbt_channel as byte) as boolean`
- `function tbt62_check_channel(channel as EN_TBT62_CHANNEL, tbt_channel as byte) as boolean`
- `function tbt62_get_VCC_voltage(tbt_channel as byte) as real`
- `function tbt62_get_3V3_voltage(tbt_channel as byte) as real`
- `function tbt62_get_power_fault(tbt_channel as byte) as byte`
- `function tbt62_vcc_control(state as EN_TBT62_VCC_CONTROL, tbt_channel as byte) as boolean`
- `function tbt62_get_voltage(channel as EN_TBT62_CHECK_CHANNEL, tbt_channel as byte) as real`
- `function tbt62_checkBUSY(tbt_channel as byte) as boolean`
- `function tbt62_ID_Hex(SensorID as string(8)) as string(16)`
- `function tbt62_ow_get_temperature(byref temperature as real, sensorID as string(8), channel as EN_TBT62_CHANNEL, tbt_channel as byte) as EN_TBT62_FAULT`
- `function tbt62_ow_get_temp_separate(byref temperature as real, sensorID as string(8), phase as EN_TBT62_ONEWIRE_GET_TEMP, channel as EN_TBT62_CHANNEL, tbt_channel as byte) as EN_TBT62_FAULT`
- `function tbt62_set_mode(mode as EN_TBT62_MODE, channel as EN_TBT62_CHANNEL, tbt_channel as byte) as boolean`
- `function tbt62_sw_get_temp_hum(byref temperature as real, byref humidity as real, sensor as EN_TEMP_HUM_SENSOR_TYPE, channel as EN_TBT62_CHANNEL, tbt_channel as byte) as EN_TBT62_FAULT`

Enums: `EN_TBT62_UNITS`(TBT62_METRIC_UNITS, TBT62_IMPERIAL_UNITS); `EN_TBT62_MODE`(TBT62_ONE_WIRE, TBT62_SINGLE_WIRE); `EN_TBT62_CHECK_CHANNEL`(TBT62_VOLTAGE_VCC, TBT62_VOLTAGE_3V3, TBT62_POWER_FAULT); `EN_TBT62_VCC_CONTROL`(TBT62_VCC_OFF, TBT62_VCC_ON); `EN_TBT62_CHANNEL`(TBT62_CHANNEL_1, TBT62_CHANNEL_2); `EN_TEMP_HUM_SENSOR_TYPE`(DHT11, DHT22); `EN_TBT62_INIT_RESULT`(TBT62_INIT_OK, TBT62_INIT_ERROR_SI2C_NO_EMPTY_CHANNEL, TBT62_INIT_ERROR_UNKNOWN_TIBBIT, TBT62_INIT_ERROR_NO_VALID_VERSION, TBT62_INIT_ERROR_FAULT_CHECK_3V3, TBT62_INIT_ERROR_FAULT_CHECK_VCC, TBT62_INIT_ERROR_POWER_FAULT_CHECK); `EN_TBT62_FAULT`(TBT62_NO_FAULT, TBT62_FAULT_TIBBIT, TBT62_FAULT_CONTROLSUM, TBT62_FAULT_NO_SENSOR); `EN_TBT62_ONEWIRE_GET_TEMP`(TBT62_ONEWIRE_GET_TEMP_SAMPLE_START, TBT62_ONEWIRE_GET_TEMP_READ_DATA)

## tibbits/tbt30/tbt30.tbh


API:
- `sub tbt30_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte)`
- `function tbt30_get_pc(byref humidity as float, byref temperature as float, channel as byte) as ok_ng`
- `function tbt30_get(byref humidity as word, byref temperature as word, channel as byte)as ok_ng`

## tibbits/tbt26/tbt26.tbh

Config defines (set before include):
- `TBT26_SPI_CS` = PL_IO_NULL — DEFINES-------------------------------------------------------------
- `TBT26_SPI_CLK` = PL_IO_NULL
- `TBT26_SPI_MOSI` = PL_IO_NULL
- `TBT26_SPI_MISO` = PL_IO_NULL
- `TBT26_SAMPLE_RATE` = 20

API:
- `function tbt26_init(byref signature as string, pin_miso as byte, pin_mosi as byte, pin_clk as byte, pin_cs as byte, byref channel as byte) as errcheck` — Call this function to initialize the Tibbit. This library requires an SSI channel. If all channels are already occupied then this function will return TBT26_NO_
- `sub tbt26_start_recording(inverted as no_yes, carrier as no_yes, freq_div as word, pin_cs as byte, channel as byte)` — Call this function to start the IR signal recording process, i.e. before pressing a button on a remote control you want to clone. Call tbt26_get_data() to read 
- `function tbt26_get_data(pin_cs as byte, channel as byte) as string` — Call this function to read out the recorded IR signal. Do this only after the signal has been received (after you've pressed the button on the remote control yo
- `sub tbt26_play_back(byref data as string, pin_cs as byte, channel as byte)` — Call this function to play back the IR command.<br><br> Arguments:<br><br> dt: IR data. First two bytes are low and high bytes of the divider value for the carr

Enums: `errcheck`(TBT26_OK, TBT26_INIT_FAILURE, TBT26_NO_SSI_AVAILABLE)

## tibbits/tbt28/tbt28.tbh


API:
- `function tbt28_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte)as ok_ng`
- `function tbt28_get(byref channel as byte) as word`

## tibbits/tbt22/tbt22.tbh

Config defines (set before include):
- `TBT22_MAX_NUM_OF_SOCKS` = 1

API:
- `function tbt_rtd_init(signature as string, data_pin as byte, clk_pin as byte, int_pin as byte, byref tbt_channel as byte, use_ssi as no_yes)as ok_ng` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `function tbt22_rtd_config(mode as rtd_conv_mode, sensor as rtd_sensor_type, int_pin as byte, tbt_channel as byte)as ok_ng` — MAX31865 provide the notch frequencies for the noise rejection filter. Input noise is attenuated by a third-order digital "sinc" filter.Noise from 50Hz or 60Hz 
- `sub tbt22_rtd_release(tbt_channel as byte)` — MAX31865 provide the notch frequencies for the noise rejection filter. Input noise is attenuated by a third-order digital "sinc" filter.Noise from 50Hz or 60Hz 
- `function tbt22_rtd_get_temperature(byref data as real, byref fault_detect as byte, byref fault_status as byte, int_pin as byte, tbt_channel as byte)as ok_ng`
- `function tbt22_rtd_fw_version(tbt_channel as byte)as string`

Enums: `rtd_conv_mode`(tbt22_conversion_with_50_hz_mode, tbt22_conversion_with_60_hz_mode); `rtd_sensor_type`(PT100, PT200, PT500, PT1000)

## tibbits/tbt53/tbt53.tbh


API:
- `function tbt53_init(use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte) as ok_ng`
- `function tbt53_get_current(byref ma as real, channel as byte) as ok_ng`
- `sub tbt53_th_release(channel as byte)`

## tibbits/tbt41/tbt41.tbh


API:
- `function tbt41_init(byref signature as string, use_ssi as no_yes, pin_clk as byte, pin_data as byte, byref channel as byte) as tbt41_errcheck` — Call this function to initialize the Tibbit. Use_ssi argument specifies whether you want to communicate with this Tibbit using the SSI channel running in the I2
- `function tbt41_line_out_enable(num as ext_line_name,en as no_yes, channel as byte)as ok_ng` — Configures the specified line (num) to be an input (en=NO) or outpur (en=YES). The function will return NG if the execution fails.
- `function tbt41_line_pup_enable(num as ext_line_name, en as no_yes, channel as byte)as ok_ng` — If en=YES and the corresponding line (num) is configured for input, then this line will be pulled up with a 100 KOhm resistor. The function will return NG if th
- `function tbt41_line_set(num as ext_line_name, state as low_high, channel as byte) as ok_ng` — Sets the output state of the specified line (num). For this to work the line has to be configured as output. The function will return NG if the execution fails.
- `function tbt41_line_get(num as ext_line_name, byref state as low_high, channel as byte)as ok_ng` — Reads the state of the specified line (num). The value will be returned in the state variable. The function will return NG if the execution fails.
- `function tbt41_port_config_set(dir as byte,pullup as byte, channel as byte)as ok_ng` — Sets the direction and pull-up status for all port lines simultaneously. Each bit of dir argument  is responsible for the direction of one line. The line will a
- `function tbt41_port_config_get(byref dir as byte,byref pullup as byte, channel as byte)as ok_ng` — Reads the direction (input/output) and pull-up resistor configuration data. Each bit of dir and pullup reflects the programming of the corresponding line. Curre
- `function tbt41_port_set(data as byte, channel as byte) as ok_ng` — Sets the output states of all port lines. Only lines configured as outputs will be affected. The function will return NG if the execution fails.
- `function tbt41_port_get(byref data as byte, channel as byte)as ok_ng` — Reads the current state of all port lines. Port state is returned through the data argument. The function will return NG if the execution fails.

Enums: `ext_line_name`(EXT_LINE_1, EXT_LINE_2, EXT_LINE_3, EXT_LINE_4, EXT_LINE_5, EXT_LINE_6, EXT_LINE_7, EXT_LINE_8); `tbt41_errcheck`(TBT41_OK, TBT41_SELF_TEST_FAIL, TBT41_NO_SSI_AVAILABLE)

## tibbits/tbt57/tbt57_common.tbh


API:
- `function tbt57_init(byref filename as string, byref spi_num as byte, pin_cs as byte, pin_clk as byte, pin_mosi as byte, pin_miso as byte) as tbt57_errcheck` — Call this function to initialize the Tibbit (using filename file, which must be the correct PGA configuration file). This function will attempt to allocate an S

Enums: `tbt57_errcheck`(TBT57_OK, TBT57_FILE_NOT_ATTACHED, TBT57_INIT_FAILURE, TBT57_NO_SSI_AVAILABLE)

## tibbits/tbt57/tbt57_sled.tbh


API:
- `function tbt57_sled_init(byref spi_num as byte, pin_cs as byte, pin_clk as byte, pin_mosi as byte, pin_miso as byte)as tbt57_errcheck` — Call this function to initialize the Tibbit (start the FPGA and load it with the SPI-to-SK6812RGBW protocol converter). The function relies on tbt57_init() - a 
- `sub tbt57_sled_data_start(pin_cs as byte, spi_num as byte)` — Call this function to start a new SPI transaction, thus resetting the FPGA internal buffer pointer. After that, call tbt57_sled_send_byte() and/or tbt57_sled_se
- `sub tbt57_sled_send_byte(dt as byte)` — Sends one byte into the FPGA's memory buffer. The buffer pointer auto-increments with each byte sent. Buffer capacity is 8192 bytes. tbt57_sled_data_start() mus
- `sub tbt57_sled_send_string(byref s as string)` — Sends a string of byte values into the FPGA's memory buffer. The buffer pointer auto-increments with each byte sent. Buffer capacity is 8192 bytes. tbt57_sled_d
- `sub tbt57_sled_end_and_display(pin_cs as byte)` — Calling this procedure concludes the SPI transaction (data upload into the FPGA), and instructs the FPGA to send the data to the LED chain. After the data is se
- `function tbt57_sled_check_ready(pin_miso as byte) as no_yes` — Returns NO if the FPGA is busy updating LEDs, or YES if the FPGA is idle. This call will only return a meaningful value if invoked outside an SPI transaction, i

## time/datetime.tbh


API:
- `function datetime_to_timestamp(days as word, mins as word, secs as byte) as dword`
- `function datetime_current_timestamp() as dword`
- `function datetime_str_to_timestamp(byref datestr as string, byref format as string) as dword`
- `function datetime_read_number(byref src as string, byref index as word, max_digits as byte) as word`
- `function datetime_next_cron(next_cron as crontab) as dword`
- `function datetime_timestamp_to_string(timestamp as dword, byref format as string) as string`
- `sub datetime_from_timestamp(timestamp as dword, byref days as word, byref mins as word, byref secs as byte)`
- `sub datetime_astro(byref a as astro_struct)`
- `sub datetime_type_convert(byref ts_str as string(14),byref time_daycount as word,byref time_mincount as word,byref bSec as byte, convert_dir as datetime_convert_dir)`
- `sub datetime_string_format(byref result as string(14),`

Enums: `datetime_convert_dir`(TIME_TO_STR, STR_TO_TIME, TIME_TO_BYTESTR, BYTESTR_TO_TIME, STR_TO_BYTESTR, BYTESTR_TO_STR); `en_datetime_rdwr`(TIME_GET, TIME_SET)

## time/time.tbh


API:
- `sub td_get_tzone_offset(timezone as en_td_timezones, byref minutes_offset as integer)`
- `function td_gmt_to_local(byref day_count as word, byref min_count as word, timezone as en_td_timezones, dst as off_on) as ok_ng`
- `function td_local_to_gmt(byref day_count as word, byref min_count as word, timezone as en_td_timezones, dst as off_on) as ok_ng`
- `function td_to_str(byref td_str as string, day_count as word,min_count as word, seconds as byte, mseconds as word) as ok_ng`
- `function td_from_str(byref td_str as string, byref day_count as word, byref min_count as word, byref seconds as byte,byref mseconds as word) as ok_ng`
- `function td_to_binstr(byref td_str as string, day_count as word, min_count as word, seconds as byte, mseconds as word) as ok_ng`
- `function td_from_binstr(byref td_str as string, byref day_count as word, byref min_count as word, byref seconds as byte,byref mseconds as word) as ok_ng`
- `function td_str_to_binstr(byref td_str as string) as ok_ng`
- `function td_binstr_to_str(byref td_str as string) as ok_ng`
- `function td_str_date_time_reformat(byref td_str as string, op as en_td_string_ops, date_format as en_td_date_formats) as ok_ng`
- `function td_str_time_reformat(byref t_str as string, op as en_td_string_ops) as ok_ng`
- `function td_elapsed(end_time as dword) as boolean`

Enums: `en_td_string_ops`(TD_STR_ADD_FORMATTING, TD_STR_REMOVE_FORMATTING); `en_td_timezones`(TD_TIMEZONE_GMT_MINUS_12_00, TD_TIMEZONE_GMT_MINUS_11_00, TD_TIMEZONE_GMT_MINUS_10_00, TD_TIMEZONE_GMT_MINUS_09_00, TD_TIMEZONE_GMT_MINUS_08_00, TD_TIMEZONE_GMT_MINUS_07_00, TD_TIMEZONE_GMT_MINUS_06_00, TD_TIMEZONE_GMT_MINUS_05_00, TD_TIMEZONE_GMT_MINUS_04_30, TD_TIMEZONE_GMT_MINUS_04_00, TD_TIMEZONE_GMT_MINUS_03_30, TD_TIMEZONE_GMT_MINUS_03_00…); `en_td_date_formats`(TD_DATE_FORMAT_YYYYMMDD, TD_DATE_FORMAT_MMDDYYYY, TD_DATE_FORMAT_DDMMYYYY)

## ui/ui.tbh


API:
- `sub device_menu_pre(`
- `sub device_input_box_pre(`
- `sub device_list_box_pre(`
- `sub device_msg_box_pre(`
- `sub device_menu_post(`
- `sub device_input_box_post(`
- `sub device_list_box_post(`
- `sub device_msg_box_post(`
- `function device_settings_sg(setting_name as string(50),index as byte, byref setting_val as string, byref stg_num as byte, rw as en_device_rdwr) as en_stg_status_codes`
- `function device_mb_get_key(mk as en_mb_keys) as string`
- `sub device_mb_interrupt()`
- `sub device_ib_interrupt()`
- `sub device_lb_interrupt()`
- `sub device_tb_interrupt()`
- `sub device_menu_interrupt()`
- `sub device_move_cursor(menu_item as menu_display_item,desc_file as string(30))`
- `sub device_ib_timer_event(byref current_state as input_box_key_actions,byref key_asc as byte,byref insert_mode as no_yes)`
- `sub lcd_clear(x as word, y as word, width as word, height as word)`
- `sub lcd_print_msg(byref msg as string,x as word, y as word, w as word, h as word,al as pl_lcd_text_alignment, bolder as no_yes)`
- `sub reset_keypad()`
- `sub ui_handle_kp(kp_event as pl_kp_event_codes, kp_code as byte)`
- `sub device_menu_key_proc(key_event as pl_kp_event_codes, key_code as byte, byref current_state as menu_key_actions)`
- `sub device_number_key_action(led_key as word,upper_asc as byte,lower_asc as byte, number_asc as byte, byref current_state as input_box_key_actions, byref key_asc as byte, byref insert_mode as no_yes)`
- `sub device_ib_key_proc(key_event as pl_kp_event_codes, key_code as byte, byref current_state as input_box_key_actions, byref key_asc as byte, byref insert_mode as no_yes)`
- `sub device_lb_key_proc(key_event as pl_kp_event_codes, key_code as byte, byref current_state as list_box_key_action)`
- `sub device_mb_key_proc(key_event as pl_kp_event_codes, key_code as byte)`
- `sub set_stg_modified()`
- `sub entering_menu()`
- `sub ui_exit_level()`
- `sub ui_menu_out()`
- `sub ui_menu_exit()`

Enums: `en_mb_keys`(MBK_COMMAND_CONFIRM, MBK_COMMAND_CANCEL, MBK_YES, MBK_NO, MBK_OK, MBK_F1, MBK_F2, MBK_F4); `en_ib_mode`(INPUT_BOX_ALPH_LOWER, INPUT_BOX_ALPH_UPPER, INPUT_BOX_NUMERIC); `en_device_rdwr`(DEVICE_GET, DEVICE_SET); `en_ui_mode`(UI_MODE_NONE, UI_MODE_MENU, UI_MODE_INPUT_BOX, UI_MODE_LIST, UI_MODE_MSG)

## ui/ui_input_box.tbh

Config defines (set before include):
- `RESTART` = no — =========================================================================== ui_input_box library required device specific properties and methods: sub lcd_clear(x as word, y as word, width as word, height as word) sub dev
- `IB_MAX_LEN` = 30
- `LCD_FIX_FONT` = "Tibbo-5x7(V).bin"
- `INPUT_BOX_X` = 0
- `INPUT_BOX_Y` = 0
- `INPUT_BOX_W` = 1
- `INPUT_BOX_H` = 1
- `UIB_HOR_SPACING` = 3

API:
- `function ui_input_box(`
- `sub ui_input_box_key_proc(key_event as pl_kp_event_codes, key_code as byte)`
- `sub ui_input_box_proc_timer()`

Enums: `ui_input_box_results`(INPUT_BOX_RESULT_OK, INPUT_BOX_RESULT_CANCEL, INPUT_BOX_RESULT_TIMEOUT, INPUT_BOX_RESULT_FAIL); `input_box_char_ranges`(INPUT_BOX_CHAR_RANGE_09, INPUT_BOX_CHAR_RANGE_AZ, INPUT_BOX_CHAR_RANGE_09AZ, INPUT_BOX_CHAR_RANGE_DIGITS); `input_box_change_chr_dir`(INPUT_BOX_CHANGE_CHR_FORWARD, INPUT_BOX_CHANGE_CHR_BACKWARD); `input_box_key_actions`(INPUT_BOX_NONE, INPUT_BOX_INPUT, INPUT_BOX_CHAR_FORWARD, INPUT_BOX_CHAR_BACKWARD, INPUT_BOX_POS_FORWARD, INPUT_BOX_POS_BACKWARD, INPUT_BOX_DELETE, INPUT_BOX_DELETE_ALL, INPUT_BOX_CONFIRM, INPUT_BOX_CANCEL, INPUT_BOX_BACKSPACE)

## ui/ui_list_box.tbh

Config defines (set before include):
- `SMALL_ICON_FILE` = "small_icons.bmp" — =========================================================================== ui_list_box libaray required device specific properties and methods: const SYS_ERROR_REBOOT sub lcd_clear(x as word, y as word, width as word, h
- `LCD_STD_FONT` = "Tibbo-5x7(VP).bin"
- `LIST_BOX_CURSOR_STYLE` = 0
- `ULB_VER_SPACING` = 3
- `ULB_HOR_SPACING` = 3
- `DISPLAY_STR_LEN` = 255
- `SCROLL_BORDER` = 2
- `SCROLL_CURSOR_WIDTH` = 5
- `CURSOR_BAR_LEN_OFFSET` = 2
- `SCROLL_BAR_WIDTH` = 5
- `SCROLL_ARROW_HEIGHT` = 5
- `SCROLL_ARROW_X_POS_OFFSET` = 0
- `SCROLL_ARROW_Y_POS_OFFSET` = 2
- `LCD_LOCK` = lcd.lock
- `LCD_UNLOCK` = lcd.lock
- `LCD_BACKCOLOR` = 0

API:
- `sub ui_list_box(`
- `function ui_list_box_ext(`
- `sub ui_list_box_interrupt()`
- `sub ui_list_box_key_proc(key_event as pl_kp_event_codes, key_code as byte)`

Enums: `ui_list_box_results`(LIST_BOX_RESULT_OK, LIST_BOX_RESULT_CANCEL, LIST_BOX_RESULT_TIMEOUT, LIST_BOX_RESULT_FAIL); `list_box_key_action`(LIST_BOX_CURSOR_UP, LIST_BOX_CURSOR_DOWN, LIST_BOX_CONFIRM, LIST_BOX_CANCEL)

## ui/ui_menu.tbh

Config defines (set before include):
- `LCD_FIX_FONT` = "Tibbo-5x7(V).bin" — =========================================================================== ui_menu library required device specific properties and methods: sub lcd_clear(x as word, y as word, width as word, height as word) function dev
- `LCD_STD_FONT` = "Tibbo-5x7(VP).bin"
- `MENU_MAX_LVL` = 5
- `MENU_MAX_ITEM_PER_LVL` = 10
- `BMP_CANCEL_XOFFSET` = 69
- `BMP_ENTER_XOFFSET` = 86
- `BMP_UP_XOFFSET` = 103
- `BMP_DOWN_XOFFSET` = 120
- `LCD_MENU_TOUT` = 200
- `DISPLAY_STR_LEN` = 255
- `UM_VER_SPACING` = 3
- `UM_HOR_SPACING` = 3
- `SCROLL_BAR_WIDTH` = 25
- `SCROLL_ARROW_HEIGHT` = 20
- `SCROLL_MIN_HEIGHT` = 4
- `SCROLL_CUROSR_WIDTH` = 20
- `CURSOR_BAR_LEN_OFFSET` = 2
- `LCD_CURSORCOLOR` = 63080
- `LCD_DISABLE_FORECOLOR` = 33840
- `LCD_FORECOLOR` = 65535
- `SCROLL_BORDER` = 2
- `SMALL_ICON_FILE` = "small_icons.bmp"
- `TAB` = 9
- `CR` = 13
- `COMMA` = 44
- `MENU_IB_INSERT` = NO
- `MENU_SCRIPT_FILE` = "menu_descr.txt"
- `STD_INPUT_WAIT_TIME` = 20
- `LIST_BOX_X` = 0
- `LIST_BOX_Y` = 0
- `LIST_BOX_W` = lcd.width
- `LIST_BOX_H` = lcd.height
- `LCD_BACKCOLOR` = 0
- `UI_TABLE_CONTROL` = 0

API:
- `function ui_menu(`
- `sub ui_menu_key_proc(key_event as pl_kp_event_codes, key_code as byte)`

Enums: `ui_menu_results`(MENU_RESULT_OK, MENU_RESULT_TIMEOUT); `menu_key_actions`(MENU_KEY_UP, MENU_KEY_DOWN, MENU_KEY_IN, MENU_KEY_OUT)

## ui/ui_msg_box.tbh

Config defines (set before include):
- `LCD_STD_FONT` = "Tibbo-5x7(VP).bin" — =========================================================================== ui_msg_box library required device specific properties and methods: sub lcd_clear(x as word, y as word, width as word, height as word)		'clear l
- `MB_MSG_LEN` = 60 — legth of message
- `MSB_VER_SPACING` = 1 — vertical spacing for the message box(number of pixels between lines)
- `MSB_HOR_SPACING` = 1 — horizontal space for the message box(number of pixels between characters)
- `MSG_BOX_BOLDER` = 2 — width of message box bolder(in pixels)
- `MSB_BOLDER_PADDING` = 5 — the space between the bolder and the actual message that is being printed
- `LCD_LOCK` = lcd.lock — lock the lcd(define it as nothing to remove the lcd locking effect)
- `LCD_UNLOCK` = lcd.unlock — lock the lcd(define it as nothing to remove the lcd locking effect)

API:
- `sub ui_msg_box(byref msg as string(60),x as word, y as word, w as word, h as word,align as pl_lcd_text_alignment, byref keycode_str as string(20), bolder as no_yes, timeout as byte)`
- `sub ui_msg_box_key_proc(key_event as pl_kp_event_codes, key_code as byte)`

## upgrade/upgrade.tbh

Config defines (set before include):
- `FD_SECTOR_SIZE` = 256

API:
- `function device_firmware_upload_async(source as PL_FW_UPG_SOURCE, number as byte) as no_yes`
- `function device_firmware_upload_update() as no_yes`
- `sub set_baudrate(baudrate as dword)`
- `sub upgrade_set_buffer(buffer as string)`
- `function get_fw_upg_state() as pl_upg_state_t`
- `sub on_firmware_update_start(byref current_fw_upg_state as pl_upg_state_t)` — Callback when the file type is read to let app know what will be updated.
- `sub on_firmware_update_data_received(byref current_fw_upg_state as pl_upg_state_t)`
- `sub on_firmware_update_percent_change(byref current_fw_upg_state as pl_upg_state_t)` — Callback when data has been written to flash.
- `sub on_firmware_update_file_complete(byref current_fw_upg_state as pl_upg_state_t)` — Callback when all files have been downloaded.
- `sub on_firmware_update_complete(byref current_fw_upg_state as pl_upg_state_t)` — Callback when all files have been downloaded.
- `sub init_serial(port as byte, baud as dword)`
- `sub init_receive_socket(receive_interface as string)`
- `sub device_firmware_write_tios_app(fw as string)`
- `sub device_firmware_write_wa2000_mon_app(fw as string)`
- `sub device_firmware_read_manifest(manifest as string)`
- `sub device_firmware_get_fw_block(byref dev_fw_upg_state as pl_upg_state_t )`
- `function device_firmware_bytes_available() as dword`
- `function device_firmware_read_32_uint() as dword`
- `function get_firmware_index(fwtype as PL_UPG_FW_TYPE) as integer`
- `sub upgrade_WA2000_firmware(fw_type as PL_UPG_FW_TYPE,  index as byte)`

Enums: `PL_FW_UPG_STATE`(PL_FW_UPG__INIT, PL_FW_READ_HEADER, PL_FW_UPG_READ_FW_TYPE, PL_FW_UPG_READ_LEN, PL_FW_UPG_READ_CHECKSUM, PL_FW_UPG_READ_FW, PL_FW_UPG_COMPLETE, PL_FW_UPG_FAIL, PL_FW_UPG_CANCEL); `PL_UPG_FW_TYPE`(TIOS_MON, COMPRESSED_TIOS, UNCOMPRESSED_TIOS, COMPRESSED_APP, UNCOMPRESSED_APP, COMPRESSED_TIOS_APP, UNCOMPRESSED_TIOS_APP, WA2000_MON, WA2000_APP, MANIFEST, WA3000_MON, WA3000_APP); `PL_FW_UPG_SOURCE`(PL_FW_UPG_BLE, PL_FW_UPG_WEB, PL_FW_UPG_SOCK, PL_FW_UPG_SER, PL_FW_UPG_HTTP); `PL_FW_UPG_FAIL_REASON`(PL_FW_FAIL_NONE, PL_FW_FAIL_CANCEL, PL_FW_FAIL_NUMFILES, PL_FW_FAIL_INVALID_FW_TYPE, PL_FW_FAIL_INVALID_FW_LENGTH, PL_FW_FAIL_INVALID_FW_CHECKSUM, PL_FW_FAIL_SOURCE_UNKNOWN, PL_FW__FAIL_INVALID_HARDWARE); `baudrates`(b1200, b2400, b4800, b9600, b19200, b38400, b56000, b57600, b115200, b128000, b153600, b230400…)

## utils/flags.tbh


API:
- `sub declare_ip_set(interface as pl_sock_interfaces)` — ============================================================= FLAG.TBS =============================================================
- `sub declare_ip_obtained(interface as pl_sock_interfaces)`
- `sub declare_error_mode`
- `sub init_x_flags` — Status codes for setting-related operation
- `sub write_x_flag(flag_num as en_x_flags,byref new_val as string, interface as pl_sock_interfaces)`
- `function get_x_flags_net(interface as pl_sock_interfaces) as string(10)`

Enums: `en_x_flags`(EN_X_FLAGS_NORMAL, EN_X_FLAGS_PROG, EN_X_FLAGS_ERROR, EN_X_FLAGS_IP, EN_X_FLAGS_CONN, EN_X_FLAGS_ES, EN_X_FLAGS_SE)

## utils/login_control.tbh


API:
- `function login(new_login as cmd_modes, cmd_data as string(32), socket as byte) as ok_ng`
- `function compare_logins(new_login as cmd_modes, cmd_data as string(32), socket as byte) as login_comparison_codes`
- `sub logout()`
- `sub login_timer_proc()`
- `sub login_timeout_reset()`

Callbacks YOU must implement:
- `sub callback_login_event(mode as cmd_modes)`
- `function callback_get_timeout(mode as cmd_modes) as word`

Enums: `cmd_modes`(CMD_MODE_NONE, CMD_MODE_AGGREGATE, CMD_MODE_INBAND, CMD_MODE_HTTP, CMD_MODE_TELNET, CMD_MODE_UDP, CMD_MODE_SERIAL, CMD_MODE_TERMINAL); `login_comparison_codes`(LC_WILL_ACCEPT, LC_WILL_ACCEPT_REPEATED_LOGIN, LC_WILL_ACCEPT_LOWER_IN_PROGRESS, LC_WILL_REJECT_HIGHER_IN_PROGRESS, LC_WILL_REJECT_SAME_IN_PROGRESS)

## utils/utils.tbh


API:
- `sub base64_encode(byref input_str as string, input_len as byte, byref result as string)`
- `sub base64_decode(byref input as string, byref result as string)`
- `sub time_delay_ms(delay_ms as word)`
- `function abs(Value as real) as real`
- `function sgn(Value as real) as real`
- `function math_pow(base as integer, exp as integer) as real`
- `function math_hex_to_float(byref num as string(8)) as real`
- `function string_to_float(byref s as string) as float`
- `function ftofixed(r as real, decimals as byte) as string`
- `function hex_mac(byref mac as string) as string`
- `sub json_parser_init()`
- `function json_trim(s as string) as string`
- `function json_get_catcode(ch as string(1)) as byte`
- `function json_get_value(byref key as string, byref data as string) as string`
- `function escape_string(data as string) as string`
- `function unescape_string(data as string) as string`
- `function str_to_hex(hash as string) as string`
- `function trim_trailing_zeros(s as string(FLOAT_MAX_STRING_LENGTH)) as string(FLOAT_MAX_STRING_LENGTH)`
- `function float_to_shortest_decimal_precise(f as real) as string(FLOAT_MAX_STRING_LENGTH)`
- `function find_shortest_decimal(f as real) as string(FLOAT_MAX_STRING_LENGTH)`
- `function are_same_ieee754_value(a as real, b as real) as boolean`
- `function fallback_shortest_decimal(f as real) as string`
- `function test_round_trip_accuracy(original as real, decimal_str as string(FLOAT_MAX_STRING_LENGTH)) as boolean`
- `function truncate_last_digit(s as string(FLOAT_MAX_STRING_LENGTH)) as string(FLOAT_MAX_STRING_LENGTH)`
- `function round_up_last_digit(s as string(FLOAT_MAX_STRING_LENGTH)) as string(FLOAT_MAX_STRING_LENGTH)`
- `function str_uppercase(byref s as string) as string`
- `function str_lowercase(byref s as string) as string`
- `function flip_byte(data as byte) as byte`

## wln/wln.tbh

Config defines (set before include):
- `WLN_DEBUG_PRINT` = 0 — 1- debug output enabled, destination depends on WLN_DEBUG_REDIR 0- no debug output.
- `WLN_DEBUG_REDIR` = 0 — Only relevant when WLN_DEBUG_PRINT is 1 1- will invoke callback_wln_debuginfo() to output debug printing 0- will use sys.debugprint to output to console
- `WLN_RESET_MODE` = 0 — 0- dedicated RST line. Remember to define this line's mapping with WLN_RST. 1- CS and CLK lines are to generate reset (special hardware circuit required).
- `WLN_RST` = PL_IO_NULL — RST line mapping. Only relevant when WLN_RESET_MODE=0.
- `WLN_CS` = PL_IO_NULL — CS line mapping.
- `WLN_DI` = PL_IO_NULL — DI line mapping.
- `WLN_DO` = PL_IO_NULL — DO line mapping.
- `WLN_CLK` = PL_IO_NULL — CLK line mapping.
- `WLN_KEEP_ALIVE` = 0 — 0- do not send keepalive UDP datagrams (saves code and memory space). 1- send keepalive UDP datagrams to prevent disassociation from the access point.
- `WLN_KEEP_ALIVE_TOUT` = 120 — Time interval, in 1/2 second increments, between keepalive UDP datagrams. Only relevant when WLN_KEEP_ALIVE=1.
- `WLN_WPA` = 0 — 0- disable WPA1/WPA2 support (saves code and memory space). 1- enable WPA1/WPA2 support.
- `WLN_RESCAN_TMR_CTR_CONNECT` = 120
- `WLN_RESCAN_TMR_CTR_NO_CONNECT` = 140

API:
- `function wln_get_info(info_element as wln_info_elements, byref extra_data as string) as string`
- `function wln_start(byref ap_name as string, security_mode as pl_wln_security_modes, byref key as string, domain as pl_wln_domains, active_scan as no_yes, scanfilter as pl_wln_scan_filter) as en_wln_status_codes`
- `function wln_change(byref ap_name as string,security_mode as pl_wln_security_modes,byref key as string) as en_wln_status_codes`
- `sub wln_stop()`
- `function wln_check_association() as pl_wln_association_states`
- `sub wln_proc_timer()`
- `sub wln_proc_event(wln_event as pl_wln_events)`
- `sub wln_proc_task_complete(completed_task as pl_wln_tasks)`
- `sub wln_proc_data()`
- `function wln_wpa_mkey_get(byref password as string, byref ssid as string) as string`
- `sub wln_update_rssi()`
- `sub wln_start_rescan()`
- `sub wln_check_for_better_ap(rssi_lvl as byte)`
- `sub wln_delay_ms(ms as dword)`
- `sub wln_init()`
- `sub wln_init_gpio()`
- `sub wln_reset()`
- `sub wln_autoconnect(enable as boolean)`

Callbacks YOU must implement:
- `sub callback_wln_failure(wln_state as en_wln_status_codes)`
- `sub callback_wln_ok()`
- `sub callback_wln_starting_association()`
- `sub callback_wln_pre_buffrq(required_buff_pages as byte)`
- `sub callback_wln_mkey_progress_update(progress as byte)`
- `sub callback_wln_rescan_result(current_rssi as byte, scan_rssi as byte, different_ap as no_yes)`
- `sub callback_wln_debugprint(print_data as string)`
- `sub callback_wln_rescan_for_better_ap()`

Enums: `pl_wln_security_modes`(WLN_SECURITY_MODE_DISABLED, WLN_SECURITY_MODE_WEP64, WLN_SECURITY_MODE_WEP128, WLN_SECURITY_MODE_WPA1, WLN_SECURITY_MODE_WPA2); `pl_wln_security_modes`(WLN_SECURITY_MODE_DISABLED, WLN_SECURITY_MODE_WEP64, WLN_SECURITY_MODE_WEP128); `en_wln_status_codes`(WLN_STATUS_OK, WLN_STATUS_OUT_OF_SOCKETS, WLN_STATUS_INSUFFICIENT_BUFFER_SPACE, WLN_STATUS_MISSING_FIRMWARE_FILE, WLN_STATUS_BOOT_FAILURE, WLN_STATUS_INVALID_SECURITY_MODE, WLN_STATUS_INVALID_WEP_KEY, WLN_STATUS_SCANNING_FAILURE, WLN_STATUS_ASSOCIATION_FAILURE, WLN_STATUS_DISASSOCIATION, WLN_STATUS_UNEXPECTED_ERROR, WLN_STATUS_NOT_STARTED…); `wln_info_elements`(WLN_INFO_ELEMENT_REQUIRED_BUFFERS)


# Сверка с docs.tibbo.com (октябрь 2026)

В docs описаны 10 библиотек: AGG, DHCP, FILENUM, GPRS, MQTT, PPPOE, SCAP, SOCK, STG (settings), WLN - около 130 страниц `lib_*`/`library_*`. Сигнатуры выше взяты из актуальных .tbh tibbotech/libraries и новее docs; docs нужны для смысла параметров и порядка подключения. Страницы STG (`lib_stg_*`) в docs пока пустые («reworked»). Остальные библиотеки (dns, http, modbus, sntp, smtp, tibbits/tbtNN, ui и т.д.) в docs не описаны - только .tbh.

## Процедуры из docs, которых нет в .tbh выше (старые версии библиотек)
- `function mqtt_reconnect() as ok_ng` - переподключение с параметрами последнего `mqtt_connect()`; при успехе вызывается `callback_mqtt_connect_ok` (lib_mqtt_mqtt_reconnect).
- `function pppoe_get_info(info_element as pppoe_info_elements, byref extra_data as string) as string` - `PPPOE_INFO_ELEMENT_REQUIRED_BUFFERS`: сколько страниц буфера нужно библиотеке; `extra_data` пустая (lib_pppoe_pppoe_get_info). Enum `pppoe_info_elements` в .tbh есть.
- `function wln_rescan(byref ap_name as string) as en_wln_status_codes` - поиск указанной точки доступа для оценки сигнала (роуминг); возвращает WLN_STATUS_OK / _NOT_STARTED / _BUSY, результат приходит в `callback_wln_rescan_result(current_rssi, scan_rssi, different_ap)`. В новой wln.tbh вместо неё `wln_start_rescan()` и `callback_wln_rescan_for_better_ap()`.

## Сигнатуры: docs (старые) против .tbh (новые)
| Процедура | docs.tibbo.com | .tbh выше |
|---|---|---|
| `mqtt_start` | `sub mqtt_start()` | `mqtt_start(target_interface, server, dst_port, user, password, client_id, encrypted)` |
| `mqtt_connect` | `mqtt_connect(dst_ip, dst_port, user, password, keep_alive as byte) as ok_ng` | `mqtt_connect() as ok_ng` (параметры в mqtt_start) |
| `mqtt_publish` | `(topic, data)` | `(topic, data, qos, retain)`; для больших сообщений `mqtt_start_publish` + `mqtt_continue_publish` |
| `callback_mqtt_notif` | `(topic, data)` | `(topic, data, remaining_bytes as dword)` |
| `wln_start` | `(ap_name, security_mode, key, domain)` | ещё `active_scan as no_yes, scanfilter as pl_wln_scan_filter` |
| `gprs_start` | `(at_dt_command_param, apn)` | ещё `username, password` |
| `callback_dhcp_ok` | `…dhcp_obtained_ip, dhcp_obtained_gateway, dhcp_obtained_netmask, dhcp_obtained_lease_time` | `ip, gateway_ip, netmask, lease_time` (только имена) |

Правило: реализуй колбэки и вызывай процедуры по той .tbh, которая лежит в проекте (`src_lib_ver`), а не по docs.

## #define из docs, расходящиеся со значениями выше
| #define | docs | .tbh |
|---|---|---|
| `DHCP_POST_FAIL_DELAY` | 180 | 60 |
| `MQTT_RX_BUFF` / `MQTT_TX_BUFF` | 1 | 16 |
| `SOCK_MAX_SIGNATURE_LEN` | 0 | 3 |
| `GPRS_MODULE_EXTERNAL` | 0 = встроенный модуль | комментарий в .tbh: 0 = внешний |
| `GPRS_RESET` | 55 | нет в извлечении |
| `GPRS_SER_PORT_RTSMAP`, `GPRS_SER_PORT_CTSMAP` | = GPRS_SER_PORT | нет в извлечении |

## Полезное из docs по работе библиотек
- Все библиотеки с `*_get_info(…_INFO_ELEMENT_REQUIRED_BUFFERS)` сообщают, сколько страниц буфера им нужно: вызывай до `sys.buffalloc` и учитывай в бюджете страниц (ref_libraries_common_get_info).
- `callback_*_pre_buffrq(required_buff_pages)` сообщает, что свободных страниц буфера не хватает и сколько нужно библиотеке.
- DHCP: `DHCP_MAX_RETRIES` попыток в пакете, пауза между попытками случайная 1…`DHCP_MAX_RETRY_DELAY` с, между пакетами `DHCP_POST_FAIL_DELAY`; `callback_dhcp_pre_clear_ip(interface)` - вызывается перед установкой IP интерфейса в 0.0.0.0 (только если IP ещё не 0.0.0.0); по комментарию .tbh соединения через интерфейс при этом рвутся (lib_dhcp_callback_dhcp_pre_clear_ip). На WM2000/WS1102 вместо библиотеки можно использовать встроенный DHCP (`wln.dhcp`, события `on_sys_dhcp_ok/failure`), но тогда `wln.dhcp` и `wln.autodhcp` библиотеке мешают - выключи их, если используешь библиотеку.
- SOCK/FILENUM: `sock_get("SIG")`/`filenum_get("SIG")` возвращают номер или 255, если свободных нет; `sock_who_uses()/filenum_who_uses()` возвращают подпись (нужен `*_MAX_SIGNATURE_LEN > 0`).
