#!/usr/bin/env python3
"""Test stand-in for a Tibbo device on the TIDE UDP protocol (port 65535), as tide-proxy speaks it:
discovery "_?", X (info), PC (state), Q (programming mode), D (128-byte blocks, reply = 2-byte index),
T (finish: the app's build GUID becomes the app version), PR/PB (run/pause), B (buzz), EC (reboot).
Usage: fake_device.py [--mac 0.36.119.87.32.2] [--refuse-q] [--seconds 60]; writes the received app to
fake_device.tpc in the current folder."""
import re
import socket
import sys
import time

argv = sys.argv[1:]
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
MAC = opt("--mac", "0.36.119.87.32.2")
REFUSE_Q = "--refuse-q" in argv
END = time.time() + float(opt("--seconds", "60"))
TWO = ("PC", "PR", "PB", "CB", "GM", "GP", "SR", "SM", "PO", "SP", "QF", "EC")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("0.0.0.0", 65535))
s.settimeout(0.5)

state = {"pc": "***", "app": "old_app", "ver": "00000000-0000-0000-0000-000000000000", "blocks": {}}
head = ("[%s]" % MAC).encode()
log = open("fake_device.log", "w")


def reply(addr, body, nonce):
    s.sendto(head + body + ((b"|" + nonce) if nonce is not None else b""), addr)


while time.time() < END:
    try:
        msg, addr = s.recvfrom(2048)
    except socket.timeout:
        continue
    if msg.startswith(b"_?"):
        log.write("discover\n"); log.flush()
        reply(addr, b"A", None)
        continue
    m = re.match(rb"^_\[([0-9.]+)\]", msg)
    if not m or ".".join(str(int(x)) for x in m.group(1).split(b".")) != MAC:
        continue
    rest = msg[m.end():]
    cmd = rest[:2].decode("latin-1") if rest[:2].decode("latin-1") in TWO else rest[:1].decode("latin-1")
    body = rest[len(cmd):]
    nonce = None
    if cmd == "D":
        data = body[:130]
        idx = data[0] << 8 | data[1]
        state["blocks"][idx] = data[2:]
        s.sendto(head + b"A" + data[:2], addr)  # D reply: no nonce, the block index in the last 2 bytes
        continue
    if b"|" in body:
        body, nonce = body.rsplit(b"|", 1)
    log.write("%s %r\n" % (cmd, body[:40])); log.flush()
    if cmd == "X":
        reply(addr, ("ATiOS-32 V4.02.02/%s/%s" % (state["ver"], state["app"])).encode(), nonce)
    elif cmd == "PC":
        reply(addr, ("A%s/0000/0000" % state["pc"]).encode(), nonce)
    elif cmd == "Q":
        reply(addr, b"F" if REFUSE_Q else b"A", nonce)
        state["blocks"] = {}
    elif cmd == "QF":
        reply(addr, b"A", nonce)
    elif cmd == "T":
        img = b"".join(state["blocks"][i] for i in sorted(state["blocks"]))
        open("fake_device.tpc", "wb").write(img)
        g = re.search(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", img)
        state["ver"] = g.group().decode() if g else state["ver"]
        state["app"] = "uploaded"
        state["pc"] = "***"
        reply(addr, b"A", nonce)
    elif cmd == "PR":
        state["pc"] = "*R*"
        reply(addr, b"A" + state["pc"].encode(), nonce)
    elif cmd == "PB":
        state["pc"] = "**B"
        reply(addr, b"A" + state["pc"].encode(), nonce)
    else:  # B, EC, N, ...
        reply(addr, b"A", nonce)
