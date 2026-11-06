#!/usr/bin/env python3
# Test stand-in for TIDE's tmake.exe: same arguments and message format, writes the .tpc named in the .tpr.
import re, sys, pathlib
tpr = pathlib.Path(sys.argv[1]); args = sys.argv[2:]
assert any(a.startswith("-p") for a in args), "tmake must get -p<Platforms>"
text = tpr.read_text(encoding="utf-8", errors="replace")
out = re.search(r"(?mi)^\s*output\s*=\s*(.+)$", text).group(1).strip()
debug = re.search(r"(?mi)^\s*debug\s*=\s*(\w+)", text).group(1).lower()
bad = [(n, l) for n, l in enumerate((tpr.parent / "main.tbs").read_text().splitlines(), 1) if "sock.nmu" in l]
for n, _ in bad:
    print("%s(%d): error C1013: 'nmu' is not member of 'sock' object" % (tpr.parent / "main.tbs", n))
if bad:
    sys.exit(1)
(tpr.parent / out).write_bytes(b"TPC" + debug.encode())
print("Build complete: 0 error(s), 0 warning(s)")
