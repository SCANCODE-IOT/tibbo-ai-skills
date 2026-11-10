#!/usr/bin/env python3
"""AppBlocks hardware-canvas warnings for a TPS layout (the yellow triangles on Tibbit sockets).

The AppBlocks editor (app.appblocks.io) checks each M/C socket pair with its own Tibbit table and draws a yellow
triangle on the socket; hovering the Tibbit shows the text. These warnings are NOT listed in the Problems tab and do
not stop the build, so a project can look clean ("0 errors, 0 warnings") and still be flagged on the board picture.

This module repeats that check (getTppProjectWarnings in the editor bundle) on data/appblocks_pairs.json:
  - "Incorrect pair"      - a connector the editor does not accept for this module (e.g. #20 over #09/#10: the editor
                            allows only #18 for power Tibbits, although docs.tibbo.com/tibbit_09 also lists #20 and #21);
  - "Connector required"  - a module that has mates but nothing in its C socket;
  - "Tibbit required"     - a connector or C-sensor with an empty M socket (e.g. #28/#29/#30 need #00-3 next to them:
                            it brings +5 V, ground and the two I2C lines);
  - line messages         - an optional line of the module is not wired on this socket.
A C2 connector clears "Connector required" / "Tibbit required" on its tile if at least one pair under it is complete.

  python3 scripts/ab_pairs.py "TPP2W(G2)" S1=05 S2=21 S9=54 S10=20 S11=09
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
INCORRECT = "Incorrect pair"
NEEDS_M = ("49",)             # C Tibbits that need a specific M partner


def load_pairs():
    return json.load(open(os.path.join(DATA, "appblocks_pairs.json"), encoding="utf-8"))


def norm(m):
    m = str(m).strip().lstrip("#").replace("-", "_")
    if re.fullmatch(r"\d", m.split("_")[0]):
        m = "0" + m
    return m


def _form(t):
    return re.sub(r"[ST]", "", t["form"], count=1)


def _group(groups, form, sock):
    if form in ("C1", "M1", "WIFI"):
        return [sock]
    for g in groups.get(form, []):
        if sock in g:
            return g
    return []


def occupancy(board, slots, data=None):
    """{socket str: model} with wide Tibbits (M2/C2/H1/H2) spread over every socket they cover, as the editor does."""
    data = data or load_pairs()
    b = data["boards"].get(board)
    if not b:
        return {}
    out = {}
    for k, v in slots.items():
        n, m = str(k).upper().lstrip("S"), norm(v["model"] if isinstance(v, dict) else v)
        t = data["tibbits"].get(m)
        for f in (_group(b["neighborGroups"], _form(t), n) if t else [n]):
            out[f] = m
    return out


def socket_warnings(board, slots, board_lines=None, data=None):
    """board: 'TPP2W(G2)' etc.; slots: {socket number or 'S1': model}; board_lines: {'S1': {'A': 'PL_IO_NUM_..', ...}}
    (from boards.json, used for the line messages). Returns {socket str: [messages]} for flagged sockets only,
    or None when AppBlocks has no data for this board."""
    data = data or load_pairs()
    b = data["boards"].get(board)
    if not b:
        return None
    tt = data["tibbits"]
    s = {}
    for k, v in slots.items():
        n = str(k).upper().lstrip("S")
        s[n] = norm(v["model"] if isinstance(v, dict) else v)
    groups, mates = b["neighborGroups"], b["mateSockets"]
    c = {}
    for d, p in s.items():
        t = tt.get(p)
        if t:
            for f in _group(groups, _form(t), d):
                c[f] = p
    out = {}
    for M, C in mates:
        p, m = c.get(M), c.get(C)
        if p and m and _form(tt[p]) not in ("H1", "H2") and m not in tt[p]["mates"]:
            out[M] = [INCORRECT]
            out[C] = [INCORRECT]
        if p and not m and tt[p]["mates"]:
            if _form(tt[p]) == "M2":
                if int(C) % 4 != 0:
                    out[C] = ["Connector required"]
            else:
                out[C] = ["Connector required"]
        if not p and m:
            out[M] = ["Tibbit required"]
    for d, p in s.items():
        t = tt.get(p)
        if not t or _form(t) != "C2":
            continue
        g = _group(groups, "C2", d)
        under = [pr for pr in mates if pr[0] in g or pr[1] in g]
        if any(c.get(pr[0]) and c.get(pr[1]) for pr in under):
            for pr in under:
                for sock in pr:
                    if out.get(sock) and out[sock][0] != INCORRECT:
                        out[sock] = []
    for d, p in s.items():
        t = tt.get(p)
        if not t or p not in NEEDS_M:
            continue
        for g in _group(groups, _form(t), d):
            pr = next((x for x in mates if x[1] == g), None)
            if pr and c.get(pr[0]) is None:
                out[pr[0]] = ["Tibbit #" + " or #".join(t["mates"]) + " required"]
    if board_lines is not None:
        for d, p in s.items():
            t = tt.get(p)
            if not t or _form(t) not in ("M1", "M2", "H1", "H2"):
                continue
            socks = sorted(_group(groups, _form(t), d), key=int)
            pins = []
            for so in socks:
                bl = board_lines.get("S" + so)
                if bl is None or bl.get("type") == "C":
                    continue
                pins += [bl.get("lines", {}).get(x, "PL_IO_NULL") for x in "ABCD"]
            msgs = [msg for i, _id, msg in t["lines"] if i >= len(pins) or pins[i] == "PL_IO_NULL"]
            if p == "43_2":
                msgs.append("This Tibbit's ground and signal lines are not isolated from TPS ground.")
            if msgs:
                out[d] = out.get(d, []) + msgs
    return {k: v for k, v in out.items() if v}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    board = sys.argv[1]
    slots = dict(a.split("=", 1) for a in sys.argv[2:])
    boards = json.load(open(os.path.join(DATA, "boards.json"), encoding="utf-8"))
    res = socket_warnings(board, slots, boards.get(board, {}).get("sockets"))
    if res is None:
        print(f"AppBlocks не знает плату {board}")
        return 2
    for k in sorted(res, key=int):
        print(f"S{k}: {'; '.join(res[k])}")
    if not res:
        print("AppBlocks не отметит ни одного сокета")
    return 1 if res else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:      # the reader (head, grep -q) closed the pipe: not an error
        try:
            sys.stdout.close()
        except OSError:
            pass
        os._exit(0)
