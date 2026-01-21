from __future__ import annotations

import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List

from src.simulator.bot_engine import BotEngine, ideas_to_payload


@dataclass
class SimulatorConfig:
    bot_count: int
    idea_rate: float
    seed: int
    network_layers: List[int]


def _parse_value(raw: str) -> Any:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = [item.strip() for item in inner.split(",")]
        return [_parse_value(item) for item in items]
    if value.isdigit():
        return int(value)
    if value.replace(".", "", 1).isdigit():
        return float(value)
    return value


def load_config(config_path: Path) -> SimulatorConfig:
    data: Dict[str, Any] = {}
    for line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        data[key.strip()] = _parse_value(raw_value)
    return SimulatorConfig(
        bot_count=int(data.get("bot_count", 100)),
        idea_rate=float(data.get("idea_rate", 1)),
        seed=int(data.get("seed", 0)),
        network_layers=list(data.get("network_layers", [])),
    )


class SimulatorHandler(BaseHTTPRequestHandler):
    engine: BotEngine

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self._send_json(self.engine.status())
            return
        if self.path == "/api/ideas":
            ideas = self.engine.tick()
            payload = {
                "generated": len(ideas),
                "ideas": ideas_to_payload(ideas),
                "recent": self.engine.recent_ideas(),
            }
            self._send_json(payload)
            return
        self._send_json({"error": "not_found"}, status=404)


def create_engine() -> BotEngine:
    config_path = Path(__file__).resolve().parents[2] / "config" / "simulator.yml"
    config = load_config(config_path)
    return BotEngine(
        bot_count=config.bot_count,
        idea_rate=config.idea_rate,
        seed=config.seed,
        network_layers=config.network_layers,
    )


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    engine = create_engine()
    SimulatorHandler.engine = engine
    server = HTTPServer((host, port), SimulatorHandler)
    print(f"Simulator server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
