"""
Discord Local IPC Pipe Client
Communicates directly with the local Discord Desktop application via IPC socket/named pipe.
"""

import json
import os
import struct
import sys
import uuid
from typing import Any, Dict, Optional


class DiscordIPCClient:
    OP_HANDSHAKE = 0
    OP_FRAME = 1
    OP_CLOSE = 2
    OP_PING = 3
    OP_PONG = 4

    def __init__(self, client_id: str):
        self.client_id = client_id
        self._pipe = None
        self.is_connected = False

    def connect(self) -> bool:
        """Attempts to open a connection to the local Discord IPC pipe."""
        if sys.platform == "win32":
            for i in range(10):
                pipe_path = f"\\\\.\\pipe\\discord-ipc-{i}"
                try:
                    self._pipe = open(pipe_path, "w+b", buffering=0)
                    self.is_connected = True
                    self._send(self.OP_HANDSHAKE, {"v": 1, "client_id": self.client_id})
                    self._read()  # Read handshake response
                    return True
                except (OSError, FileNotFoundError):
                    continue
        else:
            base_path = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
            for i in range(10):
                pipe_path = os.path.join(base_path, f"discord-ipc-{i}")
                try:
                    import socket
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.connect(pipe_path)
                    self._pipe = sock
                    self.is_connected = True
                    self._send(self.OP_HANDSHAKE, {"v": 1, "client_id": self.client_id})
                    self._read()
                    return True
                except (OSError, FileNotFoundError):
                    continue

        self.is_connected = False
        return False

    def set_activity(self, activity: Dict[str, Any], pid: Optional[int] = None) -> bool:
        """Sends a SET_ACTIVITY frame to update the rich presence."""
        if not self.is_connected:
            return False

        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": pid or os.getpid(),
                "activity": activity,
            },
            "nonce": str(uuid.uuid4()),
        }

        try:
            self._send(self.OP_FRAME, payload)
            response = self._read()
            return response.get("evt") != "ERROR"
        except Exception:
            self.close()
            return False

    def clear_activity(self, pid: Optional[int] = None) -> bool:
        """Clears the active presence."""
        if not self.is_connected:
            return False
        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": pid or os.getpid(),
                "activity": None,
            },
            "nonce": str(uuid.uuid4()),
        }
        try:
            self._send(self.OP_FRAME, payload)
            self._read()
            return True
        except Exception:
            self.close()
            return False

    def _send(self, op: int, payload: Dict[str, Any]) -> None:
        raw_json = json.dumps(payload).encode("utf-8")
        header = struct.pack("<II", op, len(raw_json))
        if sys.platform == "win32":
            self._pipe.write(header + raw_json)
            self._pipe.flush()
        else:
            self._pipe.sendall(header + raw_json)

    def _read(self) -> Dict[str, Any]:
        if sys.platform == "win32":
            header = self._pipe.read(8)
            if not header or len(header) < 8:
                return {}
            op, length = struct.unpack("<II", header)
            data = self._pipe.read(length)
            return json.loads(data.decode("utf-8"))
        else:
            header = self._pipe.recv(8)
            if not header or len(header) < 8:
                return {}
            op, length = struct.unpack("<II", header)
            data = self._pipe.recv(length)
            return json.loads(data.decode("utf-8"))

    def close(self) -> None:
        """Closes the pipe connection."""
        if self._pipe:
            try:
                self._send(self.OP_CLOSE, {})
                self._pipe.close()
            except Exception:
                pass
        self._pipe = None
        self.is_connected = False
