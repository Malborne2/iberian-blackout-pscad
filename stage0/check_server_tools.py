"""Prove the patched server exposes 68 tools when launched exactly as configured
(`python -m pscad_mcp.server`), by speaking MCP over stdio.

This does not touch PSCAD; it only lists tools.
"""
from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading


def main() -> int:
    p = subprocess.Popen(
        [sys.executable, "-m", "pscad_mcp.server"],
        cwd=r"C:\GitHub\PSCAD-MCP",
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", bufsize=1,
    )
    q: queue.Queue = queue.Queue()

    def pump():
        for line in p.stdout:
            q.put(line)

    threading.Thread(target=pump, daemon=True).start()

    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n")
        p.stdin.flush()

    def recv(timeout=30):
        while True:
            line = q.get(timeout=timeout)
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "tool-count-check", "version": "0"}}})
    init = recv()
    send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = recv()

    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    print("server:", init.get("result", {}).get("serverInfo"))
    print("tool count:", len(names))
    for probe in ("pscad_get_ports", "pscad_get_build_dimensions", "pscad_get_canvas_settings",
                  "pscad_get_flags", "pscad_set_flags", "pscad_list_dialogs",
                  "pscad_click_dialog_button"):
        print(f"  {probe}: {'present' if probe in names else 'MISSING'}")
    p.kill()
    return 0 if len(names) == 72 else 1


if __name__ == "__main__":
    sys.exit(main())
