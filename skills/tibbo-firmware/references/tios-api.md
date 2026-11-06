# TiOS API reference (auto-extracted from github.com/tibbotech/platforms)

Source: `Platforms/*.tph` — the same declaration files TIDE uses. Names, signatures and enum members here are exact.
One-line descriptions are truncated; for the full text open the matching .tph or docs.tibbo.com.
Hidden/internal members (declared with `!`) are omitted. Availability depends on the platform — see platforms.md.


## sys.tph


Events:
- `on_sys_init` — First event to be generated after your devices boots up.

## sys-2xxx.tph

**object sys** — This is the system object that loosely combines "general system" stuff such as initialization (boot) event, buffer management, system timer, and some other miscellaneous properties and methods.

Properties:
- `sys.runmode` R/O (ENUM, BYTE). [read-only] — Returns current run (execution) mode: 0- PL_SYS_MODE_RELEASE (release mode), 1- PL_SYS_MODE_DEBUG (debug mode).
- `sys.resettype` R/O (ENUM, BYTE). [read-only] — Returns the type of the most recent hardware reset:0- PL_SYS_RESET_TYPE_INTERNAL (internal reset caused by "self-reboot" of the CPU -- through TIDE command or sys.reboot…
- `sys.extresettype` R/O (BYTE, enum pl_sys_ext_reset_type). [read-only] — Returns the type of external reset that has occurred on the system.
- `sys.totalbuffpages` R/O (WORD). [read-only] — Returns the total amount of memory pages available for buffers (one page= 256 bytes).
- `sys.freebuffpages` R/O (WORD). [read-only] — Returns the number of free (not yet allocated) buffer pages (one page= 256 bytes).
- `sys.version` R/O (STRING). [read-only] — Returns firmware (TiOS) version string.
- `sys.timercount` R/O (WORD). [read-only] — Returns the time (in half-second intervals) elapsed since the device powered up.
- `sys.timercount32` R/O (DWORD). [read-only] — Returns the time (in half-second intervals) elapsed since the device powered up.
- `sys.timercountms` (DWORD) - Returns the amount of time (in milliseconds) elapsed since the device powered up. **[docs.tibbo.com: не R/O, можно перезаписать; диапазон 0–4294967295, затем переход через 0; R/O-вариант - `sys.timercountmse` (object_sys_timercountms)]**
- `sys.onsystimerperiod` (ENUM, BYTE), default= 50 (0.5 seconds) — Defines, in 10ms increments, the period at which the on_sys_timer event will be generated.
- `sys.serialnum` R/O (STRING). [read-only] — Returns the 12-byte or 128-byte string containing the serial number of the device.
- `sys.wdenabled`  - Enables or disables the watchdog timer. **[docs.tibbo.com: enum no_yes, по умолчанию 0 - NO (выключен) (object_wdenabled)]**
- `sys.wdautoreset`  - Enables or disables the automatic reloading of the watchdog by TiOS Value Range -- 0- DISABLED 1- ENABLED (default) By default, sys.wdautoreset is ENABLED, allowing TiOS… **[docs.tibbo.com: по умолчанию 1 - ENABLED (object_wdautoreset)]**
- `sys.wdperiod`  - Sets the timeout period for the watchdog timer. **[docs.tibbo.com: 0–3000 шагов ≈10 мс, по умолчанию 3000 (≈30 с) (object_wdperiod)]**
- `sys.hsclock`  — Enables or disables the HSE (High-Speed External) oscillator and the PLL (Phase-Locked Loop).
- `sys.monversion` R/O (STRING). [read-only] — Returns the version of the Monitor/Loader.
- `sys.timercountmse` R/O . [read-only] — Returns the amount of time (in milliseconds) elapsed since the device powered up.

Methods / functions:
- `sys.halt()` — Stops your program execution (halts VM).
- `sys.reboot()` — Causes your device to reboot through internal reset.
- `sys.buffalloc()` — Allocates buffer memory as previously requested by "buffrq" methods of individual objects (such as ser.rxbuffrq).
- `sys.setserialnum(byref str as string) as ok_ng` — Sets the programmable portion (64 bytes) of the device's 128-byte serial number.
- `sys.trace(byref str as string)` — 
- `sys.debugprint(byref str as string)` — 
- `sys.wdreset()` — Reloads the watchdog timer, preventing it from expiring and causing a system reset.
- `sys.getexceptioninfo(byref hfsr as dword, byref cfsr as dword, byref lr as dword, byref pc as dword, byref current_lr as dword)` — Checks the CPU registers prior to the last crash.
- `sin( angle as float) as float` — Calculates the sin of angle.
- `asin( x as float) as float` — Calculates the arc sin.
- `cos( angle as float) as float` — Calculates the cos of angle.
- `acos( x as float) as float` — Calculates the arc cos.
- `tan( angle as float) as float` — Calculates the tan of angle.
- `atan( x as float) as float` — Calculates the arc tan.
- `sqrt( x as float) as float` — Calculates the square root.
- `atan2( y as float, x as float) as float` — Calculates the square root.
- `sys.delayms(ms as dword)` — Delays the system for at least ms milliseconds.

Events:
- `on_sys_timer` — Periodic event that is generated at intervals defined by the sys.onsystimerperiod property.

Enums:
- `pl_sys_mode`: PL_SYS_MODE_RELEASE, PL_SYS_MODE_DEBUG
- `pl_sys_reset_type`: PL_SYS_RESET_TYPE_INTERNAL, PL_SYS_RESET_TYPE_EXTERNAL
- `pl_sys_ext_reset_type`: PL_SYS_EXT_RESET_TYPE_INTERNAL, PL_SYS_EXT_RESET_TYPE_WATCHDOG, PL_SYS_EXT_RESET_TYPE_POWERUP, PL_SYS_EXT_RESET_TYPE_BROWNOUT, PL_SYS_EXT_RESET_TYPE_RSTPIN
- `pl_sys_speed_choices`: PL_SYS_SPEED_LOW, PL_SYS_SPEED_MEDIUM, PL_SYS_SPEED_FULL

## sys-1xxx.tph

**object sys** — This is the system object that loosely combines "general system" stuff such as initialization (boot) event, buffer management, system timer, and some other miscellaneous properties and methods.

Properties:
- `sys.runmode` R/O (ENUM, BYTE). [read-only] — Returns current run (execution) mode: 0- PL_SYS_MODE_RELEASE (release mode), 1- PL_SYS_MODE_DEBUG (debug mode).
- `sys.resettype` R/O (ENUM, BYTE). [read-only] — Returns the type of the most recent hardware reset:0- PL_SYS_RESET_TYPE_INTERNAL (internal reset caused by "self-reboot" of the CPU -- through TIDE command or sys.reboot…
- `sys.totalbuffpages` R/O (BYTE or WORD). [read-only] — Returns the total amount of memory pages available for buffers (one page= 256 bytes).
- `sys.freebuffpages` R/O (BYTE or WORD). [read-only] — Returns the number of free (not yet allocated) buffer pages (one page= 256 bytes).
- `sys.version` R/O (STRING). [read-only] — Returns firmware (TiOS) version string.
- `sys.timercount` R/O (WORD). [read-only] — Returns the time (in half-second intervals) elapsed since the device powered up.
- `sys.currentpll` R/O (ENUM, BYTE). [read-only] — Returns current PLL mode of the device: 0- OFF (PLL is off, the device runs at low speed with reduced power consumption), 1- YES (PLL is on, the device runs at maximum…
- `sys.onsystimerperiod` (ENUM, BYTE), default= 50 (0.5 seconds) — Defines, in 10ms increments, the period at which the on_sys_timer event will be generated.
- `sys.serialnum` R/O (STRING). [read-only] — Returns the 128-byte string containing the serial number of the device.

Methods / functions:
- `sys.halt()` — Stops your program execution (halts VM).
- `sys.reboot()` — Causes your device to reboot through internal reset.
- `sys.buffalloc()` — Allocates buffer memory as previously requested by "buffrq" methods of individual objects (such as ser.rxbuffrq).
- `sys.newpll(newpllstate as off_on)` — Sets new state of the PLL:0- OFF (PLL will be off, the device will emerge from reset at low speed with reduced power consumption),1- ON (PLL will be on, the device will…
- `sys.setserialnum(byref str as string) as ok_ng` — Sets the programmable portion (64 bytes) of the device's 128-byte serial number.
- `sys.debugprint(byref str as string)` — Sends (prints) a string to the TIDE's console output.

Events:
- `on_sys_timer` — Periodic event that is generated at intervals defined by the sys.onsystimerperiod property.

Enums:
- `pl_sys_mode`: PL_SYS_MODE_RELEASE, PL_SYS_MODE_DEBUG
- `pl_sys_reset_type`: PL_SYS_RESET_TYPE_INTERNAL, PL_SYS_RESET_TYPE_EXTERNAL

## sys-linux.tph

**object sys** — This is the system object that loosely combines "general system" stuff such as initialization (boot) event, buffer management, system timer, and some other miscellaneous properties and methods.

Properties:
- `sys.runmode` R/O (ENUM, BYTE). [read-only] — Returns current run (execution) mode: 0- PL_SYS_MODE_RELEASE (release mode), 1- PL_SYS_MODE_DEBUG (debug mode).
- `sys.totalbuffpages` R/O (WORD). [read-only] — Returns the total amount of memory pages available for buffers (one page= 256 bytes).
- `sys.freebuffpages` R/O (WORD). [read-only] — Returns the number of free (not yet allocated) buffer pages (one page= 256 bytes).
- `sys.version` R/O (STRING). [read-only] — Returns firmware (TiOS) version string.
- `sys.timercount` R/O (WORD). [read-only] — Returns the time (in half-second intervals) elapsed since the device powered up.
- `sys.timercount32` R/O (DWORD). [read-only] — Returns the time (in half-second intervals) elapsed since the device powered up.
- `sys.timercountms` (DWORD) - **[docs.tibbo.com: не R/O, можно перезаписать; диапазон 0–4294967295, затем переход через 0; R/O-вариант - `sys.timercountmse` (object_sys_timercountms)]**
- `sys.onsystimerperiod` (ENUM, BYTE), default= 50 (0.5 seconds) — Defines, in 10ms increments, the period at which the on_sys_timer event will be generated.
- `sys.serialnum` R/O (STRING). [read-only] — Returns the 12-byte or 128-byte string containing the serial number of the device.

Methods / functions:
- `sys.halt()` — Stops your program execution (halts VM).
- `sys.reboot()` — Causes your device to reboot through internal reset.
- `sys.buffalloc()` — Allocates buffer memory as previously requested by "buffrq" methods of individual objects (such as ser.rxbuffrq).
- `sys.debugprint(byref str as string)` — Sends (prints) a string to the TIDE's console output.
- `sys.exec(byref filename as string, byref args as string, byref env as string)` — Executes the Linux program. filename must be either a binary executable, or a script.

Events:
- `on_sys_timer` — Periodic event that is generated at intervals defined by the sys.onsystimerperiod property.

Enums:
- `pl_sys_mode`: PL_SYS_MODE_RELEASE, PL_SYS_MODE_DEBUG

## io-2xxx.tph

Properties:
- `io.intcount`  — io.intcount property.
- `io.intedge`  — io.intedge property.
- `io.intstate`  [read-only] — io.intstate property.
- `io.intmode`  — io.intmode property.

## io-1xxx.tph

**object io** — The io. object controls the I/O lines, 8-bit I/O ports, and interrupt lines of your device. The lists of available I/O lines, ports, and interrupt lines are platform-specific and are defined by pl_io_num, pl_io_port_num, and pl_int_num enums. On this platform, the I/O lines are unidirectional, i.e. 

Properties:
- `io.num` (ENUM, BYTE), default= 0 — Sets/returns the number of the currently selected I/O line.
- `io.portnum` (ENUM, BYTE). default= 0 — Sets/returns the number of the currently selected 8-bit I/O port.
- `io.state` (ENUM, BYTE). default= 1- HIGH (typically) — For the currently selected I/O line (selection is made through the io.num property), sets/returns this line's state.
- `io.portstate` (BYTE). default= 255 (typically) — For the currently selected 8-bit I/O port (selection is made through the io.portnum property), sets/returns the states of 8 port's lines.
- `io.enabled` (ENUM, BYTE). default= 0- NO — For the currently selected I/O line (selection is made through the io.num property), sets/returns the state of the line's output buffer, i.e. configures the line as…
- `io.portenabled` (BYTE). default= 0 — For the currently selected 8-bit I/O port (selection is made through the io.portnum property), sets/returns the state of the port's output buffers, i.e. configures…
- `io.intnum` (ENUM, BYTE). default= 0 — Sets/returns the number of the currently selected interrupt line.
- `io.intenabled` (ENUM, BYTE). default= 0- NO — For the currently selected interrupt line (selection is made through the io.intnum property), enables/disables on_io_int event generation for this line.

Methods / functions:
- `io.invert(num as pl_io_num)` — For the I/O line specified by the num argument, inverts the state of this line (reads its current state and writes an opposite state into the output buffer).
- `io.lineget(num as pl_io_num) as low_high` — For the I/O line specified by the num argument, returns this line's state.
- `io.lineset(num as pl_io_num, state as low_high)` — For the I/O line specified by the num argument, sets the state of this line's output buffer.
- `io.portget(num as pl_io_port_num) as byte` — For the 8-bit I/O port specified by the num argument, returns this port's state.
- `io.portset(num as pl_io_port_num, state as byte)` — For the 8-bit I/O port specified by the num argument, sets the state of this port's output buffers.

Events:
- `on_io_int(linestate as byte)` — Generated when a change of state (from LOW to HIGH or from HIGH to LOW) on one of the enabled interrupt lines is detected.

## net.tph

**object net** — The net object represents an Ethernet interface of your device. This object only specifies various parameters related to the Ethernet interface (IP address, default gateway IP, netmask, etc.) and is not responsible for sending/transmitting network data. The latter is the job of the sock object.

Properties:
- `net.mac` R/O (STRING), default= "as preset during device production". [read-only] — Returns current MAC (hardware Ethernet) address of the device.
- `net.ip` (STRING), default= "1.0.0.1" — Sets/returns the IP address of the Ethernet interface of your device.
- `net.netmask` (STRING), default= "0.0.0.0" — Sets/returns the netmask of the Ethernet interface of your device.
- `net.gatewayip` (STRING), default= "0.0.0.0" - Sets/returns the IP address of the default gateway for the Ethernet interface of your device. **[docs.tibbo.com: default = "127.0.0.1"; записывать можно, только когда ни один сокет не работает через Ethernet (object_net_gatewayip)]**
- `net.failure` R/O (ENUM, BYTE), default= 0- NO (no failure). [read-only] — Reports whether the Network Interface Controller (NIC) IC has failed: 0- NO (no failure), 1- YES (NIC failure).
- `net.linkstate` R/O (ENUM, BYTE), default= 0- PL_NET_LINKSTAT_NOLINK (no link). [read-only] — Returns current link status of the Ethernet port of the device: 0- PL_NET_LINKSTAT_NOLINK (no link), 1- PL_NET_LINKSTAT_10BASET (linked at 10Mbit/s), 2-…

Events:
- `on_net_link_change` — Generated when the state of the physical link of Ethernet port changes.
- `on_net_overrun` — Generated when overflow occurs on the internal RX buffer of the Network Interface Controller (NIC) IC.

Enums:
- `pl_net_linkstate`: PL_NET_LINKSTAT_NOLINK, PL_NET_LINKSTAT_10BASET, PL_NET_LINKSTAT_100BASET

## sock.tph

**object sock** — This is the sockets object that encompasses ALL available sockets. Total number of sockets is typically 16 but can be less due to memory limitations of a particular platform. The number of available sockets can be obtained through the sock.numofsock read-only property. Selection of a particular sock

Properties:
- `sock.numofsock` R/O (BYTE). [read-only] — Returns total number of sockets available on the current platform.
- `sock.num` (BYTE), default= 0 (socket #0 selected) — Sets/returns the number of the currently selected socket (sockets are enumerated from 0).
- `sock.state` R/O (ENUM, BYTE), default= 0 - PL_SST_CLOSED (connection is closed). [read-only] — For the currently selected socket (selection is made through sock.num), returns the "detailed" current socket state (as opposed to the sock.event property, which retuns…
- `sock.statesimple` R/O (ENUM, BYTE), default= 0-PL_SST_SIMPLE_CLOSED (connection is closed). [read-only] — For the currently selected socket (selection is made through sock.num) returns "simplified" current socket state (as opposed to on_sock_event that retuns simplified…
- `sock.inconmode` (ENUM, BYTE), default= 0- PL_SOCK_INCONMODE_NONE (does not accept any incoming connections) — For the currently selected socket (selection is made through sock.num) specifies whether incoming connections (passive opens) will be accepted and, if yes, from which…
- `sock.reconmode` (ENUM, BYTE), default= 0- PL_SOCK_RECONMODE_0 — For the currently selected socket (selection is made through sock.num) whether the socket accepts reconnects, and, if yes, from which sources.
- `sock.localportlist` (STRING), default= "" (empty string) — For the currently selected socket (selection is made through sock.num) sets/returns the list of listening ports on any of which this socket will accept an incoming UDP…
- `sock.httpportlist` (STRING), default= "" (empty string) — For the currently selected socket (selection is made through sock.num) sets/returns the list of listening ports on any of which this socket will accept an incoming HTTP…
- `sock.localport` R/O (WORD), default= 0. [read-only] — For the currently selected socket (selection is made through sock.num) returns current local port of the socket.
- `sock.outport` (WORD), default= 0 (automatic) — For the currently selected socket (selection is made through sock.num) sets/returns the number of the port that will be used by the socket to establish outgoing…
- `sock.acceptbcast` (ENUM, BYTE), default= 0-NO — For the currently selected socket (selection is made through sock.num) specifies whether the socket will accept incoming broadcast UDP datagrams: 0- NO (won't accept…
- `sock.targetip` (STRING), default= "0.0.0.0" — For active opens on the currently selected socket (selection is made through sock.num) specifies the target IP to which the socket will attempt to connect to.
- `sock.targetmac` (STRING), default= "0.0.0.0.0.0" — 
- `sock.targetport` (WORD), default= 0 — For active opens on the currently selected socket (selection is made through sock.num) specifies the target port to which the socket will attempt to connect to.
- `sock.targetbcast` (ENUM, BYTE), default= 0- NO — For the currently selected socket (selection is made through sock.num) specifies whether this port will be sending its outgoing UDP datagrams as link-level broadcasts:…
- `sock.remotemac` R/O (STRING), default= "0.0.0.0.0.0". [read-only] — For the currently selected socket (selection is made through sock.num) returns the MAC address of the host with which this socket had the most recent or currently has a…
- `sock.remoteip` R/O (STRING), default= "0.0.0.0". [read-only] — For the currently selected socket (selection is made through sock.num) returns the IP address of the host with which this socket had the most recent or currently has a…
- `sock.remoteport` R/O (WORD), default= 0. [read-only] — For the currently selected socket (selection is made through sock.num) returns the port number of the host with which this socket had the most recent or currently has a…
- `sock.bcast` R/O (ENUM BYTE), default= 0- NO. [read-only] — For the currently selected socket (selection is made through sock.num) reports whether the current or most recently received UDP datagram was a broadcast one.
- `sock.protocol` (ENUM, BYTE), default= 0- PL_SOCK_PROTOCOL_UDP (UDP transport protocol for the socket) — For the currently selected socket (selection is made through sock.num ) selects the transport protocol: 0- PL_SOCK_PROTOCOL_UDP (UDP transport protocol), 1-…
- `sock.splittcppackets` (ENUM, BYTE), default= 0 - NO — For the currently selected socket (selection is made through sock.num), specifies whether the program will have additional control over the size of TCP packets being…
- `sock.httpmode` (ENUM BYTE), default= 0- NO (not in HTTP mode) — For the currently selected socket (selection is made through sock.num) specifies whether this socket is in the HTTP mode: 0- NO ("regular" TCP connection), 1- YES (TCP…
- `sock.httpnoclose` (ENUM, BYTE), default= 0- NO (will be closed) — For the currently selected socket (selection is made through sock.num) sets/returns whether TCP HTTP connection will be kept opened after the HTTP request has been…
- `sock.connectiontout` (WORD), default= 0 (no timeout) — For the currently selected socket (selection is made through sock.num) sets/returns connection timeout threshold for the socket in half-second increments.
- `sock.toutcounter` R/O (WORD), default= 0 [read-only] — For the currently selected socket (selection is made through sock.num) returns the time, in 0.5 second intervals, elapsed since the data was last send or received on…
- `sock.inbandcommands` (ENUM, BYTE), default= 0 - NO (inband commands disabled) — For the currently selected socket (selection is made through sock.num), specifies whether inband command passing is allowed: 0 - NO (inband commands are not allowed), 1…
- `sock.escchar` (BYTE), default= 255 — For the currently selected socket (selection is made through sock.num) specifies the ASCII code of the character that will be used as an escape character for inband…
- `sock.endchar` (BYTE), default= 13 (CR) — For the currently selected socket (selection is made through sock.num) specifies the ASCII code of the character that will end inband command (message).
- `sock.gendataarrivalevent` (BYTE), default= 1- YES (on_sock_data_arrival event will be generated) — For the currently selected socket (selection is made through sock.num) specifies whether the on_sock_data_arrival event will be generated once there is some data in the…
- `sock.rxbuffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current RX buffer capacity in bytes.
- `sock.txbuffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current TX buffer capacity in bytes.
- `sock.cmdbuffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current CMD buffer capacity in bytes.
- `sock.rplbuffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current RPL buffer capacity in bytes.
- `sock.varbuffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current VAR buffer capacity in bytes.
- `sock.tx2buffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num) returns current TX2 buffer capacity in bytes.
- `sock.httprqtype` R/O (ENUM, BYTE), default= 0 (PL_SOCK_HTTP_RQ_GET). [read-only] — For the currently selected socket (selection is made through sock.num), and provided that this socket is running in the HTTP mode (sock.httpmode= 1- YES), returns the…
- `sock.rxlen` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns total number of bytes currently waiting in the RX buffer to be extracted and processed by your…
- `sock.txlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the total number of bytes currently found in the TX buffer (including the uncommitted data).
- `sock.txfree` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the amount of free space in the TX buffer in bytes.
- `sock.newtxlen` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the amount of uncommitted TX data in bytes.
- `sock.httprqstring` R/O (STRING), default= "". [read-only] — For the selected socket (selection is made through sock.num) returns up to 255 bytes of the HTTP request string stored in the VAR buffer.
- `sock.rxpacketlen` R/O (WORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the length (in bytes) of the UDP datagram being extracted from the RX buffer.
- `sock.cmdlen` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the length of data (in bytes) waiting to be processed in the CMD buffer.
- `sock.varlen` R/O (WORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the length of data (in bytes) waiting to be processed in the VAR buffer.
- `sock.rpllen` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the length of data (in bytes) waiting to be send out from the RPL buffer; this is the buffer that…
- `sock.rplfree` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the free space (in bytes) available in the RPL buffer; this is the buffer that stores outgoing…
- `sock.tx2len` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through sock.num) returns the amount of data waiting to be sent out in the TX2 buffer; this is the buffer that is needed to…
- `sock.inconenabledmaster` (ENUM, BYTE), default= 1- YES (incoming connections are globally enabled) — A master switch that globally defines whether incoming connections will be accepted: 0- NO (no socket will be allowed to accept an incoming connection), 1- YES (incoming…
- `sock.urlsubstitutes` (STRING), default= "" (no substitutes set) — A comma-separated list of filenames whose extensions will be automatically substituted for .html by the internal webserver of your device.
- `sock.sinkdata` (ENUM, BYTE), default= 0 - NO (normal data processing) — For the currently selected socket (selection is made through sock.num), specifies whether the incoming data should be discarded.
- `sock.allowedinterfaces` (STRING), default=is platform-dependent — For the selected socket (selection is made through sock.num) defines the list of network interfaces on which this socket will accept incoming connections.
- `sock.availableinterfaces` R/O (WORD). [read-only] — Returns the comma-delimited list of network interfaces available on this platform.
- `sock.targetinterface` (ENUM, BYTE), default= 1- PL_SOCK_INTERFACE_NET — .
- `sock.currentinterface` R/O (ENUM, BYTE), default= 0- PL_SOCK_INTERFACE_NULL [read-only] — .

Methods / functions:
- `sock.gethttprqstring(maxinplen as word) as string` — For the selected socket (selection is made through sock.num) extracts up to 255 bytes of the HTTP request string from the VAR buffer.
- `sock.rxclear()` — For the selected socket (selection is made through sock.num) clears (deletes all data from) the RX buffer.
- `sock.txclear()` — For the selected socket (selection is made through sock.num) clears (deletes all data from) the TX buffer.
- `sock.getdata(maxinplen as word) as string` — For the selected socket (selection is made through sock.num) returns the string that contains the data extracted from the RX buffer.
- `sock.peekdata(maxinplen as word) as string` — METHOD.
- `sock.setdata(byref txdata as string)` — For the selected socket (selection is made through sock.num) adds the data passed in the txdata argument to the contents of the TX buffer.
- `sock.send()` — For the selected socket (selection is made through sock.num) commits (allows sending) the data that was previously saved into the TX buffer using the sock.setdata method.
- `sock.getinband as string` — For the selected socket (selection is made through sock.num) returns the string that contains the data extracted from the CMD buffer; this is the buffer that accumulates…
- `sock.peekinband as string` — METHOD.
- `sock.setsendinband(byref data as string)` — For the selected socket (selection is made through sock.num) puts the data into the RPL buffer; this is the buffer that stores outgoing inband replies (messages).
- `sock.notifysent(threshold as word)` — Using this method for the selected socket (selection is made through sock.num) will cause the on_sock_data_sent event to be generated when the amount of committed data…
- `sock.nextpacket()` — For the selected socket (selection is made through sock.num) in the UDP mode ( sock.protocol= 0- PL_SOCK_PROTOCOL_UDP) closes processing of current UDP datagram and…
- `sock.connect()` — For the selected socket (selection is made through sock.num) causes the socket to attempt to connect to the target host specified by the sock.targetport and…
- `sock.close()` — For the selected socket (selection is made through sock.num) causes the socket to close the connection with the other host.
- `sock.reset()` — For the selected socket (selection is made through sock.num) causes the socket to abort the connection with the other host.
- `sock.discard()` — For the selected socket (selection is made through sock.num) causes the socket to discard the connection with the other host.
- `sock.rxbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the RX buffer of the socket.
- `sock.txbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the TX buffer of the socket.
- `sock.cmdbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the CMD buffer of the socket; this is…
- `sock.rplbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the RPL buffer of the socket; this is…
- `sock.varbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the VAR buffer of the socket; this is…
- `sock.tx2buffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through sock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the TX2 buffer of the socket; this…
- `sock.redir(redir as pl_redir) as pl_redir` — For the currently selected socket (selection is made through sock.num), redirects the data being RXed to the TX buffer of the same socket, different socket, or another…

Events:
- `on_sock_inband` — At least one data byte is present in the CMD buffer (sock.cmdlen>0).
- `on_sock_postdata` — Generated when at least one data byte is present in the VAR buffer of the socket, but only after the VAR buffer has become full at least once in the cause of the current…
- `on_sock_data_arrival` — When the event handler for this event is entered, the sock.num property is automatically switched to the socket for which this event was generated.
- `on_sock_event(newstate as pl_sock_state,newstatesimple as pl_sock_state_simple)` — Notifies your program that the socket state has changed.
- `on_sock_overrun` — Data overrun has occurred in the RX buffer of the socket.
- `on_sock_data_sent` — Generated after the total amount of committed data in the TX buffer of the socket (sock.txlen) is found to be less than the threshold that was preset through the…
- `on_sock_tcp_packet_arrival(len as word)` — Notifies your program that the TCP packet of a certain size has arrived.

Enums:
- `pl_sock_state`: PL_SST_CLOSED=0, PL_SST_CL_PCLOSED, PL_SST_CL_ACLOSED, PL_SST_CL_PRESET_POPENING, PL_SST_CL_PRESET_AOPENING, PL_SST_CL_PRESET_EST, PL_SST_CL_PRESET_PCLOSING, PL_SST_CL_PRESET_ACLOSING, PL_SST_CL_PRESET_STRANGE, PL_SST_CL_ARESET_CMD, PL_SST_CL_ARESET_RE_PO, PL_SST_CL_ARESET_RE_AO, PL_SST_CL_ARESET_RE_EST, PL_SST_CL_ARESET_RE_PC, PL_SST_CL_ARESET_RE_AC, PL_SST_CL_ARESET_TOUT, PL_SST_CL_ARESET_DERR, PL_SST_CL_DISCARDED_CMD, PL_SST_CL_DISCARDED_PO_WCS, PL_SST_CL_DISCARDED_AO_WCS, PL_SST_CL_DISCARDED_ARPFL, PL_SST_CL_DISCARDED_TOUT, PL_SST_ARP=&h20, PL_SST_PO=&h40, PL_SST_AO=&h60, PL_SST_EST=&h80, PL_SST_EST_POPENED=&h80, PL_SST_EST_AOPENED, PL_SST_EST_TLS=&h82, PL_SST_EST_TLS_FAILED=&h83, PL_SST_PC=&hA0, PL_SST_AC=&hC0
- `pl_sock_state_simple`: PL_SSTS_CLOSED, PL_SSTS_ARP, PL_SSTS_PO, PL_SSTS_AO, PL_SSTS_EST, PL_SSTS_PC, PL_SSTS_AC
- `pl_sock_inconmode`: PL_SOCK_INCONMODE_NONE, PL_SOCK_INCONMODE_SPECIFIC_IPPORT, PL_SOCK_INCONMODE_SPECIFIC_IP_ANY_PORT, PL_SOCK_INCONMODE_ANY_IP_ANY_PORT
- `pl_sock_reconmode`: PL_SOCK_RECONMODE_0, PL_SOCK_RECONMODE_1, PL_SOCK_RECONMODE_2, PL_SOCK_RECONMODE_3
- `pl_sock_protocol`: PL_SOCK_PROTOCOL_UDP, PL_SOCK_PROTOCOL_TCP, PL_SOCK_PROTOCOL_RAW
- `pl_http_rq_type`: PL_SOCK_HTTP_RQ_GET, PL_SOCK_HTTP_RQ_POST

## ser.tph

**object ser** — This is a serial port object that encompasses ALL serial ports (UARTs) available on a particular system (total number of available serial ports can be obtained through the ser.numofports read-only property). Selection of a particular port to work with is done through the ser.num property. Most other

Properties:
- `ser.numofports` READ-ONLY PROPERTY (BYTE). [read-only] — Returns total number of serial ports found on the current platform.
- `ser.num` (BYTE), default= 0 (serial port #0 selected) — Sets/returns the number of currently selected serial port (ports are enumerated from 0).
- `ser.enabled` (ENUM, BYTE), default= 0- NO — (not enabled).
- `ser.mode` (ENUM, BYTE), default= 0- UART (UART) — Sets operating mode for the currently selected serial port (selection is made through ser.num): 0- PL_SER_MODE_UART (UART), 1- PL_SER_MODE_WIEGAND (Wiegand), 2-…
- `ser.interface` (ENUM, BYTE), default= 0- PL_SER_SI_FULLDUPLEX (full-duplex) — Chooses full-duplex or half-duplex operating mode for currently selected serial port (selection is made through ser.num): 0- PL_SER_SI_FULLDUPLEX (full-duplex mode), 1-…
- `ser.flowcontrol` (ENUM, BYTE), default= 0- DISABLED — Sets/returns flow control mode for currently selected serial port (selection is made through ser.num): 0- DISABLED, 1- PL_SER_FC_RTSCTS, or 1- PL_SER_FC_XONXOFF.
- `ser.rtsmap` (ENUM, BYTE), default=- different for each serial port: UART0: 0- PL_IO_NUM_0, UART1: 1- PL_IO_NUM_1, UART2: 2- PL_IO_NUM_2, UART3: 3- PL_IO_NUM_3 — Sets/returns the number of the I/O line that will act as RTS/W0out/cout output of currently selected serial port (selection is made through ser.num).
- `ser.ctsmap` (ENUM, BYTE), default=- different for each serial port: UART0: 0- PL_INT_NUM_0, UART1: 1- PL_INT_NUM_1, UART2: 2- PL_INT_NUM_2, UART3: 3- PL_INT_NUM_3 — Sets/returns the number of I/O line that will act as CTS/W0&1in/cin input of currently selected serial port (selection is made through ser.num).
- `ser.xonchar` (BYTE), default= &h11 (XON character) — Sets/returns the ASCII code of the character that will be used to PAUSE transmission in the XON/XOFF flow control mode (ser.flowcontrol= 2- PL_SER_FC_XONOFF) for the…
- `ser.xoffchar` (BYTE), default= &h13 (XOFF character) — Sets/returns the ASCII code of the character that will be used to RESUME transmission in the XON/XOFF flow control mode (ser.flowcontrol= 2- PL_SER_FC_XONOFF) for the…
- `ser.dircontrol` (ENUM, BYTE), default= 0- PL_SER_DCP_LOWFORINPUT (LOW for input) — Sets/returns the polarity of the direction control line (RTS) for selected serial port (selection is made through ser.num): 0- PL_SER_DCP_LOWFORINPUT (DIR LOW for input,…
- `ser.baud` (ENUM, BYTE), default= 12- PL_SER_BAUD_9600 — Sets/returns the baudrate for the selected serial port (selection is made through ser.num).
- `ser.baudrate` (WORD), default= "platform-dependent, results in 9600 bps" — Sets/returns the baudrate "divisor value" for the selected serial port (selection is made through ser.num).
- `ser.baudrate` (WORD), default= "platform-dependent, results in 9600 bps" — Sets/returns the baudrate "divisor value" for the selected serial port (selection is made through ser.num).
- `ser.parity` (ENUM, BYTE), default= 0- PL_SER_PR_NONE (no parity) — Sets/returns the parity mode for the selected serial port (selection is made through ser.num): 0- PL_SER_PR_NONE (no parity), 1- PL_SER_PR_EVEN (even parity), 2-…
- `ser.parity` (ENUM, BYTE), default= 0- PL_SER_PR_NONE (no parity) — Sets/returns the parity mode for the selected serial port (selection is made through ser.num): 0- PL_SER_PR_NONE (no parity), 1- PL_SER_PR_EVEN (even parity), 2-…
- `ser.bits` (ENUM, BYTE), default= 1- PL_SER_BB_8 (8 bits) — Specifies the number of data bits in a word TXed/RXed by the currently selected serial port (selection is made through ser.num): 0- PL_SER_BB_7 (7 bits/word), or 1-…
- `ser.bits` (ENUM, BYTE), default= 1- PL_SER_BB_8 (8 bits) — Specifies the number of data bits in a word TXed/RXed by the currently selected serial port (selection is made through ser.num): 0- PL_SER_BB_7 (7 bits/word), or 1-…
- `ser.interchardelay` (BYTE), default= 0 (no delay) — Sets/returns maximum intercharacter delay for the selected serial port (selection is made through ser.num) in 10ms steps.
- `ser.autoclose` (ENUM, BYTE), default= 0- NO — .
- `ser.esctype` (ENUM, BYTE), default= 0- PL_SER_ET_DISABLED (escape sequences disabled) — Defines, for selected serial port (selection is made through ser.num) whether serial escape sequence recognition is enabled and, if yes, what type of escape sequence is…
- `ser.escchar` (BYTE), default= 1 (SOH character) — For selected serial port (selection is made through ser.num) sets/retrieves ASCII code of the escape character used for type1 or type2 serial escape sequences.
- `ser.rxbuffsize` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num)returns current RX buffer capacity in bytes.
- `ser.txbuffsize` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num) returns current TX buffer capacity in bytes.
- `ser.rxlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num) returns total number of committed bytes currently waiting in the RX buffer to be extracted and processed…
- `ser.txlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num) returns total number of committed bytes currently found in the TX buffer.
- `ser.txfree` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num )returns the amount of free space in the TX buffer in bytes, not taking into account uncommitted data.
- `ser.newtxlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — For the selected serial port (selection is made through ser.num) returns the amount of uncommitted TX data in bytes.
- `ser.div9600` R/O (WORD), default= "platform dependent". [read-only] — Returns the value to which the ser.baudrate property must be set in order to achieve the baudrate of 9600bps under present operating conditions.
- `ser.sinkdata` (ENUM, BYTE), default= 0- NO (normal data processing) — For the currently selected serial port (selection is made through ser.num) specifies whether the incoming data should be discarded.

Methods / functions:
- `ser.rxclear` — For the selected serial port (selection is made through ser.num) clears (deletes all data from) the RX buffer.
- `ser.txclear` — For the selected serial port (selection is made through ser.num) clears (deletes all data from) the TX buffer.
- `ser.getdata(maxinplen as word) as string` — For the selected serial port (selection is made through ser.num ) returns the string that contains the data extracted from the RX buffer.
- `ser.peekdata(maxinplen as word) as string` — METHOD.
- `ser.setdata(byref txdata as string)` — For the selected serial port (selection is made through ser.num) adds the data passed in the txdata argument to the contents of the TX buffer.
- `ser.send()` — For the selected serial port (selection is made through ser.num) commits (allows sending) the data that was previously saved into the TX buffer using the ser.setdata…
- `ser.notifysent(threshold as word)` — Using this method for the selected serial port (selection is made through ser.num) will cause the on_ser_data_sent event to be generated when the amount of committed…
- `ser.rxbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected serial port (selection is made through ser.num ) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the RX buffer of the serial port.
- `ser.txbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected serial port (selection is made through ser.num ) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the TX buffer of the serial port.
- `ser.redir(redir as pl_redir) as pl_redir` — For the selected serial port (selection is made through ser.num) redirects the data being RXed to the TX buffer of the same serial port, different serial port, or…

Events:
- `on_ser_esc` — Generated when currently enabled escape sequence is detected in the received UART data stream.
- `on_ser_data_arrival` — Generated when at least one data byte is present in the RX buffer of the serial port (i.e. for this port the ser.rxlen)>0).
- `on_ser_data_sent` — Generated after the total amount of committed data in the TX buffer of the serial port (ser.txlen) is found to be less than the threshold that was preset through the…
- `on_ser_overrun` — Generated when data overrun has occurred in the RX buffer of the serial port.

Enums:
- `pl_ser_mode`: PL_SER_MODE_UART, PL_SER_MODE_WIEGAND, PL_SER_MODE_CLOCKDATA
- `pl_ser_interface`: PL_SER_SI_FULLDUPLEX, PL_SER_SI_HALFDUPLEX
- `pl_ser_flowcontrol`: PL_SER_FC_DISABLED, PL_SER_FC_RTSCTS, PL_SER_FC_XONOFF
- `pl_ser_dircontrol`: PL_SER_DCP_LOWFORINPUT, PL_SER_DCP_HIGHFORINPUT
- `pl_ser_baud`: PL_SER_BAUD_110=109091, PL_SER_BAUD_300=40000, PL_SER_BAUD_1200=10000, PL_SER_BAUD_2400=5000, PL_SER_BAUD_4800=2500, PL_SER_BAUD_9600=1250, PL_SER_BAUD_19200=625, PL_SER_BAUD_38400=313, PL_SER_BAUD_57600=208, PL_SER_BAUD_115200=104, PL_SER_BAUD_230400=52, PL_SER_BAUD_460800=26
- `pl_ser_baud`: PL_SER_BAUD_1200=50000, PL_SER_BAUD_2400=25000, PL_SER_BAUD_4800=12500, PL_SER_BAUD_9600=6250, PL_SER_BAUD_19200=3125, PL_SER_BAUD_38400=1563, PL_SER_BAUD_57600=1042, PL_SER_BAUD_115200=521, PL_SER_BAUD_230400=260, PL_SER_BAUD_460800=130, PL_SER_BAUD_921600=65
- `pl_ser_baud`: PL_SER_BAUD_2400=37376, PL_SER_BAUD_4800=18688, PL_SER_BAUD_9600=9344, PL_SER_BAUD_19200=4672, PL_SER_BAUD_38400=2336, PL_SER_BAUD_57600=1557, PL_SER_BAUD_115200=779, PL_SER_BAUD_230400=389, PL_SER_BAUD_460800=195, PL_SER_BAUD_921600=97
- `pl_ser_baud`: PL_SER_BAUD_50, PL_SER_BAUD_75, PL_SER_BAUD_110, PL_SER_BAUD_134, PL_SER_BAUD_150, PL_SER_BAUD_200, PL_SER_BAUD_300, PL_SER_BAUD_600, PL_SER_BAUD_1200, PL_SER_BAUD_1800, PL_SER_BAUD_2400, PL_SER_BAUD_4800, PL_SER_BAUD_9600, PL_SER_BAUD_19200, PL_SER_BAUD_38400, PL_SER_BAUD_57600, PL_SER_BAUD_115200, PL_SER_BAUD_230400, PL_SER_BAUD_460800, PL_SER_BAUD_500000, PL_SER_BAUD_576000, PL_SER_BAUD_921600, PL_SER_BAUD_1000000, PL_SER_BAUD_1152000, PL_SER_BAUD_1500000, PL_SER_BAUD_2000000, PL_SER_BAUD_2500000, PL_SER_BAUD_3000000, PL_SER_BAUD_3500000, PL_SER_BAUD_4000000
- `pl_ser_parity`: PL_SER_PR_NONE, PL_SER_PR_EVEN, PL_SER_PR_ODD, PL_SER_PR_MARK, PL_SER_PR_SPACE
- `pl_ser_bits`: PL_SER_BB_7, PL_SER_BB_8
- `pl_ser_esctype`: PL_SER_ET_DISABLED, PL_SER_ET_TYPE1, PL_SER_ET_TYPE2

## romfile.tph

**object romfile** — The romfile object allows you to access resource (fixed) files that you have added to your project. Resource files appear under the "Resource Files" branch of your project tree. Resource files are not processed by the compiler in any way, they are just added to the compiled project binary "as is". R

Properties:
- `romfile.offset` R/O (DWORD) [read-only] — .
- `romfile.pointer` (WORD) [LEGACY] — Sets/returns the current pointer position in the currently opened resource file.
- `romfile.pointer32` (DWORD) — Sets/returns the current pointer position in the currently opened resource file.
- `romfile.size` R/O (DWORD). [read-only] — Returns the size of the currently opened resource file.

Methods / functions:
- `romfile.find(frompos as dword, byref substr as string, num as word) as word` — Locates the Nth occurrence of a substring within the currently opened resource file.
- `romfile.find32(frompos as dword, byref substr as string, num as word) as dword` — Locates the Nth occurrence of a substring within the currently opened resource file.
- `romfile.getdata(maxinplen as byte) as string` — Reads the specified amount of bytes (characters) from the currently opened resource file, from the location pointed at by the file pointer (romfile.pointer32).
- `romfile.open(byref filename as string)` — Opens or re-opens a resource file.

## stor.tph

**object stor** — The stor object provides access to the non-volatile (EEPROM) memory in which your application can store data that must not be lost when the device is switched off. Using this object you can also access and change the MAC address of the device (be careful with that!).

Properties:
- `stor.base` (WORD), default= 8 - Returns the base address of the EEPROM from which the area available to your application starts. **[docs.tibbo.com: по умолчанию = размер специальной конфигурационной области + 1. На большинстве платформ область 28 байт (8 байт MAC + 20 байт пароль) → stor.base = 29; у DS1101/DS1102 область 8 байт → 9, у DS1100 EEPROM 208 байт. Физический адрес = startaddr + stor.base − 1 (object_stor_base, ref_platforms_eeprom_conf_section, dsws110x_flash_eeprom)]**
- `stor.size` R/O (WORD), default= "actual_EEPROM_capacity-8" [read-only] - Returns total EEPROM memory capacity (in bytes) for the current device. **[docs.tibbo.com: размер области приложения = ёмкость − (stor.base − 1), т.е. обычно ёмкость − 28 (object_stor_size)]**

Methods / functions:
- `stor.getdata(startaddr as word, len as byte) as string` - Reads up to len number of bytes from the EEPROM starting from address startaddr (addresses are counted from 1). **[docs.tibbo.com: см. также `stor.setdata(byref datatoset as string, startaddr as word) as byte` - пишет данные, возвращает число реально записанных байт; успех, только если оно равно len(datatoset); startaddr=0 трактуется как 1 (object_stor_setdata)]**

## fd.tph

**object fd** — This is the flash disk (fd.) object, it allows you to save data in the flash memory of your device. The fd. object can be used to work with the flash memory in two different ways. You can (1) read and write individual sectors of the flash memory directly, or (2) create a formatted disk that stores f

Properties:
- `fd.availableflashspace` R/O (WORD). [read-only] — Returns the total number of sectors available to store application's data.
- `fd.buffernum` (BYTE), default= 0 (RAM buffer #0 selected) — Sets/returns the number of the RAM buffer that will be used for direct sector access.
- `fd.capacity` R/O (WORD). [read-only] — Returns the capacity, in sectors, of the currently existing flash disk.
- `fd.filenum` (BYTE), default= 0 (file #0 selected) — Sets/returns the number of the currently selected file.
- `fd.fileopened` R/O (ENUM, BYTE), default= 0- NO (no file is currently opened on this file number). [read-only] — Reports if any file is currently opened "on" the selected file number (selection is made through fd.filenum.
- `fd.filesize` R/O (DWORD). [read-only] — Returns the size, in bytes, of the file opened "on" the currently selected file number (selection is made through fd.filenum).
- `fd.laststatus` R/O (ENUM, BYTE), default= 0- PL_FD_STATUS_OK (completed successfully). [read-only] — Returns the execution result for the most recent disk-related method execution.
- `fd.maxopenedfiles` R/O (BYTE). [read-only] — Returns the total number of files that can be simultaneously opened by your application.
- `fd.maxstoredfiles` R/O (BYTE). [read-only] — Returns the total number of files that can be simultaneously stored on the currently existing flash disk.
- `fd.numservicesectors` R/O (BYTE). [read-only] — Returns the total number of sectors occupied by the "housekeeping" data of the currently existing flash disk.
- `fd.pointer` R/O (DWORD). [read-only] — Returns the pointer position for the file opened "on" the currently selected file number (selection is made through fd.filenum).
- `fd.ready` R/O (ENUM, BYTE), default= 0- NO (the disk is not mounted and is not ready for use). [read-only] — Informs whether the flash disk is mounted and ready for use.
- `fd.sector` R/O (WORD). [read-only] — Returns the physical sector number corresponding to the current position of the file pointer position (see fd.pointer).
- `fd.totalsize` R/O (WORD). [read-only] — Returns the total number of sectors occupied by the currently existing flash disk.
- `fd.transactioncapacityremaining` R/O (ENUM, BYTE), default= 0 (0 sectors). [read-only] — Returns the number of sectors that can still be changed in the cause of the current disk transaction.
- `fd.transactionstarted` R/O (ENUM, BYTE), default= 0- NO (transaction hasn't been started yet). [read-only] — Reports whether a disk transaction is currently in progress.

Methods / functions:
- `fd.checksum(mode as pl_fd_csum_mode, byref csum as word) as ok_ng` — Calculates and writes into the RAM buffer, or verifies the checksum for the data in the currently selected RAM buffer of the flash memory (selection is made through the…
- `fd.close() as pl_fd_status_codes` — Closes the file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.copyfirmware(numsectors as word)` — Copies the specified number of sectors (starting from the logical sector 0) from the data area into the TiOS/application area of the flash memory, then reboots the…
- `fd.copyfirmwarefromfile() as pl_fd_status_codes` — Copies the data from an opened and currently selected file of the flash disk (selection is made through fd.filenum) into the TiOS/application area of the flash memory,…
- `fd.copyfirmwarelzo(app_present as no_yes, source_sector as word) as byte` — 
- `fd.copyfirmwarelzo(app_present as no_yes)` - Assumes that there is a block of data containing the TiOS firmware, optionally followed by an LZO-compressed application binary stored beginning from the logical sector… **[docs.tibbo.com: 32-битная версия, нужен Monitor V2.00+ (object_fd_copyfirmwarelzo_32)]**
- `fd.copyfirmwarelzo(source_sector as word, byref length as dword, dest_sector as word, byref output_len as dword, displ_x as word, displ_y as word, display_w as word, display_h as byte, reported_cs as word) as byte` — 
- `fd.copyfirmwarelzo(byref length as dword)` - Assumes that there is LZO-compressed firmware/application file of length bytes stored at logical sector 0 of the flash memory. **[docs.tibbo.com: 16-битная версия для отдельных платформ (object_fd_copyfirmwarelzo)]**
- `fd.copyfirmwarefromfilelzo() as pl_fd_status_codes` — Copies the data from an opened and currently selected file of the flash disk (selection is made through fd.filenum) into the TiOS/application area of the flash memory.
- `fd.cutfromtop(numsectors as dword) as pl_fd_status_codes` — Removed a specified number of sectors from the beginning of a file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.create(byref name_attr as string) as pl_fd_status_codes` — Creates a new file with the specified name and attributes.
- `fd.delete(byref name as string) as pl_fd_status_codes` — Deletes a file with the specified file name from the flash disk.
- `fd.find(frompos as dword,byref substr as string,instance as word,dir as forward_back,incr as word,mode as pl_fd_find_modes) as dword` — Finds the Nth instance of data satisfying selected criteria in a file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.flush() as pl_fd_status_codes` — Saves back to the flash memory ("flushes") the changes made to the most recently edited file.
- `fd.format(totalsize as word, maxstoredfiles as byte) as pl_fd_status_codes` — Formats the flash memory to create a flash disk; no transaction journal sectors will be allocated.
- `fd.formatj(totalsize as word, maxstoredfiles as byte, maxjournalsectors as byte) as pl_fd_status_codes` — Formats the flash memory to create a flash disk.
- `fd.getattributes(byref name as string) as string` — Returns the attributes string for a file with the specified file name.
- `fd.getbuffer(offset as word, len as word) as string` — Reads the specified number of bytes from the currently selected RAM buffer of the flash memory (selection is made through the fd.buffernum property).
- `fd.getdata(maxinplen as byte) as string` — Reads a specified number of bytes from the file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.getfreespace() as word` — Returns the total number of free data sectors available on the flash disk.
- `fd.getnextdirmember() as string` — Returns the next filename (if any) found in the disk directory.
- `fd.getnumfiles() as byte` — Returns the total number of files currently stored on the disk.
- `fd.getsector(num as word) as pl_fd_status_codes` — Reads the entire 264 bytes from the specified sector into the currently selected RAM buffer of the flash memory (selection is made through the fd.buffernum property).
- `fd.mount() as pl_fd_status_codes` — Mounts (prepares for use) the flash disk already existing in the flash memory.
- `fd.open(byref name as string) as pl_fd_status_codes` — Opens a file with a specified name "on" a currently selected file number (selection is made through fd.filenum).
- `fd.rename(byref old_name as string, byref new_name as string) as pl_fd_status_codes` — Renames a file specified by its name.
- `fd.resetdirpointer()` — Resets the directory pointer to zero.
- `fd.setattributes(byref name as string, byref attr as string) as pl_fd_status_codes` — Sets the attributes string for a file with the specified file name.
- `fd.setbuffer(byref data as string, offset as word) as word` — Writes a specified number of bytes into the currently selected RAM buffer of the flash memory (selection is made through the fd.buffernum property).
- `fd.setdata(byref data as string) as pl_fd_status_codes` — Writes the data string to a file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.setfilesize(newsize as dword) as pl_fd_status_codes` — Sets (reduces) the file size of a file opened "on" a currently selected file number (selection is made through fd.filenum.
- `fd.setpointer(pos as dword) as pl_fd_status_codes` — Sets the new pointer position for a file opened "on" a currently selected file number (selection is made through fd.filenum).
- `fd.setsector(num as word) as pl_fd_status_codes` — Writes the entire 264 bytes of the specified sector with the data from the currently selected RAM buffer of the flash memory (selection is made through the fd.buffernum…
- `fd.transactioncommit() as pl_fd_status_codes` — Commits a disk transaction that was previously started with the fd.transactionstart method.
- `fd.transactionstart() as pl_fd_status_codes` — Starts a disk transaction.
- `fd.copymonitor(x1 as byte, x2 as byte, x3 as byte, x4 as byte, source_sector as word)` — 
- `fd.copymonitor(x1 as byte, x2 as byte, x3 as byte, x4 as byte)` — 

Enums:
- `pl_fd_status_codes`: PL_FD_STATUS_OK, PL_FD_STATUS_FAIL, PL_FD_STATUS_CHECKSUM_ERR, PL_FD_STATUS_FORMAT_ERR, PL_FD_STATUS_INV_PARAM, PL_FD_STATUS_DUPLICATE_NAME, PL_FD_STATUS_FILE_TABLE_FULL, PL_FD_STATUS_DATA_FULL, PL_FD_STATUS_NOT_READY, PL_FD_STATUS_NOT_FOUND, PL_FD_STATUS_NOT_OPENED, PL_FD_STATUS_ALREADY_OPENED, PL_FD_STATUS_TRANSACTION_ALREADY_STARTED, PL_FD_STATUS_TRANSACTION_NOT_YET_STARTED, PL_FD_STATUS_TRANSACTION_CAPACITY_EXCEEDED, PL_FD_STATUS_TRANSACTIONS_NOT_SUPPORTED, PL_FD_STATUS_FLASH_NOT_DETECTED
- `pl_fd_csum_mode`: PL_FD_CSUM_MODE_VERIFY, PL_FD_CSUM_MODE_CALCULATE
- `pl_fd_find_modes`: PL_FD_FIND_EQUAL, PL_FD_FIND_NOT_EQUAL, PL_FD_FIND_GREATER, PL_FD_FIND_GREATER_EQUAL, PL_FD_FIND_LESSER, PL_FD_FIND_LESSER_EQUAL
- `fd_error_data_codes`: FD_ERROR_NO_ADDITIONAL_ERROR_DATA, FD_ERROR_MOUNT_BOOT_READ_ERROR, FD_ERROR_MOUNT_BOOT_CS_ERROR, FD_ERROR_MOUNT_BOOT_MARKER_INVALID, FD_ERROR_MOUNT_BOOT_DATA_INVALID, FD_ERROR_MOUNT_ENDBOOT_READ_ERROR, FD_ERROR_MOUNT_ENDBOOT_CS_ERROR, FD_ERROR_MOUNT_ENDBOOT_DATA_INVALID, FD_ERROR_MOUNT_FRT_READ_ERROR, FD_ERROR_MOUNT_FRT_CS_ERROR, FD_ERROR_MOUNT_FRT_LOGICAL_NUMBER_OOR, FD_ERROR_MOUNT_FRT_LOGICAL_NUMBER_DUPLICATION, FD_ERROR_MOUNT_FRT_WRITE_ERROR_1, FD_ERROR_MOUNT_FRT_WRITE_ERROR_2, FD_ERROR_MOUNT_FRT_INVALID_ACTIVE_SECTOR_COUNT, FD_ERROR_MOUNT_FRT_EMPTY_MAPPING_DETECTED, FD_ERROR_MOUNT_FAT_READ_ERROR, FD_ERROR_MOUNT_FAT_CS_ERROR, FD_ERROR_MOUNT_FAT_LOGICAL_NUMBER_OOR, FD_ERROR_FAT_LOGICAL_NUMBER_DUPLICATION, FD_ERROR_MOUNT_FAT_WRITE_ERROR_1, FD_ERROR_MOUNT_FAT_WRITE_ERROR_2, FD_ERROR_MOUNT_FAT_INVALID_ACTIVE_SECTOR_COUNT, FD_ERROR_MOUNT_FAT_EMPTY_MAPPING_DETECTED, FD_ERROR_FORMAT_BOOT_WRITE_ERROR, FD_ERROR_FORMAT_ENDBOOT_WRITE_ERROR, FD_ERROR_FORMAT_FRT_WRITE_ERROR, FD_ERROR_FORMAT_FAT_WRITE_ERROR, FD_ERROR_RENAME_COMMON_PORTION_ERROR, FD_ERROR_RENAME_FRT_READ_ERROR, FD_ERROR_RENAME_FRT_CS_ERROR, FD_ERROR_RENAME_FRT_WRITE_ERROR, FD_ERROR_OPEN_COMMON_PORTION_ERROR, FD_ERROR_OPEN_FRT_READ_ERROR, FD_ERROR_OPEN_FRT_CS_ERROR, FD_ERROR_OPEN_FRT_WRITE_ERROR, FD_ERROR_FLUSH_DATASECTOR_WRITE_ERROR, FD_ERROR_SETATTRIBUTES_COMMON_PORTION_ERROR, FD_ERROR_SETATTRIBUTES_FRT_READ_ERROR, FD_ERROR_SETATTRIBUTES_FRT_CS_ERROR, FD_ERROR_SETATTRIBUTES_FRT_WRITE_ERROR, FD_ERROR_DELETE_COMMON_PORTION_ERROR, FD_ERROR_DELETE_FRT_READ_ERROR, FD_ERROR_DELETE_FRT_CS_ERROR, FD_ERROR_DELETE_FRT_WRITE_ERROR, FD_ERROR_DELETE_ENTRY_SECTOR_INVALID, FD_ERROR_DELETE_FAT_WRITE_ERROR_1, FD_ERROR_DELETE_FAT_READ_ERROR, FD_ERROR_DELETE_FAT_CS_ERROR, FD_ERROR_DELETE_INVALID_FAT_CHAIN_1, FD_ERROR_DELETE_INVALID_FAT_CHAIN_2, FD_ERROR_DELETE_FAT_WRITE_ERROR_2, FD_ERROR_CREATE_COMMON_PORTION_ERROR, FD_ERROR_CREATE_FAT_READ_ERROR, FD_ERROR_CREATE_FAT_CS_ERROR, FD_ERROR_CREATE_FAT_WRITE_ERROR, FD_ERROR_CREATE_DATASECTOR_WRITE_ERROR, FD_ERROR_CREATE_FRT_READ_ERROR, FD_ERROR_CREATE_FRT_CS_ERROR, FD_ERROR_CREATE_FRT_WRITE_ERROR, FD_ERROR_GETNUMFILES_FRT_READ_ERROR, FD_ERROR_GETNUMFILES_FRT_CS_ERROR, FD_ERROR_GETNEXTDIRMEMBER_FRT_READ_ERROR, FD_ERROR_GETNEXTDIRMEMBER_FRT_CS_ERROR, FD_ERROR_FREESPACE_FAT_READ_ERROR, FD_ERROR_FREESPACE_FAT_CS_ERROR, FD_ERROR_FREESPACE_FAT_INVALID_DATA, FD_ERROR_FINDFREESECTOR_FAT_INVALID_DATA, FD_ERROR_FINDFREESECTOR_FAT_READ_ERROR, FD_ERROR_FINDFREESECTOR_FAT_CS_ERROR, FD_ERROR_GETDATA_DATASECT_READ_ERROR_1, FD_ERROR_GETDATA_DATASECT_CS_ERROR_1, FD_ERROR_GETDATA_DATASECT_READ_ERROR_2, FD_ERROR_GETDATA_DATASECT_CS_ERROR_2, FD_ERROR_GETDATA_DATASECT_READ_ERROR_3, FD_ERROR_GETDATA_DATASECT_CS_ERROR_3, FD_ERROR_SETDATA_DATASECT_READ_ERROR_1, FD_ERROR_SETDATA_DATASECT_CS_ERROR_1, FD_ERROR_SETDATA_DATASECT_READ_ERROR_2, FD_ERROR_SETDATA_DATASECT_CS_ERROR_2, FD_ERROR_SETDATA_DATASECT_READ_ERROR_3, FD_ERROR_SETDATA_DATASECT_CS_ERROR_3, FD_ERROR_SETDATA_DATASECT_READ_ERROR_4, FD_ERROR_SETDATA_DATASECT_CS_ERROR_4, FD_ERROR_GNSOFC_READ_ERROR_1, FD_ERROR_GNSOFC_CS_ERROR_1, FD_ERROR_GNSOFC_CHAIN_ERROR_1, FD_ERROR_GNSOFC_CHAIN_ERROR_2, FD_ERROR_GNSOFC_READ_ERROR_2, FD_ERROR_GNSOFC_CS_ERROR_2, FD_ERROR_GNSOFC_READ_ERROR_3, FD_ERROR_GNSOFC_CS_ERROR_3, FD_ERROR_GNSOFC_READ_ERROR_4, FD_ERROR_GNSOFC_CS_ERROR_4, FD_ERROR_GNSOFC_WRITE_ERROR, FD_ERROR_SAVE_FAT_SECTOR_WRITE_ERROR_1, FD_ERROR_SAVE_FAT_SECTOR_WRITE_ERROR_2, FD_ERROR_SAVE_FRT_SECTOR_WRITE_ERROR_1, FD_ERROR_SAVE_FRT_SECTOR_WRITE_ERROR_2, FD_ERROR_FIND_DATASECTOR_READ_ERROR_1, FD_ERROR_FIND_DATASECTOR_CS_ERROR_1, FD_ERROR_FIND_DATASECTOR_READ_ERROR_2, FD_ERROR_FIND_DATASECTOR_CS_ERROR_2, FD_ERROR_FIND_DATASECTOR_READ_ERROR_3, FD_ERROR_FIND_DATASECTOR_CS_ERROR_3, FD_ERROR_FIND_GNSOFC_READ_ERROR_1, FD_ERROR_FIND_GNSOFC_CS_ERROR_1, FD_ERROR_FIND_GNSOFC_CHAIN_ERROR, FD_ERROR_MOUNT_JOURNAL_DATA_INVALID, FD_ERROR_MOUNT_JOURNAL_COMMITTING_FAILED, FD_ERROR_MOUNT_JOURNAL_COMMITTING_FAILED2

## wln.tph

**object wln** — The wln. object represents the Wi-Fi interface of your device. This object is responsible for finding and associating with Wi-Fi networks, as well as for creating your own network. It also specifies various parameters related to the Wi-Fi interface (IP address, default gateway IP, netmask, etc.). Th

Properties:
- `wln.associationstate` R/O (ENUM, BYTE), default= 0- PL_WLN_NOT_ASSOCIATED (the Wi-Fi interface is idle). [read-only] — Indicates whether the Wi-Fi interface is idle, associated with another network, or running its own network.
- `wln.buffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — Returns the current capacity (in bytes) of the wln object's TX buffer.
- `wln.clkmap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — Sets/returns the number of the GPIO line acting as the clock (CLK) line of the Wi-Fi module's SPI interface.
- `wln.csmap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — Sets/returns the number of the GPIO line acting as the chip select (CS) line of the Wi-Fi module's SPI interface.
- `wln.dimap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — Sets/returns the number of the GPIO line acting as the data in (DI) line of the Wi-Fi module's SPI interface.
- `wln.domain` (ENUM, BYTE), default= 0 - PL_WLN_DOMAIN_FCC - Sets or returns the domain (area of the world) in which this device is operating. **[docs.tibbo.com: GA1000: FCC - каналы 1–11, EU - 1–13, JAPAN - 1–14 (2,4 ГГц); на WM2000 доступны коды стран 3–76 (PL_WLN_DOMAIN_AG … _VE, список в object_wln_domain и ml_dcb_domains); на WS1102 с TiOS 4.02 свойство устарело - домен задаётся в DCB и требует перезагрузки]**
- `wln.domap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — Sets/returns the number of the GPIO line acting as the data out (DO) line of the Wi-Fi module's SPI interface.
- `wln.enabled` R/O (ENUM, BYTE), default= 0- NO. [read-only] — Indicates whether the Wi-Fi interface is operational.
- `wln.gatewayip` (STRING), default= "0.0.0.0" — Sets/returns the IP address of the default gateway for the Wi-Fi interface of your device.
- `wln.monversion` R/O (STRING). [read-only] — For the WA2000 Wi-Fi/BLE add-on, returns the version string of the module's Monitor/Loader.
- `wln.fwversion` R/O (STRING). [read-only] — For the WA2000 Wi-Fi/BLE add-on, returns the version string of the module's main firmware.
- `wln.band` (ENUM, BYTE), default= 5- WIFI_PHY_11ABGN_MIXED (2.4G and 5G bands, 802.11a/b/g/n) — Specifies what frequency bands (2.4GHz, 5.0GHz, or both) and 802.11 communications standards ("a", "b", "g", "n" or combinations thereof) are enabled.
- `wln.monversion` R/O (STRING). [read-only] — For the WA2000 Wi-Fi/BLE add-on, returns the version string of the module's Monitor/Loader.
- `wln.fwversion` R/O (STRING). [read-only] — For the WA2000 Wi-Fi/BLE add-on, returns the version string of the module's main firmware.
- `wln.band` (ENUM, BYTE), default= 5- WIFI_PHY_11ABGN_MIXED (2.4G and 5G bands, 802.11a/b/g/n) — Specifies what frequency bands (2.4GHz, 5.0GHz, or both) and 802.11 communications standards ("a", "b", "g", "n" or combinations thereof) are enabled.
- `wln.ip` (STRING), default= "1.0.0.1" — Sets/returns the IP address of the Wi-Fi interface of your device.
- `wln.mac` (STRING), default= "0.0.0.0.0.0" — Sets/returns the MAC address of the Wi-Fi interface.
- `wln.netmask` (STRING), default= "0.0.0.0" — Sets/returns the netmask of the Wi-Fi interface of your device.
- `wln.rssi` R/O (BYTE), default= 0. [read-only] — Indicates the strength of the signal being received from the wireless peer.
- `wln.scanfilter` (ENUM, BYTE), default= 0- PL_WLN_SCAN_ALL — Determines what wireless networks are included in the scan results (after scanning with wln.scan or wln.activescan): all networks, only infrastructure networks (access…
- `wln.scanresultbssid` R/O (STRING), default= "". [read-only] — After a successful scan for a particular network (wln.scan or wln.activescan with the SSID specified) this property will contain the BSSID ("MAC address") of this…
- `wln.scanresultbssmode` R/O (ENUM, BYTE), default= 0- PL_WLN_BSS_MODE_INFRASTRUCTURE. [read-only] — After a successful scan for a particular network (wln.scan with the ssid specified) this property will contain the network mode of this network (infrastructure or…
- `wln.scanresultchannel` R/O (BYTE), default= 1 (channel 1). [read-only] — After a successful scan for a particular network (wln.scan with the ssid specified) this property will contain the number of the channel on which this network operates.
- `wln.scanresultrssi` R/O (BYTE), default= 0. [read-only] — After a successful scan for a particular network (wln.scan with the ssid specified) this property will contain the strength of the signal received from this network.
- `wln.scanresultssid` R/O (STRING), default= "". [read-only] — After a scan (wln.scan or wln.activescan) this property will contain a comma-delimited list of discovered networks or the name of a particular network depending on how…
- `wln.scanresultwpainfo` R/O (STRING), default= "". [read-only] — On GA1000, after a successful scan for a particular network (wln.scan or wln.activescan with the SSID specified) this property will contain binary data required for…
- `wln.task` R/O (ENUM, BYTE), default= 0- PL_WLN_TASK_IDLE. [read-only] — Indicates the current wln. task being executed.
- `wln.autodhcp`  — Indicates whether wln.dhcp is enabled at boot: 0 - NO (wln.dhcp is not enabled at boot), 1 - YES (wln.dhcp is enabled at boot) As this is a Device Configuration Block…
- `wln.dhcp` (ENUM, BYTE), default= 1 - YES (TiOS will handle DHCP negotiation and triggers event handlers) - Indicates whether DHCP is enabled. **[docs.tibbo.com: по умолчанию 0 - NO; начальное значение берётся из параметра dhcp в DCB; только WM2000/WS1102; при выключенном wln.autoconnect ставить до wln.boot; с DHCP-библиотекой wln.dhcp и wln.autodhcp должны быть выключены (object_wln_dhcp, ml_dcb)]**
- `wln.autoconnect`  - Indicates whether the device will automatically initialize all connectivity hardware and attempt to associate with a designated Wi-Fi network, maintain the connection,… **[docs.tibbo.com: по умолчанию 0 - NO; только WM2000/WS1102; читается при загрузке, нужен для отладки по Wi-Fi (object_wln_autoconnect)]**
- `wln.autoconnectssid`  — Sets or returns the SSID of the network with which the device will attempt to connect when wln.autoconnect is called.
- `wln.autoconnectpassword`  — Sets or returns the password of the network with which the device will attempt to connect when wln.autoconnect is called.

Methods / functions:
- `wln.activescan(byref ssid as string) as accepted_rejected` — METHOD.
- `wln.associate(byref bssid as string, byref ssid as string, channel as byte, bssmode as pl_wln_bss_modes) as accepted_rejected` — Causes the Wi-Fi interface to attempt association with the specified wireless network.
- `wln.boot(offset as dword) as ok_ng` — Boots up the Wi-Fi add-on module.
- `wln.buffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — Pre-requests a number of buffer pages (1 page= 256 bytes) for the TX buffer of the wln. object.
- `wln.disassociate() as accepted_rejected` — Causes the Wi-Fi interface to commence disassociation from a wireless network.
- `wln.getmoduletype() as pl_wln_module_types` — Detects and returns the Wi-Fi module type, or just returns the module type if it has already been detected earlier.
- `wln.disable()` — Causes the wln. object to be disabled.
- `wln.setupgraderegion(region as pl_wln_upgrade_regions)` — For the WA2000 Wi-Fi/BLE add-on, specifies what region (portion) of the WA2000's firmware is going to be upgraded -- the main firmware or the Monitor/Loader.
- `wln.writeflashpage(byref page as string) as accepted_rejected` — For the WA2000 Wi-Fi/BLE add-on, sends a 128-byte page (block) of firmware data into the module.
- `wln.upgrade(region as pl_wln_upgrade_regions, fwlength_l as word, fwlength_h as word , checksum_l as word, checksum_h as word)` — For the WA2000 Wi-Fi/BLE add-on, initiates copying of the firmware "file" (that was uploaded onto the WA2000 using wln.writeflashpage) from the spare area into the…
- `wln.upgrade(region as pl_wln_upgrade_regions, fwlength as dword, checksum as dword)` - For the WA2000 Wi-Fi/BLE add-on, initiates copying of the firmware "file" (that was uploaded onto the WA2000 using wln.writeflashpage) from the spare area into the… **[docs.tibbo.com: в docs: `wln.upgrade()` без аргументов, область задаётся заранее `wln.setupgraderegion` (object_wln_upgrade)]**
- `wln.waitforupgradecompletion() as ok_ng` — For the WA2000 Wi-Fi/BLE add-on, waits for the firmware copying to complete and returns the result of the copying process.
- `wln.getmoduletype() as pl_wln_module_types` — Detects and returns the Wi-Fi module type, or just returns the module type if it has already been detected earlier.
- `wln.getmoduletype() as pl_wln_module_types` — Detects and returns the Wi-Fi module type, or just returns the module type if it has already been detected earlier.
- `wln.disable()` — Causes the wln. object to be disabled.
- `wln.setupgraderegion(region as pl_wln_upgrade_regions)` — For the WA2000 Wi-Fi/BLE add-on, specifies what region (portion) of the WA2000's firmware is going to be upgraded -- the main firmware or the Monitor/Loader.
- `wln.writeflashpage(byref page as string) as accepted_rejected` — For the WA2000 Wi-Fi/BLE add-on, sends a 128-byte page (block) of firmware data into the module.
- `wln.upgrade(region as pl_wln_upgrade_regions, fwlength as dword, checksum as dword)` — For the WA2000 Wi-Fi/BLE add-on, initiates copying of the firmware "file" (that was uploaded onto the WA2000 using wln.writeflashpage) from the spare area into the…
- `wln.waitforupgradecompletion() as ok_ng` — For the WA2000 Wi-Fi/BLE add-on, waits for the firmware copying to complete and returns the result of the copying process.
- `wln.networkstart(byref ssid as string,channel as byte) as accepted_rejected` — Causes the Wi-Fi interface to commence creating its own network.
- `wln.networkstop() as accepted_rejected` — Causes the Wi-Fi interface to commence the termination of its own network.
- `wln.scan(byref ssid as string) as accepted_rejected` — Causes the Wi-Fi interface to commence either the passive detection of available wireless networks or obtainment of an additional information about a particular network…
- `wln.settxpower(level as byte) as accepted_rejected` - Causes the Wi-Fi interface to commence the adjustment of the TX power to the specified level. **[docs.tibbo.com: на WS1102 с TiOS 4.02 устарел (object_wln_settxpower)]**
- `wln.setwep(byref wepkey as string, wepmode as pl_wln_wep_modes) as accepted_rejected` — Causes the Wi-Fi interface to set new WEP mode and key.
- `wln.setwpa(wpamode as pl_wln_wpa_modes, algorithm as pl_wln_wpa_algorithms, byref wpakey as string, cast as pl_wln_wpa_unicast_multicast) as accepted_rejected` — Causes the Wi-Fi interface to commence setting new WPA mode and key.
- `wln.seteaptls(byref ca_cert as string, byref client_cert as string, byref private_key as string, byref private_key_passwd as string, byref identify as string) as accepted_rejected` — Causes the Wi-Fi interface to commence setting the new data for EAP TLS Enterprise ciphering.
- `wln.seteappeap(byref ca_cert as string, byref identify as string, byref password as string, phase1 as pl_wln_peap_phase1, phase2 as pl_wln_peap_phase2) as accepted_rejected` — Causes the Wi-Fi interface to commence setting the new data for EAP PEAP Enterprise ciphering.
- `wln.seteapttls(byref ca_cert as string, byref identify as string, byref password as string, phase2 as pl_wln_ttls_phase2) as accepted_rejected` — Causes the Wi-Fi interface to commence setting the new data for EAP PEAP Enterprise ciphering.

Events:
- `on_wln_event(wln_event as pl_wln_events)` — Generated when the wln. object detects disassociation from the wireless network, the Wi-Fi interface is disabled by calling wln.disable, or the Wi-Fi hardware is…
- `on_wln_task_complete(completed_task as pl_wln_tasks)` — Generated when the Wi-Fi interface completes executing a given task.

Enums:
- `pl_wln_bss_modes`: PL_WLN_BSS_MODE_INFRASTRUCTURE, PL_WLN_BSS_MODE_ADHOC
- `pl_wln_association_states`: PL_WLN_NOT_ASSOCIATED, PL_WLN_ASSOCIATED, PL_WLN_OWN_NETWORK, PL_WLN_ASSOCIATION_INPROG
- `pl_wln_phy_modes`: WIFI_PHY_11BG_MIXED=0, WIFI_PHY_11B, WIFI_PHY_11A, WIFI_PHY_11ABG_MIXED, WIFI_PHY_11G, WIFI_PHY_11ABGN_MIXED, WIFI_PHY_11N_2_4G, WIFI_PHY_11GN_MIXED, WIFI_PHY_11AN_MIXED, WIFI_PHY_11BGN_MIXED, WIFI_PHY_11AGN_MIXED, WIFI_PHY_11N_5G
- `pl_wln_domains`: PL_WLN_DOMAIN_FCC, PL_WLN_DOMAIN_EU, PL_WLN_DOMAIN_JAPAN
- `pl_wln_module_types`: PL_WLN_MODULE_TYPE_GA1000, PL_WLN_MODULE_TYPE_WA2000, PL_WLN_MODULE_TYPE_WM2000
- `pl_wln_upgrade_regions`: PL_WLN_UPGRADE_REGION_MAIN, PL_WLN_UPGRADE_REGION_MONITOR
- `pl_wln_events`: PL_WLN_EVENT_DISABLED, PL_WLN_EVENT_DISASSOCIATED, PL_WLN_EVENT_ASSOCIATED
- `pl_wln_tasks`: PL_WLN_TASK_IDLE, PL_WLN_TASK_SCAN, PL_WLN_TASK_ASSOCIATE, PL_WLN_TASK_SETTXPOWER, PL_WLN_TASK_SETWEP, PL_WLN_TASK_DISASSOCIATE, PL_WLN_TASK_NETWORK_START, PL_WLN_TASK_NETWORK_STOP, PL_WLN_TASK_SETWPA, PL_WLN_TASK_ACTIVESCAN, PL_WLN_TASK_UPDATERSSI, PL_WLN_TASK_SET_EAP_TLS, PL_WLN_TASK_SET_EAP_PEAP, PL_WLN_TASK_SET_EAP_TTLS
- `pl_wln_scan_filter`: PL_WLN_SCAN_ALL, PL_WLN_ASCAN_INFRASTRUCTURE, PL_WLN_OWN_ADHOC
- `pl_wln_wep_modes`: PL_WLN_WEP_MODE_DISABLED, PL_WLN_WEP_MODE_64, PL_WLN_WEP_MODE_128
- `pl_wln_wpa_modes`: PL_WLN_WPA_DISABLED, PL_WLN_WPA_WPA1_PSK, PL_WLN_WPA_WPA2_PSK
- `pl_wln_wpa_algorithms`: PL_WLN_WPA_ALGORITHM_TKIP, PL_WLN_WPA_ALGORITHM_AES
- `pl_wln_wpa_unicast_multicast`: PL_WLN_WPA_CAST_UNICAST, PL_WLN_WPA_CAST_MULTICAST
- `pl_wln_mfgtx_modes`: PL_WLN_MFGTX_MODE_CONTINUOUS, PL_WLN_MFGTX_MODE_BURST, PL_WLN_MFGTX_MODE_DATATX
- `pl_wln_mfgtx_rates`: PL_WLN_MFGTX_RATE_1M, PL_WLN_MFGTX_RATE_2M, PL_WLN_MFGTX_RATE_5_5M, PL_WLN_MFGTX_RATE_11M, PL_WLN_MFGTX_RATE_22M, PL_WLN_MFGTX_RATE_6M, PL_WLN_MFGTX_RATE_9M, PL_WLN_MFGTX_RATE_12M, PL_WLN_MFGTX_RATE_18M, PL_WLN_MFGTX_RATE_24M, PL_WLN_MFGTX_RATE_36M, PL_WLN_MFGTX_RATE_48M, PL_WLN_MFGTX_RATE_54M, PL_WLN_MFGTX_RATE_72M
- `pl_wln_peap_phase1`: PL_WLN_PEAP_PHASE2_0, PL_WLN_PEAP_PHASE2_1
- `pl_wln_peap_phase2`: PL_WLN_PEAP_PHASE2_MSCHAPV2, PL_WLN_PEAP_PHASE2_TLS, PL_WLN_PEAP_PHASE2_GTC, PL_WLN_PEAP_PHASE2_OTP, PL_WLN_PEAP_PHASE2_MD5
- `pl_wln_ttls_phase2`: PL_WLN_TTLS_PHASE2_EAP_MD5, PL_WLN_TTLS_PHASE2_EAP_GTC, PL_WLN_TTLS_PHASE2_EAP_OTP, PL_WLN_TTLS_PHASE2_EAP_MSCHAPV2, PL_WLN_TTLS_PHASE2_EAP_TLS, PL_WLN_TTLS_PHASE2_MSCHAPV2, PL_WLN_TTLS_PHASE2_MSCHAP, PL_WLN_TTLS_PHASE2_PAP, PL_WLN_TTLS_PHASE2_CHAP

## bt.tph

**object bt** — The bt. object represents the BLE interface of your device. The bt. object is designed to work with the WA2000 add-on Wi-Fi/BLE module. For BT (BLE) radio to work, you must first boot the module using the wln.boot method. This will enable not only the Wi-Fi, but also the BT (BLE) portion of the WA20

Properties:
- `bt.enabled` R/O (ENUM, BYTE), default= 0- NO. [read-only] — Informs whether the BLE interface of the Wi-Fi/BLE add-on module is on.
- `bt.name` (STRING), default= "" — Defines the BLE advertising name.
- `bt.emulation` (ENUM, BYTE), default= 2- PL_WLN_BT_EMULATION_MODE_MICROCHIP — Configures the BLE interface to mimic TI, Nordic, or Microchip BLE devices.
- `bt.rxbuffsize` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the current capacity, in bytes, of the BLE's RX buffer.
- `bt.txbuffsize` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the current capacity, in bytes, of the BLE's TX buffer.
- `bt.rxlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the total number of bytes currently waiting in the RX buffer of the BLE interface.
- `bt.txlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the total number of committed bytes in the TX buffer of the BLE interface.
- `bt.txfree` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the amount of free space, in bytes, in the TX buffer of the BLE interface, not taking into the account uncommitted data.
- `bt.newtxlen` R/O (WORD | DWORD), default=0 (0 bytes). [read-only] — Returns the total number of uncommitted bytes in the TX buffer of the BLE interface.
- `bt.advertise` (ENUM, BYTE), default= 0- NO — Setting this property to 1 -YES will start the advertising service on the BLE interface.
- `bt.connected` R/O (ENUM, BYTE), default= 0- NO. [read-only] — Indicates whether the BLE interface is engaged in a connection.
- `bt.mac` (STRING), default= "0.0.0.0.0.0" - Sets and returns the MAC address of the BLE interface. **[docs.tibbo.com: до wln.boot возвращает "0.0.0.0.0.0", после - MAC модуля WA2000; задавать новый MAC только до wln.boot. На WM2000/WS1102 bt.mac только для чтения (object_bt_mac, wm2000_platform_objects)]**
- `bt.mac` R/O (STRING), default= mac address of the bluetooth module. [read-only] — Returns the MAC address of the BLE interface.
- `bt.flowcontrol` (ENUM, BYTE), default= 0- DISABLED — Sets/returns flow control mode for bluetooth object.

Methods / functions:
- `bt.enable()` — Instructs the WA2000 Wi-Fi/BLE add-on module to turns the BLE radio on.
- `bt.disable()` — Instructs the WA2000 Wi-Fi/BLE add-on module to turn the BLE radio off.
- `bt.rxbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — Pre-requests the "numpages" number of buffer pages (1 page is 256 bytes) for the RX buffer of the BLE interface.
- `bt.txbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — Pre-requests the "numpages" number of buffer pages (1 page is 256 bytes) for the TX buffer of the BLE interface.
- `bt.rxclear` — Clears the RX buffer of the BLE interface.
- `bt.txclear` — Clears the TX buffer of the BLE interface.
- `bt.getdata(maxinplen as word) as string` — Returns the string containing the data extracted from the RX buffer of the BLE interface.
- `bt.peekdata(maxinplen as word) as string` — Returns the string containing the "preview" of data from the RX buffer of the BLE interface.
- `bt.setdata(byref txdata as string)` — Stores the data passed in the txdata argument into the TX buffer of the BLE inteface.
- `bt.send()` — Commits (allows sending out) the data that was previously saved into the TX buffer of the BLE interface using the bt.setdata method.
- `bt.notifysent(threshold as word)` — Invoking this method will cause the on_bt_data_sent event to be generated when the amount of committed data in the TX buffer of the BLE interface drops to or below the…
- `bt.disconnect() as accepted_rejected` — Causes the BLE interface to terminate the active connection.

Events:
- `on_bt_event(bt_event as pl_bt_events)` — Generated when the following BLE events occur: 0- _CONNECTED -- The BLE interface has accepted an incoming connection.
- `on_bt_data_arrival()` — Generated as soon as the BLE interface receives data into the RX buffer.
- `on_bt_data_sent()` — Generated after the total amount of committed data in the TX buffer of the BLE interface drops to or below the threshold that was preset through the bt.notifysent method.
- `on_bt_overrun()` — Generated when the RX buffer of the BLE interface overflows.

Enums:
- `pl_wln_bt_emulation_modes`: PL_WLN_BT_EMULATION_MODE_TI, PL_WLN_BT_EMULATION_MODE_NORDIC, PL_WLN_BT_EMULATION_MODE_MICROCHIP
- `pl_bt_events`: PL_BT_EVENT_CONNECTED, PL_BT_EVENT_DISCONNECTED, PL_BT_EVENT_ENABLED, PL_BT_EVENT_DISABLED
- `pl_bt_flowcontrol`: PL_BT_FC_DISABLED, PL_BT_FC_ENABLED

## dhcp.tph


Events:
- `on_sys_dhcp_ok(renew as no_yes, interface as pl_sock_interfaces, ip as string(16), gateway_ip as string(16), netmask as string(16), lease_time as dword)` - Informs of the successful procurement of configuration parameters from the DHCP server. **[docs.tibbo.com: имена параметров: dhcp_obtained_ip, dhcp_obtained_gateway, dhcp_obtained_netmask, dhcp_obtained_lease_time; renew=YES - продление аренды, IP мог смениться]**
- `on_sys_dhcp_failure(interface as pl_sock_interfaces)` — Informs of the failure to procure configuration parameters from the DHCP server.

## tls.tph

Properties:
- `sock.tlsrxlen` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through sock.num), returns the total number of bytes currently waiting in the TLS RX buffer to be extracted and…
- `sock.tlscurrentnum` R/O (BYTE), default= 255 (not in use). [read-only] — Indicates which socket, if any, is using TLS encryption.

Methods / functions:
- `sock.tlsinit(offset as dword) as pl_tls_result` — For the currently selected socket (selection is made through sock.num), initializes all resources required for establishing a TLS connection.
- `sock.tlshandshake(byref server_name as string) as pl_tls_result` — For the currently selected socket (selection is made through sock.num), initiates the TLS handshake process to upgrade the socket to an encrypted connection.
- `sock.tlsdeinit() as accepted_rejected` — For the currently selected socket (selection is made through sock.num), de-initializes the TLS encryption.
- `sock.tlssetdata(byref txdata as string) as word` — For the currently selected socket (selection is made through sock.num), adds the data passed in the txdata argument to the contents of the TLS TX buffer.
- `sock.tlsgetdata(maxinplen as word) as string` — For the currently selected socket (selection is made through sock.num), returns the string that contains the decrypted data extracted from the TLS RX buffer.
- `sock.tlsbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — Pre-requests the number (numpages) of buffer pages (1 page is 256 bytes) for the buffer used for TLS operations.
- `sock.tlspeekdata(maxinplen as word) as string` — For the currently selected socket (selection is made through sock.num), returns a string that contains a "preview" of the data in the TLS RX buffer.
- `sock.tlsinitfromarray(byref cert,len as word) as pl_tls_result` — For the currently selected socket (selection is made through sock.num), initializes all resources required for establishing a TLS connection.

Enums:
- `pl_tls_result`: PL_TLS_SUCCESS, PL_TLS_REJECTED, PL_TLS_ERROR_IN_USE, PL_TLS_ERROR_CERT, PL_TLS_ERROR_NO_BUFF, PL_TLS_ERROR_INTERNAL

## ppp.tph

**object ppp** — The ppp object represents a ppp interface of your device (i.e. for accessing TCP/IP networks thru landline or GPRS modems). This object only specifies various parameters related to the ppp interface (such as the IP address) and is not responsible for sending/transmitting network data. The latter is 

Properties:
- `ppp.enabled` (ENUM, BYTE), default= 0- NO (not enabled) — Enables/disables PPP interface on the serial port specified by the ppp.portnum property.
- `ppp.portnum` (BYTE), default= 0 (serial port #0 selected) — Sets/returns the number of the serial port that will be used by the ppp. object.
- `ppp.buffsize` R/O (WORD | DWORD), default= 0 (0 bytes). [read-only] — Returns the current capacity (in bytes) of the ppp. object's buffer.
- `ppp.ip` (STRING), default= "1.0.0.1" — Sets/returns the IP address of the PPP interface of your device.

Methods / functions:
- `ppp.buffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — Pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the buffer of the ppp object.

## pppoe.tph

**object pppoe** — The pppoe object represents the PPPoE interface of your device. This object only specifies the interface itself and is not responsible for sending/transmitting network data. The latter is the job of the sock object. The object does not perform PPPoE login and configuration either -- use PPPOE librar

Properties:
- `pppoe.acmac` (STRING), default= "0.0.0.0.0.0" - Sets/returns the MAC address of the ADSL modem (a.k.a. **[docs.tibbo.com: DEPRECATED с TiOS V4]**
- `pppoe.ip` (STRING), default= "0.0.0.0" - Sets/returns the IP address of the PPPoE interface of your device. **[docs.tibbo.com: DEPRECATED с TiOS V4]**
- `pppoe.sessionid` (STRING), default= 0 - Sets/returns the ID of the current PPPoE session. **[docs.tibbo.com: DEPRECATED с TiOS V4]**

## beep.tph

**object beep** — The beep. object allows you to "play" sound patters using a buzzer attached to the CO pin of your device.

Properties:
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency (frequency of the square wave output on the CO line).
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency (frequency of the square wave output on the CO line).
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency (frequency of the square wave output on the CO line).
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency (frequency of the square wave output on the CO line).
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency (frequency of the square wave output on the CO line).
- `beep.divider` (WORD), default= 1 — Defines the buzzer frequency.
- `beep.frequency` (WORD), default= 1000 — Defines the buzzer frequency (frequency of the square wave output on the line).

Methods / functions:
- `beep.play(byref pattern as string, patint as pl_beep_int)` — Loads a new buzzer pattern to play.

Events:
- `on_beep` — Generated when a pattern finishes playing.

Enums:
- `pl_beep_int`: PL_BEEP_NOINT, PL_BEEP_CANINT

## pat.tph

> **Шкала из 5 синих LED на TiOS-платах (TPP2/TPP3, в т.ч. G2/G3):** `pat.playlb` есть только на LTPP3(G2) (Linux, раздел в конце
> файла). На TiOS шкалу ведёт приложение: на TPP - сдвиговый регистр на линиях `PL_IO_NUM_46/47/48` (reset/clock/data, данные
> активным LOW), на DS110x - линии `PL_IO_NUM_19_SB1…23_SB5`. Готовый драйвер `signal_strength_set()` есть в коде, который
> генерирует AppBlocks (скилл appblocks, generated-code.md).

**object pat** — The pat. object allows you to "play" blink patters on up to five LED pairs or channels, each pair typically consisting of red and green LEDs. Patterns only play when your application is executing and pause when you application is not running. Channel 0 is the primary channel of your system. It utili

**object pat** — The pat. object allows you to "play" blink patters on up to five LED pairs or channels, each pair typically consisting of red and green LEDs. Patterns only play when your application is executing and pause when you application is not running. Channel 0 is the primary channel of your system. It utili

**object pat** — The pat. object allows you to "play" blink patters on up to five LED pairs or channels, each pair typically consisting of red and green LEDs. Patterns only play when your application is executing and pause when you application is not running. Channel 0 is the primary channel of your system. It utili

Properties:
- `pat.channel` (BYTE), default= 0 (channel 0) — Selects/returns the pattern channel to work with.
- `pat.greenmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…
- `pat.greenmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…
- `pat.greenmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…
- `pat.redmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…
- `pat.redmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…
- `pat.redmap` (ENUM, BYTE), default=: channel 0: (-1), R/0; channels 1-4: PL_IO_NULL — For the currently selected pattern channel (selection is made through the pat.channel property), sets/returns the number of the I/O line that will act as the control…

Methods / functions:
- `pat.play(byref pattern as string, patint as pl_pat_int)` — For the currently selected pattern channel (selection is made through the pat.channel property), loads a new LED pattern to play.

Events:
- `on_pat` — Generated when an LED pattern finishes "playing".

Enums:
- `pl_pat_int`: PL_PAT_NOINT, PL_PAT_CANINT

## button.tph

**object button** — All programmable boards, programmable serial controllers, and Tibbo Project System (TPS) devices offered by Tibbo feature a button referred to as the "setup" or "MD" button ("MD" stands for "mode"). All programmable Tibbo modules have a line for connecting this button externally. When a programmable

Properties:
- `button.pressed` R/O (BYTE). [read-only] — Returns the current button state.
- `button.time` R/O (BYTE). [read-only] — Returns the time (in 0.5 second intervals) elapsed since the button was last pressed or released (whichever happened more recently).

Events:
- `on_button_pressed` — Generated when the MD button on your device is pressed (MD line goes LOW).
- `on_button_released` — Generated when the MD button on your device is released (MD line goes HIGH).

## kp.tph

**object kp** — Depending on the kp.mode property, the keypad object works with a "matrix" keypad of up to 64 keys (8 scan lines by 8 return lines) or "binary output" keypad of up to 255 keys that sends key codes through up to 8 return lines.

Properties:
- `kp.mode` (ENUM, BYTE), default= 0- PL_KP_MODE_MATRIX (matrix type) — Specifies the type of the keypad attached to your TiOS device.
- `kp.idlecode` (BYTE), default= 0 — Specifies the code that is expected to be present on the return lines of a binary keypad when no key is pressed.
- `kp.autodisablecodes` (STRING), default= "" — Defines what key event + key code combinations disable the keypad (set kp.enabled= 0- NO).
- `kp.enabled` (ENUM, BYTE), default= 0- NO (disabled) — Enables or disables the keypad.
- `kp.longpressdelay` (BYTE), default= 100 (1 sec) — Defines (in 10ms increments) the amount of time a key will have to remain pressed for the key state to transition from _PRESSED into _LONGPRESSED.
- `kp.longreleasedelay` (BYTE), default= 100 (1 sec) — Defines (in 10ms increments) the amount of time a key will have to remain released for the key state to transition from _RELEASED into _LONGRELEASED state.
- `kp.pressdelay` (BYTE), default= 3 (30 ms) — Defines (in 10ms increments) the amount of time a key will have to remain pressed for the key state to transition from _RELEASED into _PRESSED.
- `kp.releasedelay` (BYTE), default= 3 (30 ms) — Defines (in 10ms increments) the amount of time a key will have to remain released for the key state to transition from _PRESSED or _LONGPRESSED into _RELEASED.
- `kp.repeatdelay` (BYTE), default= 50 (0.5 sec.) - Defines (in 10ms increments) the time period at which the on_kp event with 4- PL_KP_EVENT_REPEATPRESSED event code will be generated once the key reaches the… **[docs.tibbo.com: default = 3 (30 мс), 0–254; 0 - автоповтора нет; менять только при kp.enabled = NO (object_kp_repeatdelay)]**
- `kp.lockupdelay` (WORD), default= 1000 (10sec) — Defines (in 10ms increments) the amount of time any key will have to stay pressed for the keypad to enter the "lockup" state.
- `kp.returnlinesmapping` (STRING), default= "" — Defines the list of up to 8 I/O lines that will serve as return lines of the keypad.
- `kp.scanlinesmapping` (STRING), default= "" — Defines the list of up to 8 I/O lines that will serve as scan lines of the matrix keypad.
- `kp.genkpevent` (ENUM, BYTE), default= 1- YES (event will be generated) — If kp.genkpevent= 1- YES, then you will be receiving keypad events through the on_kp event.
- `kp.overflow` R/O (ENUM, BYTE), default= 0- NO (no overflow). [read-only] — Informs whether the keypad is currently in the overflow state.

Methods / functions:
- `kp.getkey(byref key_event as pl_kp_event_codes, byref key_code as byte) as ok_ng` — When kp.genkpevent= 0- NO, calling this method attempts to fetch one keypad event from the keypad event FIFO.
- `kp.clearbuffer()` — Clears the keypad event FIFO.
- `kp.setlabel(key_code as byte, byref label as string)` — Use this method to set a label on a keypad button in TiOS Simulator.

Events:
- `on_kp(key_event as pl_kp_event_codes, key_code as byte)` — When kp.genkpevent= 1- YES, this event is generated whenever a key transitions into a new state.
- `on_kp_overflow()` — Indicates that the keypad event FIFO has overflown and some key events may have been lost.

Enums:
- `pl_kp_modes`: PL_KP_MODE_MATRIX, PL_KP_MODE_BINARY
- `pl_kp_event_codes`: PL_KP_EVENT_LONGRELEASED, PL_KP_EVENT_RELEASED, PL_KP_EVENT_PRESSED, PL_KP_EVENT_LONGPRESSED, PL_KP_EVENT_REPEATPRESSED, PL_KP_EVENT_LOCKEDUP

## lcd.tph

**object lcd** — The lcd object is for operating a display panel.

Properties:
- `lcd.backcolor` (WORD), default= 0 — Specifies current background color.
- `lcd.bitsperpixel` R/O (BYTE). [read-only] — Returns the number of bits available for each pixel of the currently selected controller/panel.
- `lcd.bluebits` R/O (WORD). [read-only] — A 16-bit value packing two 8-bit parameters: number of "blue" bits per pixel (high byte) and the position of the least significant blue bit within the color word (low…
- `lcd.enabled` (ENUM, BYTE), default= 0- NO (disabled) — Specifies whether the display panel is enabled.
- `lcd.error` R/O (ENUM, BYTE), default= 0- NO (no error detected). [read-only] — Indicates whether controller/panel I/O error has been detected.
- `lcd.fontheight` R/O (BYTE), default= 0. [read-only] — Returns the maximum height, in pixels, of characters in the currently selected font.
- `lcd.fontpixelpacking` R/O (ENUM, BYTE), default= 0- PL_VERTICAL (vertically adjacent pixels are packed into each byte). [read-only] — Indicates how pixels are packed into bytes in a currently selected font: 0- PL_VERTICAL when vertically adjacent pixels are packed into each byte, 1- PL_HORIZONTAL when…
- `lcd.forecolor` (WORD), default= 65535 (&hFFFF) — Specifies current "pen" (drawing) color.
- `lcd.greenbits` R/O (WORD). [read-only] — A 16-bit value packing two 8-bit parameters: number of "green" bits per pixel (high byte) and the position of the least significant green bit within the color word (low…
- `lcd.height` (WORD), default= 0 — Sets the vertical resolution of the display panel in pixels.
- `lcd.inverted` (ENUM, BYTE), default= 0- NO (not inverted, higher memory value = higher pixel brightness) — Specifies whether the image on the display panel has to be inverted: 0- NO (normal image), 1- YES (image must be inverted).
- `lcd.iomapping` (STRING), default= "" — Defines the list of I/O lines to interface with the currently selected controller/panel.
- `lcd.linewidth` (BYTE), default= 1 (1 pixel) — Specifies current "pen" width in pixels.
- `lcd.lockcount` R/O (BYTE), default= 0 (display unlocked). [read-only] — Indicates the current nesting level of the display lock.
- `lcd.paneltype` (ENUM, BYTE). [read-only] — Returns the type of the currently selected controller/panel: 0- PL_LCD_PANELTYPE_GRAYSCALE for a monochrome or grayscale panel/controller, 1- PL_LCD_PANELTYPE_COLOR for…
- `lcd.pixelpacking` R/O (ENUM, BYTE), default= 0- PL_VERTICAL (vertically adjacent pixels are packed into each byte). [read-only] — Indicates how pixels are packed into controller memory for the currently selected controller/panel: 0- PL_VERTICAL when vertically adjacent pixels are packed into each…
- `lcd.redbits` R/O (WORD). [read-only] — A 16-bit value packing two 8-bit parameters: number of "red" bits per pixel (high byte) and the position of the least significant red bit within the color word (low…
- `lcd.rotated` (ENUM, BYTE), default= 0- NO (not rotated) — Specifies whether the image on the display panel is to be rotated 180 degrees: 0- NO (not rotated), or 1- YES (rotated 180 degrees).
- `lcd.textalignment` (ENUM, BYTE), default= 0- PL_LCD_TEXT_ALIGNMENT_TOP_LEFT (top, left) — Specifies the alignment for text output produced by the lcd.printaligned method.
- `lcd.texthorizontalspacing` (BYTE), default= 1 (1 pixel) — Specifies the gap, in pixels, between characters of text output produced by the lcd.print and lcd.printaligned methods.
- `lcd.textorientation` (ENUM, BYTE), default= PL_LCD_TEXT_ORIENTATION_0 (at 0 degrees) — Specifies the print angle for text output produced by the lcd.print and lcd.printaligned methods.
- `lcd.textverticalspacing` (BYTE), default= 1 (1 pixel) — Specifies the gap, in pixels, between the lines of text output produced by the lcd.printaligned method.
- `lcd.width` (WORD), default= 0 — Sets the horizontal resolution of the display panel in pixels.
- `lcd.datawidth`  — Indicates the number of data lines between lcd controller and the LCD panel.

Methods / functions:
- `lcd.bmp(offset as dword, x as word, y as word, x_offset as word, y_offset as word, maxwidth as word, maxheight as word) as ok_ng` — Displays a portion of or full image stored in a BMP file.
- `lcd.bmpfromfile(ignored_parameter as dword, x as word, y as word, x_offset as word, y_offset as word, maxwidth as word, maxheight as word) as ok_ng` — 
- `lcd.fill(x as word,y as word, width as word, height as word)` — Paints the area with the "pen" color ( lcd.forecolor). x -- X coordinate of the top-left point of the area to be painted.
- `lcd.filledrectangle(x1 as word,y1 as word,x2 as word,y2 as word)` — Draws a filled rectangle. x1 -- X coordinate of the first point.
- `lcd.getprintwidth(byref str as string) as word` — Returns the width, in pixels, of the text output that will be produced if the str line is actually printed with the lcd.print method.
- `lcd.horline(x1 as word,x2 as word,y as word)` — Draws a horizontal line. x1 -- X coordinate of the first point.
- `lcd.line(x1 as word,y1 as word, x2 as word, y2 as word)` — Draws a line. x1 -- X coordinate of the first point.
- `lcd.lock()` — Freezes display output (on controllers/panels that support this feature).
- `lcd.print(byref str as string,x as word,y as word) as word` — Prints a str line of text at x, y coordinates.
- `lcd.printaligned(byref str as string,x as word,y as word,width as word,height as word) as byte` — Print texts, on several lines if necessary, within a specified rectangular area.
- `lcd.rectangle(x1 as word,y1 as word,x2 as word,y2 as word)` — Draws an unfilled rectangle. x1 -- X coordinate of the first point.
- `lcd.setfont(offset as dword) as ok_ng` — Selects a font to use for printing text.
- `lcd.setpixel(dt as word,x as word,y as word)` — Directly writes pixel data dt for a single pixel at x, y coordinates.
- `lcd.getpixel(x as word,y as word) as word` — UNDOCUMENTED
- `lcd.unlock()` — Unfreezes display output (on controllers/panels that support this feature).
- `lcd.verline(x as word,y1 as word,y2 as word)` — Draws a vertical line. x -- X coordinates of the first and second points.

Enums:
- `pl_lcd_paneltype`: PL_LCD_PANELTYPE_GRAYSCALE, PL_LCD_PANELTYPE_COLOR
- `pl_lcd_text_alignment`: PL_LCD_TEXT_ALIGNMENT_TOP_LEFT, PL_LCD_TEXT_ALIGNMENT_TOP_CENTER, PL_LCD_TEXT_ALIGNMENT_TOP_RIGHT, PL_LCD_TEXT_ALIGNMENT_MIDDLE_LEFT, PL_LCD_TEXT_ALIGNMENT_MIDDLE_CENTER, PL_LCD_TEXT_ALIGNMENT_MIDDLE_RIGHT, PL_LCD_TEXT_ALIGNMENT_BOTTOM_LEFT, PL_LCD_TEXT_ALIGNMENT_BOTTOM_CENTER, PL_LCD_TEXT_ALIGNMENT_BOTTOM_RIGHT
- `pl_lcd_text_orientation`: PL_LCD_TEXT_ORIENTATION_0, PL_LCD_TEXT_ORIENTATION_90, PL_LCD_TEXT_ORIENTATION_180, PL_LCD_TEXT_ORIENTATION_270
- `pl_lcd_data_width`: PL_LCD_DATA_WIDTH_18, PL_LCD_DATA_WIDTH_24

## ssi.tph

**object ssi** — The ssi. object implements up to four serial synchronous interfaces (SSI) on the general-purpose I/O lines of your device. Examples of such interfaces are SPI, I2C, clock/data, and numerous variations on these interfaces.

Properties:
- `ssi.baudrate` (BYTE), default= 1 (the fastest clock rate possible) - For the currently selected SSI channel (see ssi.channel) sets the clock rate on the CLK line (1-255). **[docs.tibbo.com: свойство чтения/записи (в прежней версии справочника было ошибочно помечено R/O); менять при ssi.enabled = NO]**
- `ssi.channel` (BYTE), default= 0 (channel #0 selected) — Sets/returns the number of the currently selected SSI channel (channels are enumerated from 0).
- `ssi.clkmap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — For the currently selected SSI channel (see ssi.channel) sets/returns the number of the general-purpose I/O line to serve as the clock (CLK) line of this channel.
- `ssi.dimap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — For the currently selected SSI channel (see ssi.channel) sets/returns the number of the general-purpose I/O line to serve as the data in (DI) line of this channel.
- `ssi.direction` (BYTE), default= 0- PL_SSI_DIRECTION_RIGHT - For the currently selected SSI channel (see ssi.channel) sets/returns the direction of data input and output: PL_SSI_DIRECTION_RIGHT means "least significant bit first",… **[docs.tibbo.com: свойство чтения/записи (в прежней версии справочника было ошибочно помечено R/O); менять при ssi.enabled = NO]**
- `ssi.domap` (ENUM, BYTE), default= PL_IO_NULL (NULL line) — For the currently selected SSI channel (see ssi.channel) sets/returns the number of the general-purpose I/O line to serve as the data out (DO) line of this channel.
- `ssi.enabled` (ENUM, BYTE), default= 0- NO (disabled) — Enables/disables the currently selected SSI channel (see ssi.channel).
- `ssi.mode` (BYTE), default= 0- PL_SSI_MODE_0 - For the currently selected SSI channel (see ssi.channel) sets/returns the clock mode. **[docs.tibbo.com: свойство чтения/записи (в прежней версии справочника было ошибочно помечено R/O); менять при ssi.enabled = NO]**
- `ssi.zmode` (BYTE), default= 0- PL_SSI_ZMODE_ALWAYS_ENABLED - For the currently selected SSI channel (see ssi.channel) sets/returns the mode of the data out (DO) line: PL_SSI_ZMODE_ALWAYS_ENABLED-- the DO line toggles normally by… **[docs.tibbo.com: свойство чтения/записи (в прежней версии справочника было ошибочно помечено R/O); менять при ssi.enabled = NO]**

Methods / functions:
- `ssi.str(byref txdata as string, ack_bit as pl_ssi_ack_modes) as string` - For the currently selected SSI channel (see ssi.channel) outputs a string of byte data to the slave device and simultaneously inputs the same amount of data from the… **[docs.tibbo.com: в docs: `ssi.str(byref txdata as string, ack_bit as no_yes) as string` - NO: 8-битные слова, YES: 9 бит с битом подтверждения; вызывать только при ssi.enabled = YES]**
- `ssi.value(txdata as word, len as byte) as word` — For the currently selected SSI channel (see ssi.channel) outputs a data word of up to 16 bits and simultaneously inputs a data word of the same length.

Enums:
- `pl_ssi_baud`: PL_SSI_BAUD_100kHz
- `pl_ssi_baud`: PL_SSI_BAUD_1MHz, PL_SSI_BAUD_900kHz, PL_SSI_BAUD_800kHz, PL_SSI_BAUD_400kHz, PL_SSI_BAUD_300kHz, PL_SSI_BAUD_200kHz, PL_SSI_BAUD_100kHz, PL_SSI_BAUD_90kHz, PL_SSI_BAUD_80kHz, PL_SSI_BAUD_70kHz, PL_SSI_BAUD_60kHz, PL_SSI_BAUD_50kHz
- `pl_ssi_baud`: PL_SSI_BAUD_1MHz, PL_SSI_BAUD_900kHz, PL_SSI_BAUD_800kHz, PL_SSI_BAUD_400kHz, PL_SSI_BAUD_300kHz, PL_SSI_BAUD_200kHz, PL_SSI_BAUD_100kHz, PL_SSI_BAUD_90kHz, PL_SSI_BAUD_80kHz, PL_SSI_BAUD_70kHz, PL_SSI_BAUD_60kHz, PL_SSI_BAUD_50kHz
- `pl_ssi_direction_options`: PL_SSI_DIRECTION_RIGHT, PL_SSI_DIRECTION_LEFT
- `pl_ssi_modes`: PL_SSI_MODE_0, PL_SSI_MODE_1, PL_SSI_MODE_2, PL_SSI_MODE_3
- `pl_ssi_ack_modes`: PL_SSI_ACK_OFF, PL_SSI_ACK_RX, PL_SSI_ACK_TX_ALL, PL_SSI_ACK_ALL_BUT_LAST
- `pl_ssi_zmodes`: PL_SSI_ZMODE_ALWAYS_ENABLED, PL_SSI_ZMODE_ENABLED_ON_ZERO

## i2c.tph

**object i2c** — 

Properties:
- `i2c.num` (BYTE). default= 0 - Sets/returns the number of the currently selected I2C channel (channels are enumerated from 0). **[docs.tibbo.com: в docs свойство называется `i2c.channel` (object_i2c_channel); остальные свойства ссылаются на i2c.channel - сверяй с .tph своей платформы]**
- `i2c.sdamap` (ENUM, BYTE), default= 0 — Sets/returns the number of the I/O line that will act as the SDA line of the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.sclmap` (ENUM, BYTE), default= 0 — Sets/returns the number of the I/O line that will act as the SCL line of the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.enabled` (ENUM, BYTE). default= 0- NO — Enables/disables the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.state` (ENUM, BYTE). default= 0- I2C_IDLE. [read-only] — Returns the state (enum i2c_state) of the currently selected I2C channel (selection is made through i2c.channel).

Methods / functions:
- `i2c.start` — Sets the START condition on the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.stop` — Sets the STOP condition on the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.write(b as byte) as i2c_ack_nack` — Writes one byte to the currently selected I2C channel (selection is made through i2c.channel).
- `i2c.read(ack_bit as i2c_ack_nack) as byte` — Reads one byte from the currently selected I2C channel (selection is made through i2c.channel).

Enums:
- `i2c_ack_nack`: ACK=0, NACK=1
- `i2c_state`: I2C_IDLE=0, I2C_STARTED=1, I2C_STRETCHING_ERROR=2, I2C_ARBITRATION_ERROR=3

## adc.tph

**object adc** — Adc. object provides access to the analog-to-digital converter (ADC).

Properties:
- `adc.num` (ENUM, BYTE), default= 0 — Sets/returns the number of the currently selected ADC channel.
- `adc.enabled` (ENUM, BYTE). default= 0- NO — For the currently selected ADC channel (selection is made through the adc.num property), defines whether this ADC channel is enabled or disabled.

Methods / functions:
- `adc.getdata() as word` — Performs a single conversion and returns the current voltage on the selected ADC channel (selection is made through the adc.num property).

## pwm.tph

**object pwm** — PWM. object provides access to the Pulse-width modulation (PWM) capabilities of lines.

Properties:
- `pwm.num` (ENUM, BYTE), default= 0 — Sets or returns the number of the currently selected PWM channel.
- `pwm.frequency` (REAL), default= 1000 — For the currently selected PWM channel (selection is made through pwm.num), indicates the frequency of modulation.
- `pwm.dutycycle` (REAL), default= 0 — For the currently selected PWM channel (selection is made through pwm.num), indicates the duty cycle.
- `pwm.enabled` (ENUM, BYTE). default= 0 - NO — For the currently selected PWM channel (selection is made through pwm.num), indicates whether it is enabled or disabled: 0 - NO (the PWM channel is disabled), 1 - YES…

Methods / functions:
- `pwm.update()` — For the currently selected PWM channel (selection is made through pwm.num), updates the frequency and duty cycle.
- `pwm.updateall()` — Updates the frequency and duty cycle for all enabled PWM channels.

## rtc.tph

**object rtc** — Facilitates access to the real-time counter (RTC) of the device. The RTC is an independent hardware counter that has its own power input. When the backup battery is installed, the RTC will continue running even when the rest of the device is powered off. The RTC keeps track of elapsed days, minutes,

Properties:
- `rtc.running` R/O (ENUM, BYTE). [read-only] — Returns current RTC state: 0- NO (RTC not running), 1- YES (RTC is running).
- `rtc.clock512`  — 
- `rtc.calibration`  — 

Methods / functions:
- `rtc.getdata(byref daycount as word, byref mincount as word, byref seconds as byte)` — Returns current RTC data as the number of elapsed days (daycount), minutes (mincount) and seconds.
- `rtc.setdata(daycount as word, mincount as word, seconds as byte)` — Presets the RTC with a number of elapsed days (daycount), minutes (mincount), and seconds.

## tpram.tph

**object tpram** — 

Properties:
- `tpram.triggerpolarity`  — 
- `tpram.tamperdetection`  — 
- `tpram.timestamping`  — 
- `tpram.capacity`  [read-only] — 

Methods / functions:
- `tpram.getdata(startaddr as word, len as byte) as string` — 
- `tpram.gettimestamp(byref daycount as word, byref mincount as word, byref seconds as byte, byref overflow as no_yes) as no_yes` — 

## lsock.tph

**object lsock** — This is the object that manages sockets on Linux. The number of available sockets can be obtained through the lsock.numofsock read-only property. Selection of a particular socket to work with is done through the lsock.num property. Most other properties and methods refer to the currently selected so

Properties:
- `lsock.num` (BYTE), default= 0 (socket #0 selected) — Sets/returns the number of the currently selected socket (sockets are enumerated from 0).
- `lsock.numofsock` R/O (BYTE). [read-only] — Returns total number of sockets available.
- `lsock.state` R/O (ENUM, BYTE), default= 0-PL_LSST_CLOSED (connection is closed). [read-only] — For the currently selected socket (selection is made through lsock.num) returns the current socket state (as opposed to on_lsock_event that returns the state at the…
- `lsock.rxbuffsize` R/O (DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through lsock.num) returns current RX buffer capacity in bytes.
- `lsock.txbuffsize` R/O (DWORD), default= 0 (0 bytes). [read-only] — For the currently selected socket (selection is made through lsock.num) returns current TX buffer capacity in bytes.
- `lsock.protocol` (ENUM, BYTE), default= 0- PL_LSOCK_PROTOCOL_UDP (UDP transport protocol for the socket) — For the currently selected socket (selection is made through lsock.num ) selects the transport protocol: 0- PL_LSOCK_PROTOCOL_UDP (UDP transport protocol), 1-…
- `lsock.localportlist` (STRING), default= "" (empty string) — For the currently selected socket (selection is made through lsock.num) sets/returns the list of listening ports on any of which this socket will accept an incoming UDP…
- `lsock.localport` R/O (WORD), default= 0. [read-only] — For the currently selected socket (selection is made through lsock.num) returns the current local port of the socket.
- `lsock.remoteip` R/O (STRING), default= "0.0.0.0". [read-only] — For the currently selected socket (selection is made through lsock.num) returns the IP address of the host with which this socket had the most recent or currently has a…
- `lsock.remoteport` R/O (WORD), default= 0. [read-only] — For the currently selected socket (selection is made through lsock.num) returns the port number of the host with which this socket had the most recent or currently has a…
- `lsock.inconenabledmaster` (ENUM, BYTE), default= 1- YES (incoming connections are globally enabled) — A master switch that globally defines whether incoming connections will be accepted: 0- NO (no socket will be allowed to accept an incoming connection), 1- YES (incoming…
- `lsock.targetip` (STRING), default= "0.0.0.0" — For active opens on the currently selected socket (selection is made through lsock.num) specifies the target IP to which the socket will attempt to connect to.
- `lsock.targetport` (WORD), default= 0 — For active opens on the currently selected socket (selection is made through lsock.num) specifies the target port to which the socket will attempt to connect to.
- `lsock.inconmode` (ENUM, BYTE), default= 0- PL_LSOCK_INCONMODE_NONE (does not accept any incoming connections) — For the currently selected socket (selection is made through lsock.num) specifies whether incoming connections (passive opens) will be accepted and, if yes, from which…
- `lsock.outport` (WORD), default= 0 (automatic) — For the currently selected socket (selection is made through lsock.num) sets/returns the number of the port that will be used by the socket to establish outgoing…
- `lsock.reconmode` (ENUM, BYTE), default= 0- PL_LSOCK_RECONMODE_0 — For the currently selected socket (selection is made through lsock.num) whether the socket accepts reconnects, and, if yes, from which sources.
- `lsock.newtxlen` R/O (DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through lsock.num) returns the amount of uncommitted TX data in bytes.
- `lsock.txlen` R/O (DWORD), default=0 (0 bytes). [read-only] — For the selected socket (selection is made through lsock.num) returns the total number of bytes currently found in the TX buffer (including the uncommitted data).
- `lsock.txfree` R/O (DWORD), default=0 (0 bytes). [read-only] — For the selected socket (selection is made through lsock.num) returns the amount of free space in the TX buffer in bytes.
- `lsock.rxlen` R/O (DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through lsock.num) returns total number of bytes currently waiting in the RX buffer to be extracted and processed by your…
- `lsock.sinkdata` (ENUM, BYTE), default= 0- NO (normal data processing) — For the currently selected socket (selection is made through lsock.num) specifies whether the incoming data should be discarded.
- `lsock.connectiontout` (WORD), default= 0 (no timeout) — For the currently selected socket (selection is made through lsock.num) sets/returns connection timeout threshold for the socket in half-second increments.
- `lsock.toutcounter` R/O (WORD), default= 0 [read-only] — For the currently selected socket (selection is made through lsock.num) returns the time, in 0.5 second intervals, elapsed since the data was last send or received on…
- `lsock.targetbcast` (ENUM, BYTE), default= 0- NO — For the currently selected socket (selection is made through lsock.num) specifies whether this port will be sending its outgoing UDP datagrams as link-level broadcasts:…
- `lsock.rxpacketlen` R/O (DWORD), default= 0 (0 bytes). [read-only] — For the selected socket (selection is made through lsock.num) returns the length (in bytes) of the UDP datagram being extracted from the RX buffer.
- `lsock.acceptbcast` (ENUM, BYTE), default= 0-NO — For the currently selected socket (selection is made through lsock.num) specifies whether the socket will accept incoming broadcast UDP datagrams: 0- NO (won't accept…
- `lsock.bcast` R/O (ENUM BYTE), default= 0- NO. [read-only] — For the currently selected socket (selection is made through lsock.num) reports whether the current or most recently received UDP datagram was a broadcast one.

Methods / functions:
- `lsock.rxbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through lsock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the RX buffer of the socket.
- `lsock.txbuffrq(numpages as BUFF_PAGE_TYPE) as BUFF_PAGE_TYPE` — For the selected socket (selection is made through lsock.num) pre-requests "numpages" number of buffer pages (1 page= 256 bytes) for the TX buffer of the socket.
- `lsock.close()` — For the selected socket (selection is made through lsock.num) causes the socket to close the connection with the other host.
- `lsock.connect()` — For the selected socket (selection is made through lsock.num) causes the socket to attempt to connect to the target host specified by the lsock.targetport and…
- `lsock.setdata(byref txdata as string)` — For the selected socket (selection is made through lsock.num) adds the data passed in the txdata argument to the contents of the TX buffer.
- `lsock.txclear()` — For the selected socket (selection is made through lsock.num) clears (deletes all data from) the TX buffer.
- `lsock.send()` — For the selected socket (selection is made through lsock.num) commits (allows sending) the data that was previously saved into the TX buffer using the lsock.setdata…
- `lsock.notifysent(threshold as word)` — Using this method for the selected socket (selection is made through lsock.num) will cause the on_lsock_data_sent event to be generated when the amount of committed data…
- `lsock.getdata(maxinplen as word) as string` — For the selected socket (selection is made through lsock.num) returns the string that contains the data extracted from the RX buffer.
- `lsock.rxclear()` — For the selected socket (selection is made through lsock.num) clears (deletes all data from) the RX buffer.
- `lsock.peekdata(maxinplen as word) as string` — METHOD.
- `lsock.nextpacket()` — For the selected socket (selection is made through lsock.num) in the UDP mode ( lsock.protocol= 0- PL_SOCK_PROTOCOL_UDP) closes processing of current UDP datagram and…
- `lsock.redir(redir as pl_redir) as pl_redir` — For the selected socket (selection is made through lsock.num) redirects the data being RXed to the TX buffer of the same socket, different socket, or another object that…

Events:
- `on_lsock_event(newstate as pl_lsock_state)` — Notifies your program that the socket state has changed.
- `on_lsock_data_sent` — Generated after the total amount of committed data in the TX buffer of the socket (lsock.txlen - lsock.newtxlen) is found to be less than the threshold that was preset…
- `on_lsock_data_arrival` — Generated when at least one data byte is present in the RX buffer of the socket (i.e. for this socket the lsock.rxlen>0).

Enums:
- `pl_lsock_state`: PL_LSST_CLOSED, PL_LSST_PO, PL_LSST_AO, PL_LSST_EST, PL_LSST_PC, PL_LSST_AC
- `pl_lsock_protocol`: PL_LSOCK_PROTOCOL_UDP, PL_LSOCK_PROTOCOL_TCP
- `pl_lsock_inconmode`: PL_LSOCK_INCONMODE_NONE, PL_LSOCK_INCONMODE_SPECIFIC_IPPORT, PL_LSOCK_INCONMODE_SPECIFIC_IP_ANY_PORT, PL_LSOCK_INCONMODE_ANY_IP_ANY_PORT
- `pl_lsock_reconmode`: PL_LSOCK_RECONMODE_0, PL_LSOCK_RECONMODE_1, PL_LSOCK_RECONMODE_2, PL_LSOCK_RECONMODE_3

## lfd.tph

**object lfd** — This is the Linux flash disk (lfd.) object, it allows you to access, create and delete files on the underlying Linux system.

Properties:
- `lfd.laststatus` R/O (ENUM, BYTE), default= 0- PL_LFD_STATUS_OK (completed successfully). [read-only] — Returns the execution result for the most recent disk-related method execution.
- `lfd.currentdir` R/O (STRING) [read-only] — Returns the current directory.
- `lfd.filenum` (BYTE), default= 0 (file #0 selected) — Sets/returns the number of the currently selected file.
- `lfd.fileopened` R/O (ENUM, BYTE), default= 0- NO (no file is currently opened on this file number). [read-only] — Reports if any file is currently opened "on" the selected file number (selection is made through lfd.filenum.
- `lfd.pointer` R/O (DWORD). [read-only] — Returns the pointer position for the file opened "on" the currently selected file number (selection is made through lfd.filenum).
- `lfd.filesize` R/O (DWORD). [read-only] — Returns the size, in bytes, of the file opened "on" the currently selected file number (selection is made through lfd.filenum).

Methods / functions:
- `lfd.setcurrentdir(byref dir as string) as pl_lfd_status_codes` — Sets the current directory.
- `lfd.create(byref file as string) as pl_lfd_status_codes` — Creates a new file with the specified name.
- `lfd.delete(byref file as string) as pl_lfd_status_codes` — Deletes a file with the specified file name.
- `lfd.rename(byref old_file as string, byref new_file as string) as pl_lfd_status_codes` — Renames a file specified by its name.
- `lfd.open(byref file as string) as pl_lfd_status_codes` — Opens a file with a specified name "on" a currently selected file number (selection is made through lfd.filenum).
- `lfd.close()` — Closes the file opened "on" a currently selected file number (selection is made through lfd.filenum).
- `lfd.setpointer(pos as dword) as pl_lfd_status_codes` — Sets the new pointer position for a file opened "on" a currently selected file number (selection is made through lfd.filenum).
- `lfd.setdata(byref data as string) as pl_lfd_status_codes` — Writes the data string to a file opened "on" a currently selected file number (selection is made through lfd.filenum).
- `lfd.getdata(maxinplen as byte) as string` — Reads a specified number of bytes from the file opened "on" a currently selected file number (selection is made through lfd.filenum).
- `lfd.setfilesize(newsize as dword) as pl_lfd_status_codes` — Sets (reduces) the file size of a file opened "on" a currently selected file number (selection is made through lfd.filenum.
- `lfd.getnextdirmember() as string` — Returns the next filename (if any) found in the current directory (can be changed with lfd.setcurrentdir).
- `lfd.resetdirpointer() as pl_lfd_status_codes` — Resets the directory pointer to zero.
- `lfd.find(frompos as dword, byref substr as string,instance as word,dir as forward_back,incr as word,mode as pl_lfd_find_modes) as dword` — Finds the Nth instance of data satisfying selected criteria in a file opened "on" a currently selected file number (selection is made through fd.filenum).
- `lfd.getfreespace() as dword` — Returns the available disk space for the current directory.
- `lfd.getnumfiles() as dword` — Returns the total number of files currently stored in the current directory.
- `lfd.copyfile(byref src as string, byref dest as string) as pl_lfd_status_codes` — Copy file. src - A string (up to 255 characters) with the full path to source file. dest - A string (up to 255 characters) with the full path including the name of the…

Enums:
- `pl_lfd_status_codes`: PL_LFD_STATUS_OK, PL_LFD_STATUS_FAIL, PL_LFD_STATUS_DUPLICATE_NAME, PL_LFD_STATUS_NOT_FOUND, PL_LFD_STATUS_NOT_OPENED
- `pl_lfd_find_modes`: PL_LFD_FIND_EQUAL, PL_LFD_FIND_NOT_EQUAL, PL_LFD_FIND_GREATER, PL_LFD_FIND_GREATER_EQUAL, PL_LFD_FIND_LESSER, PL_LFD_FIND_LESSER_EQUAL

## sled.tph

**object sled** — 


Methods / functions:
- `sled.send(byref sled_data, num_bytes as word, brightness as byte, max_brightness as byte)` — 

## syscalls.tph


Methods / functions:
- `val(byref sourcestr as string) as word` - Converts string representation of a value into 16-bit value (word or short). **[docs.tibbo.com: понимает префиксы &b и &h; с TiOS 2.0 заменяет удалённую `vali` (знаковый результат - присвоить в short)]**
- `lval(byref sourcestr as string) as dword` — Converts string representation of a value into 32-bit value (dword or long).
- `str(num as integer) as string` - Converts unsigned 16-bit numeric value (word) into its decimal string representation.Can be invoked implicitly, through the string_var=word_var expression. **[docs.tibbo.com: в docs: `str(num as word) as string`]**
- `lstr(byref num as dword) as string` — Converts unsigned 32-bit numeric value (dword) into its decimal string representation.
- `stri(num as integer) as string` — Converts signed 16-bit numeric value (short) into its decimal string representation.
- `lstri(byref num as long) as string` — Converts signed 32-bit numeric value (long) into its decimal string representation.
- `hex(num as word) as string` - Converts unsigned 16-bit numeric value (word) into its HEX string representation. **[docs.tibbo.com: в docs: `hex(num as integer)`]**
- `lhex(byref num as dword) as string` — Converts unsigned 32-bit numeric value (dword) into its HEX string representation.
- `bin(num as word) as string` - Converts unsigned 16-bit numeric value (word) into its binary string representation. **[docs.tibbo.com: в docs: `bin(num as integer)`]**
- `lbin(byref num as dword) as string` — Converts unsigned 32-bit numeric value (dword) into its binary string representation.
- `left(byref sourcestr as string, len as byte) as string` — Returns len leftmost characters of a string sourcestring.
- `right(byref sourcestr as string, len as byte) as string` — Returns len rightmost characters of a string sourcestr.
- `mid(byref sourcestr as string, frompos as byte, len as byte) as string` — Returns len characters from a string sourcestr starting from position pos.
- `len(byref sourcestr as string) as byte` — Returns the length of (number of characters in) the string sourcestr.
- `instr(frompos as byte,byref sourcestr as string,byref substr as string,num as byte) as byte` — Finds the Nth occurrence (defined by num, counting from 1) of a substring substr in a string sourcestr.
- `asc(byref sourcestr as string) as byte` — Returns the ASCII code of the leftmost character of the string.
- `chr(asciicode as byte) as string` — Returns the string that consists of a single character with ASCII code asciicode.
- `ddstr(byref str as string) as string` — Converts "dot-decimal value" in str into "dot-decimal string".
- `ddval (byref str as string) as string` — Converts "dot-decimal string" in str into "dot-decimal value".
- `strgen(len as byte,byref substr as string) as string` — Generates a string of len length consisting of repeating substrings substr.
- `strsum(byref sourcestr as string) as word` — Calculates 16-bit (word) sum of ASCII codes of all characters in a string sourcestr.
- `weekday(daycount as word) as pl_days_of_week` — Returns the day of the week for a given day number.
- `year(daycount as word) as byte` — Returns the year for a given day number.
- `month(daycount as word) as pl_months` — Returns the month for a given day number.
- `date(daycount as integer) as byte` - Returns the date for a given day number. **[docs.tibbo.com: в docs: `date(daycount as word)`]**
- `daycount(year as byte, month as byte, date as byte) as word` — Returns the day number for a given year, month, and date.
- `hours(mincount as word) as byte` — Returns the hours value (in 24-hour format) for a given minutes number.
- `minutes(mincount as word) as byte` — Returns the minutes value for given minutes number.
- `mincount(hours as byte, minutes as byte) as word` — Returns the minutes number for a given hours and minutes.
- `cfloat(byref num as real) as valid_invalid` — Floating-point calculations can lead to invalid result (#INF, -#INF errors, as per IEEE specification).
- `fstr(byref num as real) as string` - **[docs.tibbo.com: отдельной страницы в docs нет; упоминается как упрощённый аналог ftostr]**
- `ftostr(byref num as real, mode as ftostr_mode, rnd as byte) as string` — Converts real value into its string representation.
- `strtof(byref str as string) as real` — Converts string representation of a real value into a real value.
- `md5(byref str as string,byref input_hash as string,md5_mode as md5_modes,total_len as word) as string` — Generates MD5 hash on the str string.
- `sha1(byref str as string,byref input_hash as string,sha1_mode as sha1_modes,totallen as word) as string` — Generates SHA1 hash on the str string.
- `random(len as byte) as string` — Generates a string consisting of len random characters.
- `insert(byref dest_str as string,pos as byte,byref insert_str as string) as byte` — Inserts insert_str string into the dest_str string at the insert position pos.
- `aes128enc(byref key as string,byref plain as string) as string` — Encrypts data in 16-byte blocks according to the AES128 algorithm.
- `aes128dec(byref key as string,byref cypher as string) as string` — Decrypts data in 16-byte blocks according to the AES128 algorithm.
- `rc4(byref key as string, skip as word, byref data as string) as string` — Encrypts/decrypts the data stream according to the RC4 algorithm.
- `strand(byref str1 as string,byref str2 as string) as string` — Returns a string containing the result of logical AND operation on data in str1 and str2 arguments.
- `stror(byref str1 as string,byref str2 as string) as string` — Returns a string containing the result of logical OR operation on data in str1 and str2 arguments.
- `strxor(byref str1 as string,byref str2 as string) as string` — Returns a string containing the result of logical exclusive OR (XOR) operation on data in str1 and str2 arguments.
- `strtobin(byref dst, byref src as string, size as byte)` — Deserializes the binary representation of data contained in a string. dst -- The deserialized data. src -- A string containing the binary representation of the data.…
- `bintostr(byref dst as string, byref src, size as byte)` — Serializes data into its binary representation, which is contained in a string. dst -- A string containing the binary representation of the data. src -- The original…
- `hmac256(byref key as string,byref payload as string, byref result as string)` — Calculates the hash-based message authentication code (HMAC) of a data string to be transmitted. key -- Encryption key.
- `es256(byref key as string,byref payload as string, byref result as string)` — Calculates the elliptic curve signature of a data string to be transmitted. key -- Encryption key.

Enums:
- `pl_days_of_week`: PL_DOW_MONDAY=1, PL_DOW_TUESDAY, PL_DOW_WEDNESDAY, PL_DOW_THURSDAY, PL_DOW_FRIDAY, PL_DOW_SATURDAY, PL_DOW_SUNDAY
- `pl_months`: PL_MONTH_JANUARY=1, PL_MONTH_FEBRUARY, PL_MONTH_MARCH, PL_MONTH_APRIL, PL_MONTH_MAY, PL_MONTH_JUNE, PL_MONTH_JULY, PL_MONTH_AUGUST, PL_MONTH_SEPTEMBER, PL_MONTH_OCTOBER, PL_MONTH_NOVEMBER, PL_MONTH_DECEMBER
- `ftostr_mode`: FTOSTR_MODE_AUTO, FTOSTR_MODE_ME, FTOSTR_MODE_PLAIN
- `md5_modes`: MD5_UPDATE, MD5_FINISH
- `sha1_modes`: SHA1_UPDATE, SHA1_FINISH

## constants.tph


Enums:
- `off_on`: PL_OFF, PL_ON
- `no_yes`: NO, YES
- `dis_en`: DISABLED, ENABLED
- `low_high`: LOW, HIGH
- `ok_ng`: OK, NG
- `wln_ok_ng_rej`: WLN_OK, WLN_NG, WLN_REJ
- `valid_invalid`: VALID, INVALID
- `accepted_rejected`: ACCEPTED, REJECTED
- `forward_back`: FORWARD, BACK
- `ver_hor`: PL_VERTICAL, PL_HORIZONTAL
- `ris_fal`: RISING, FALLING
- `pl_redir`: PL_REDIR_NONE=0, PL_REDIR_SER, PL_REDIR_SER0=1, PL_REDIR_SER1, PL_REDIR_SOCK0=3, PL_REDIR_NONE=0, PL_REDIR_SER, PL_REDIR_SER0=1, PL_REDIR_SER1, PL_REDIR_SER2, PL_REDIR_SER3, PL_REDIR_SOCK0=6, PL_REDIR_SOCK1, PL_REDIR_SOCK2, PL_REDIR_SOCK3, PL_REDIR_SOCK4, PL_REDIR_SOCK5, PL_REDIR_SOCK6, PL_REDIR_SOCK7, PL_REDIR_SOCK8, PL_REDIR_SOCK9, PL_REDIR_SOCK10, PL_REDIR_SOCK11, PL_REDIR_SOCK12, PL_REDIR_SOCK13, PL_REDIR_SOCK14, PL_REDIR_SOCK15, PL_REDIR_LSOCK0, PL_REDIR_LSOCK1, PL_REDIR_LSOCK2, PL_REDIR_LSOCK3, PL_REDIR_LSOCK4, PL_REDIR_LSOCK5, PL_REDIR_LSOCK6, PL_REDIR_LSOCK7, PL_REDIR_LSOCK8, PL_REDIR_LSOCK9, PL_REDIR_LSOCK10, PL_REDIR_LSOCK11, PL_REDIR_LSOCK12, PL_REDIR_LSOCK13, PL_REDIR_LSOCK14, PL_REDIR_LSOCK15


# Platform-specific object headers (members NOT in the generic headers above)

Newer platforms (TPP2W(G3), TPP3W(G3), EM3000W, WM2000, WS1101/WS1102) ship their own sock/sys/ser/wln headers.
Below: only members that are new or re-declared there. If a generic member is missing on such a platform, check the file.


## EM3000W/EM3000W_sock.tph

- property `sock.httppassword` (STRING), default= "" — Sets or returns the HTTP server password for Digest Authentication.

## KLM106_32/KLM106_32.tph

- enum `pl_sock_interfaces`: PL_SOCK_INTERFACE_NULL, PL_SOCK_INTERFACE_WLN=2, PL_SOCK_INTERFACE_PPP=3
- enum `pl_adc_num`: PL_ADC_NUM_0, PL_ADC_NUM_1, PL_ADC_NUM_2, PL_ADC_NUM_3

## KLM601_32/KLM601_32.tph

- enum `pl_sock_interfaces`: PL_SOCK_INTERFACE_NULL, PL_SOCK_INTERFACE_WLN=2, PL_SOCK_INTERFACE_PPP=3
- enum `pl_adc_num`: PL_ADC_NUM_0, PL_ADC_NUM_1, PL_ADC_NUM_2, PL_ADC_NUM_3

## SPACE_AGE/Space_Age.tph

- enum `pl_sock_interfaces`: PL_SOCK_INTERFACE_NULL, PL_SOCK_INTERFACE_NET, PL_SOCK_INTERFACE_WLN, PL_SOCK_INTERFACE_PPP=3, PL_SOCK_INTERFACE_PPPOE

## TPP2W(G3)/TPP2W(G3)_sock.tph

- property `sock.httppassword` (STRING), default= "" — Sets or returns the HTTP server password for Digest Authentication.

## TPP2W(G3)/TPP2W(G3)_sys.tph

- property `sys.boardtemp` R/O . [read-only] — Reads the current temperature from the onboard temperature sensor Returns -- Valid temperature: A floating-point value representing the temperature in Celsius.
- method `sys.configaccel() as ok_ng`  — Configures the accelerometer sensor, ensuring that the accelerometer is properly set up and ready for data capture.
- method `sys.captureaccel()`  — Measures and stores the acceleration along the three axes (X, Y, and Z) of the accelerometer.
- property `sys.readaccelx` R/O . [read-only] — Returns the signed short integer value of x-axis in mg.
- property `sys.readaccely` R/O . [read-only] — Returns the signed short integer value of y-axis in mg.
- property `sys.readaccelz` R/O . [read-only] — Returns the signed short integer value of z-axis in mg.

## TPP3W(G3)/TPP3W(G3)_sock.tph

- property `sock.httppassword` (STRING), default= "" — Sets or returns the HTTP server password for Digest Authentication.

## WM2000/wm2000_ser.tph

- property `ser.baudratex` (DWORD), default= 0 — Sets/returns the baudrate for the selected serial port (selection is made through ser.num).

## WM2000/wm2000_sock.tph

- enum `pl_retx_time`: PL_RETX_50, PL_RETX_200
- property `sock.retxtime`  — Indicates the retransmission time, expressed in 10ms intervals.

## WM2000/wm2000_sys.tph

- enum `pl_sys_debug_mode`: PL_SYS_DBG_SERIAL, PL_SYS_DBG_NET, PL_SYS_DBG_NONE
- method `sys.sleep(daycount as word, mincount as word, seconds as byte)`  — Enters a low-power state and reboots the device at the specified date and time.
- property `sys.debugmode`  — Indicates whether the device will use the serial or network interface for debugging: 0 - PL_SYS_DBG_SERIAL (serial interface), 1 - PL_SYS_DBG_NET (Wi-Fi interface).
- enum `pl_app_num`: PL_APP_NUM_0, PL_APP_NUM_1
- property `sys.defaultapp`  — Indicates the default compiled Tibbo BASIC/C application binary the device should load when booting.
- method `sys.reboottoapp(value as pl_app_num)`  — Reboots the device and loads the specified compiled Tibbo BASIC/C application binary: 0 - PL_APP_NUM_0 (APP0), 1 - PL_APP_NUM_1 (APP1).

## WM2000/wm2000_wln.tph

- property `wln.autodhcpip` (STRING) — Sets/returns desired IP address that will be requested during DHCP discovery from the dcb.
- property `wln.autodhcphn` (STRING) — Sets/returns desired desired hostname for DHCP from the dcb.
- method `wln.gettlscert(byref cert, len as word)`  — This method retrieves the certificate as an array from dcb. len -- length of the certificate
- method `wln.settlscert(byref cert, len as word)`  — This method stores the certificate as an array in dcb. len -- length of the certificate
- method `wln.disablewifiradio()`  — turn wifi radio off

## WS1101/ws1101_sys.tph

- enum `pl_sys_debug_mode`: PL_SYS_DBG_SERIAL, PL_SYS_DBG_NET
- method `sys.sleep(daycount as word, mincount as word, seconds as byte)`  — Enters a low-power state and reboots the device at the specified date and time.
- property `sys.debugmode`  — Indicates whether the device will use the serial or network interface for debugging: 0 - PL_SYS_DBG_SERIAL (serial interface), 1 - PL_SYS_DBG_NET (Wi-Fi interface).
- enum `pl_app_num`: PL_APP_NUM_0, PL_APP_NUM_1
- property `sys.defaultapp`  — Indicates the default compiled Tibbo BASIC/C application binary the device should load when booting.
- method `sys.reboottoapp(value as pl_app_num)`  — Reboots the device and loads the specified compiled Tibbo BASIC/C application binary: 0 - PL_APP_NUM_0 (APP0), 1 - PL_APP_NUM_1 (APP1).

## WS1102/ws1102_ser.tph

- property `ser.baudratex` (DWORD), default= 0 — Sets/returns the baudrate for the selected serial port (selection is made through ser.num).

## WS1102/ws1102_sys.tph

- enum `pl_sys_debug_mode`: PL_SYS_DBG_SERIAL, PL_SYS_DBG_NET, PL_SYS_DBG_NONE
- method `sys.sleep(daycount as word, mincount as word, seconds as byte)`  — Enters a low-power state and reboots the device at the specified date and time.
- property `sys.debugmode`  — Indicates whether the device will use the serial or network interface for debugging: 0 - PL_SYS_DBG_SERIAL (serial interface), 1 - PL_SYS_DBG_NET (Wi-Fi interface).
- enum `pl_app_num`: PL_APP_NUM_0, PL_APP_NUM_1
- property `sys.defaultapp`  — Indicates the default compiled Tibbo BASIC/C application binary the device should load when booting.
- method `sys.reboottoapp(value as pl_app_num)`  — Reboots the device and loads the specified compiled Tibbo BASIC/C application binary: 0 - PL_APP_NUM_0 (APP0), 1 - PL_APP_NUM_1 (APP1).

## WS1102/ws1102_wln.tph

- property `wln.autodhcpip` (STRING) — Sets/returns desired IP address that will be requested during DHCP discovery from the dcb.
- property `wln.autodhcphn` (STRING) — Sets/returns desired desired hostname for DHCP from the dcb.
- method `wln.gettlscert(byref cert, len as word)`  — This method retrieves the certificate as an array from dcb. len -- length of the certificate
- method `wln.settlscert(byref cert, len as word)`  — This method stores the certificate as an array in dcb. len -- length of the certificate
- method `wln.disablewifiradio()`  — turn wifi radio off


# Сверка с docs.tibbo.com (октябрь 2026)

Сверено автоматически: 461 страница свойств, методов и событий `object_*` и `linux_object_*`, 47 страниц `syscall_*`, константы enum на страницах объектов. Выше в строках пометки **[docs.tibbo.com: …]** - расхождения со справочником Tibbo. Правило: имена и сигнатуры из .tph (выше) соответствуют компилятору конкретной версии TiOS; docs местами старее (синтаксис без `()`, `{byte | word}` вместо `BUFF_PAGE_TYPE`). При конфликте проверяй .tph своей платформы в TIDE.

## Есть в docs, не было в справочнике
- `stor.setdata(byref datatoset as string, startaddr as word) as byte` - запись в EEPROM (раньше называлась `stor.set`). Возвращает число записанных байт; запись удалась, только если оно равно `len(datatoset)`. Каждый байт строки - отдельный цикл записи (износ, см. eeprom_life).
- `i2c.channel` (byte, по умолчанию 0) - в docs так называется выбор канала I²C; в .tph - `i2c.num`.
- `sock.event`, `sock.eventsimple` - **удалены (DEPRECATED)**: состояние сокета приходит аргументами `newstate`/`newstatesimple` события `on_sock_event`.
- `vali` - **удалена** в TiOS 2.0: для знаковых значений `val()` с присвоением в `short`.
- Объекты `io.` и `pat.` в Linux-среде LTPP3(G2) (раздел docs «Development (Linux)», страницы `linux_object_io_*`, `linux_object_pat_*`) - см. ниже.

## Есть в справочнике, нет отдельной страницы в docs
`bt.flowcontrol`, `fd.copymonitor`, `io.intcount/intedge/intmode/intstate` (io-2xxx), `kp.setlabel`, `lcd.bmpfromfile/datawidth/getpixel`, `rtc.calibration/clock512`, `ser.xonchar/xoffchar`, `ser.baudratex`, `sock.gendataarrivalevent/peekinband/targetmac/tlsinitfromarray/httppassword/retxtime`, `sys.trace/exec`, математика `sin…atan2, sqrt`, `wln.seteappeap/seteaptls/seteapttls/autodhcpip/autodhcphn/gettlscert/settlscert/disablewifiradio`, `fstr`, объекты `dhcp`(события), `tls`, `tpram`, `lsock`, `lfd`, `sled`. Это не ошибка: они есть в .tph новых TiOS, но документацией не покрыты - бери сигнатуру только из .tph.

## Значения по умолчанию и R/O по docs
| Член | docs.tibbo.com | Было в справочнике |
|---|---|---|
| `kp.repeatdelay` | 3 (30 мс), 0–254 | 50 (0,5 с) |
| `net.gatewayip` | "127.0.0.1" | "0.0.0.0" |
| `wln.dhcp` | 0 - NO (или значение параметра dhcp из DCB) | 1 - YES |
| `wln.autodhcp`, `wln.autoconnect` | 0 - NO | не указано |
| `sys.wdenabled` / `sys.wdautoreset` / `sys.wdperiod` | NO / ENABLED / 3000 (≈30 с, 0–3000) | не указано |
| `sys.debugmode` | 0 - PL_SYS_DBG_SERIAL | не указано |
| `sys.defaultapp` | 1 - PL_APP_NUM_1 | не указано |
| `stor.base` | размер служебной области + 1 (обычно 29) | 8 |
| `sock.remotemac` | "0.0.0.0" (в docs, вероятно опечатка) | "0.0.0.0.0.0" |
| `ssi.baudrate/direction/mode/zmode` | чтение/запись | было ошибочно R/O (исправлено) |
| `sys.timercountms` | чтение/запись (R/O - `timercountmse`) | без пометки |
| `sys.extresettype`, `sys.boardtemp`, `sys.readaccelx/y/z` | в заголовке страницы без R/O, по смыслу только чтение | R/O |

## Сигнатуры, где docs и .tph расходятся
| docs.tibbo.com | .tph (выше) | Комментарий |
|---|---|---|
| `ssi.str(…, ack_bit as no_yes)` | `ack_bit as pl_ssi_ack_modes` | в новых TiOS режимы ACK расширены (PL_SSI_ACK_OFF/RX/TX_ALL/ALL_BUT_LAST) |
| `wln.upgrade()` | `wln.upgrade(region, fwlength, checksum)` | в docs область задаётся `wln.setupgraderegion`, затем `wln.writeflashpage`, `wln.waitforupgradecompletion` |
| `fd.copyfirmwarelzo(app_present as no_yes)` (32 бит) / `(byref length as dword)` (16 бит) | + ещё 2 варианта | на 32-битных платформах все `fd.copyfirmware*` требуют Monitor V2.00+ |
| `fd.copyfirmwarefromfile()` без результата | `as pl_fd_status_codes` | |
| `i2c.write(b as byte)`, `i2c.read(ack_bit)` | `… as i2c_ack_nack`, `… as byte` | |
| `on_sys_dhcp_ok(…, dhcp_obtained_ip …)` | `ip, gateway_ip, netmask, lease_time` | только имена параметров |
| `str(num as word)`, `hex/bin(num as integer)`, `date(daycount as word)` | `str(num as integer)`, `hex/bin(num as word)`, `date(daycount as integer)` | |
| `sock.tlsinit/tlshandshake … as enum` | `as pl_tls_result` | |

Страницы docs с явными опечатками в синтаксисе (не доверять): `fd.flush` (показан `fd.close`), `fd.mount` (`fd.format`), `fd.rename` (`fd.create`), `fd.getnumfiles` (`fd.getfreespace`), `fd.setsector` (`fd.getsector`), `fd.formatj` (`fd.format`), `sock.rplbuffrq` (`sock.cmdbuffrq`), `romfile.find32` (`romfile.find`), `callback_mqtt_sub_ok` (`callback_mqtt_connect_ok`), `dhcp_start` (`dhcp_get_info`).

## Ограничения по платформам (из страниц членов)
- `ser.baud` (enum pl_ser_baud, 50…4 000 000, по умолчанию PL_SER_BAUD_9600) - пока только LTPP3. На TiOS-платформах - `ser.baudrate` (делитель) и `ser.div9600`; на WM2000/WS1102 ещё `ser.baudratex` в бодах.
- WM2000/WS1102: `ser` поддерживает только скорости 110, 300, 1200, 2400, 4800, 9600, 19 200, 38 400, 57 600, 115 200, 230 400, 460 800, 921 600 (неподдерживаемая → 9600). `beep.frequency` (30 Гц–20 кГц) заменяет `beep.divider`. `bt.mac` только чтение, есть `bt.disconnect`; при `wln.autoconnect` не нужен `wln.boot` для BLE. `wln.networkstart/networkstop` недоступны при `wln.autoconnect = YES`; `wln.domain` - настройка DCB с перезагрузкой; `wln.mac` только чтение. `sys.sleep` - только WM2000 (страница), в .tph также WS1101/WS1102; пробуждение = полная перезагрузка. (wm2000_platform_objects, dsws110x_platform_ws1102_objects)
- `ser.ctsmap`, `ser.rtsmap`, `io.enabled` - «Selected Platforms Only»; на платформах с двунаправленными GPIO (EM500, DS1100) `io.enabled` ничего не делает и всегда читается как YES.
- `sock.cmdbuffsize`, `sock.rplbuffsize`, `sock.tx2buffsize`, `sock.varbuffsize` - только 32-битные платформы.
- Служебные байты каждого буфера: 17 на 16-битных и 33 на 32-битных платформах (буфер из N страниц вмещает N×256 − 17 или N×256 − 33 байт; в примере docs округлено до 16/32). Запрос может быть урезан, если памяти не хватает: проверяй возвращаемое `*buffrq` число страниц. `sys.buffalloc` занимает до 100 мс; изменение размеров буферов открытого сокета закрывает его.
- `sys.boardtemp` (real, °C; 255 - отказ датчика), `sys.configaccel/captureaccel/readaccelx/y/z` (мg) - только TPP Gen.3.
- `sys.defaultapp`, `sys.reboottoapp`, `sys.debugmode` - платформы с двумя приложениями (WM2000, WS1102).
- `wln.autoconnect/autoconnectssid/autoconnectpassword/autodhcp/dhcp` - только WM2000 и WS1102 (параметры DCB; после изменения нужна перезагрузка).
- `pppoe.acmac/ip/sessionid` - устарели с TiOS V4.
- `sys.onsystimerperiod`, `on_sys_timer` - с TiOS V1.2; на платформах без свойства период фиксирован 0,5 с; период не зависит от PLL.
- `wln.domain`, `wln.settxpower` - на WS1102 устарели с TiOS v4.02.

## Конфликт событий на одном прерывании (`ser` и `io`)
`ser` использует линии прерываний в режиме UART с RTS/CTS, а также в Wiegand и clock/data. На одних платформах (EM1000) это независимо от `io.intenabled`, на других (EM2000, TPP2/TPP3) - взаимозависимо: занятая портом линия показывает `io.intenabled = 1`, выключить её нельзя, пока порт открыт (ref_platforms_ser_port_int).

## Объекты io. и pat. в Linux-среде (LTPP3(G2), Tibbo BASIC/C поверх Ubuntu)
Справочник docs: `linux_object_io`, `linux_object_pat`. Отличия от TiOS:
- `io.num` (pl_io_num), `io.enabled` (no_yes, по умолчанию NO - вход), `io.state` (low_high), `io.portnum` (pl_io_port_num), `io.portenabled` (byte, по умолчанию 0 - все входы), `io.portstate` (byte), `io.intnum` (pl_int_num), `io.intenabled` (no_yes, NO), **`io.intedge` (pl_int_edge: PL_INT_EDGE_LOW=1 спад, _HIGH=2 фронт, _BOTH=3)**.
- Методы без предвыбора: `io.lineget(num as pl_io_num) as low_high`, `io.lineset(num as pl_io_num, state as low_high)`, `io.invert(num as pl_io_num)`, `io.portget(num as pl_io_port_num) as byte`, `io.portset(num as pl_io_port_num, state as byte)`.
- Прерывание можно назначить почти на любую линию (PinMux): `io.num=…; io.enabled=NO; io.intnum=PL_INT_NUM_x; io.intedge=…; io.intenabled=YES`.
- События: `on_io_int(linestate as byte)` - битовая маска линий, в очереди не более одного; `on_io_int_line(ionum as byte, intnum as byte, edge as byte)` - по событию на каждое прерывание. Используй одно из двух, иначе в очередь попадёт оба.
- «Прерывания» - это события в конце очереди, без гарантированного времени реакции (удобная замена опросу).
- 8-битные порты виртуальные: линии порта читаются/пишутся по одной слева направо (небольшая «бегущая» задержка).
- `pat.channel` 0–4 (0 - штатные зелёный/красный LED), `pat.greenmap`/`pat.redmap` (для каналов 1–4 - любые линии, канал 0 - фиксирован, −1), `pat.play(pattern, patint)` до 16 шагов (`-`,`R`,`G`,`B`, `~` - цикл, `*` - двойная скорость), `pat.playlb(pattern, patint)` - пять синих LED (`L1`…`L5`, комбинации `L135`), события `on_pat`, `on_pat_led_bar` (в примере docs обработчик назван `on_pat_ledbar` - сверяй с платформой).
- Исключения: в Linux-среде приложение может бросать исключения (linux_guide_exceptions).
