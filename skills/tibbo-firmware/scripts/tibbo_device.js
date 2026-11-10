#!/usr/bin/env node
// Driver for Tibbo's tide-proxy (github.com/tibbotech/tide-proxy): talks to Tibbo devices on the LAN
// over the TIDE UDP protocol (port 65535) without TIDE. Called by tibbo_device.py; prints
// "@@" lines: @@PROGRESS <0..1>, @@DEVICE <json>, @@MESSAGE <text>, @@RESULT <json> (last line).
//
//   node tibbo_device.js <tide-proxy folder> '<json request>'
//   request: {"action": "list" | "upload" | "run" | "stop" | "state" | "buzz" | "reboot",
//             "mac": "0.36.119.87.32.2", "file": "app.tpc", "timeout": 6, "tiosFirmware": "<path or null>"}
'use strict';
const fs = require('fs');
const net = require('net');
const path = require('path');

const [home, reqText] = process.argv.slice(2);
const req = JSON.parse(reqText || '{}');
const out = (tag, v) => process.stdout.write('@@' + tag + ' ' + (typeof v === 'string' ? v : JSON.stringify(v)) + '\n');
const finish = (res, code) => { out('RESULT', res); setTimeout(() => process.exit(code || 0), 50); };

// No silent TiOS reflash: tide-proxy reflashes TiOS + app when the device refuses programming mode and a
// firmware file can be found. Only an explicit tiosFirmware (user's consent) allows that.
delete process.env.TIDE_PLATFORMS_DIR;

// tide-proxy logs every UDP packet to the console: keep stdout for our @@ lines only.
const realLog = console.log;
console.log = console.info = console.warn = console.debug = () => {};
console.error = (...a) => process.stderr.write(a.join(' ') + '\n');

// tide-proxy also lists serial ports on every refresh; on Linux without udev (containers, WSL, minimal
// distros) that spawn fails with an uncaught error. Serial ports are not used here: ignore those.
process.on('uncaughtException', (e) => {
    const s = String(e && (e.path || e.message) || e);
    if (/udevadm|serialport|ENOENT.*(udev|tty)/i.test(s) || (e && e.syscall && /spawn/.test(e.syscall))) {
        process.stderr.write('ignored: ' + s + '\n');
        return;
    }
    out('RESULT', { ok: false, error: String(e && e.stack || e) });
    process.exit(4);
});

const { TIDEProxy } = require(path.join(home, 'lib', 'tide-proxy.js'));
const ioc = require(path.join(home, 'node_modules', 'socket.io-client'));

const normMac = (m) => (m || '').split('.').map((x) => String(Number(x))).join('.');
const mac = normMac(req.mac);
const timeout = (req.timeout || 6) * 1000;

function freePort() {
    return new Promise((resolve) => {
        const s = net.createServer();
        s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => resolve(p)); });
    });
}

(async () => {
    const port = await freePort();
    new TIDEProxy({ serverAddress: '', proxyName: 'tibbo-skills', port });
    const sock = ioc.io('http://127.0.0.1:' + port + '/tide', { transports: ['websocket'], reconnection: false });
    const devices = {};
    let seen = null;
    const onSeen = [];

    sock.on('device', (d) => {
        if (!d || !d.mac || d.type === 'serial') return;
        const m = normMac(d.mac);
        devices[m] = Object.assign(devices[m] || {}, d, { mac: m });
        if (req.action === 'list') out('DEVICE', devices[m]);
        if (m === mac) { seen = devices[m]; onSeen.splice(0).forEach((f) => f()); }
    });
    sock.on('message', (m) => { if (!m || !m.mac || normMac(m.mac) === mac) out('MESSAGE', String(m && m.data || m)); });

    const waitSeen = (ms) => new Promise((resolve) => {
        if (seen) return resolve(true);
        onSeen.push(() => resolve(true));
        setTimeout(() => resolve(!!seen), ms);
    });

    sock.on('connect_error', (e) => finish({ ok: false, error: 'proxy: ' + e.message }, 4));
    sock.on('connect', async () => {
        sock.emit('refresh');
        if (req.action === 'list') {
            setTimeout(() => finish({ ok: true, devices: Object.values(devices) }), timeout);
            return;
        }
        if (!mac) return finish({ ok: false, error: 'no --mac' }, 2);
        if (!(await waitSeen(timeout))) {
            return finish({ ok: false, error: 'device ' + mac + ' did not answer (same LAN segment? firewall for UDP 65535?)',
                devices: Object.values(devices) }, 3);
        }
        const cmd = (command, data) => sock.emit('command', { mac, command, data: data || '' });
        switch (req.action) {
            case 'state': {
                const before = seen.pcode;
                cmd('PC');
                setTimeout(() => finish({ ok: true, device: devices[mac], changed: devices[mac].pcode !== before }), 1500);
                break;
            }
            case 'buzz': sock.emit('buzz', { mac }); setTimeout(() => finish({ ok: true }), 800); break;
            case 'reboot': sock.emit('reboot', { mac }); setTimeout(() => finish({ ok: true }), 800); break;
            case 'run': cmd('PR', '+'); setTimeout(() => { cmd('PC'); setTimeout(() => finish({ ok: true, device: devices[mac] }), 1200); }, 600); break;
            case 'stop': cmd('PB'); setTimeout(() => { cmd('PC'); setTimeout(() => finish({ ok: true, device: devices[mac] }), 1200); }, 600); break;
            case 'upload': {
                const data = fs.readFileSync(req.file);
                const def = req.tiosFirmware ? { tiosFirmwarePath: req.tiosFirmware } : undefined;
                let last = -1;
                const limit = setTimeout(() => finish({ ok: false, error: 'upload timeout' }, 4), (req.uploadTimeout || 300) * 1000);
                sock.on('upload', (m) => {
                    if (normMac(m.mac) !== mac) return;
                    const p = Math.round(Number(m.data) * 100);
                    if (p !== last) { last = p; out('PROGRESS', String(Number(m.data).toFixed(2))); }
                });
                sock.on('upload_complete', (m) => {
                    if (normMac(m.mac) !== mac) return;
                    clearTimeout(limit);
                    setTimeout(() => finish({ ok: true, device: devices[mac] }), 300);
                });
                sock.on('upload_error', (m) => {
                    if (normMac(m.mac) !== mac) return;
                    clearTimeout(limit);
                    finish({ ok: false, error: m.code || 'upload_error' }, 1);
                });
                sock.emit('application', { mac, data: data.toString('binary'), deviceDefinition: def });
                break;
            }
            default: finish({ ok: false, error: 'unknown action ' + req.action }, 2);
        }
    });
})().catch((e) => { realLog('@@RESULT ' + JSON.stringify({ ok: false, error: String(e && e.stack || e) })); process.exit(4); });
