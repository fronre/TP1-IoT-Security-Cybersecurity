from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from tp1_bls.bls_core import aggregate, aggregate_verify, keygen_from_seed, sign, sk_to_pk, verify


@dataclass
class Sensor:
    name: str
    sk: int
    pk: bytes

    @classmethod
    def from_name(cls, name: str) -> "Sensor":
        sk = keygen_from_seed(f"sensor::{name}".encode())
        return cls(name=name, sk=sk, pk=sk_to_pk(sk))


class Gateway:
    def __init__(self) -> None:
        self.valid_messages: list[str] = []
        self.rejected_messages: list[str] = []

    def validate(self, pk: bytes, message: bytes, signature: bytes) -> bool:
        ok = verify(pk, message, signature)
        if ok:
            self.valid_messages.append(message.decode("utf-8", errors="replace"))
            return True
        self.rejected_messages.append(message.decode("utf-8", errors="replace"))
        return False

    def log_to_file(self, path: str) -> None:
        out = {
            "valid_messages": self.valid_messages,
            "rejected_messages": self.rejected_messages,
        }
        Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")


def run_demo() -> None:
    sensors = [Sensor.from_name(f"sensor-{i}") for i in range(10)]
    gateway = Gateway()
    messages = []
    sigs = []

    for sensor in sensors:
        message = f"{sensor.name}:temperature={20 + (len(sensor.name) % 5) * 0.5}".encode()
        sig = sign(sensor.sk, message)
        messages.append((sensor.pk, message, sig))
        sigs.append(sig)

    for pk, msg, sig in messages:
        gateway.validate(pk, msg, sig)

    tampered = b"sensor-0:temperature=99.0"
    bad_sig = sign(sensors[0].sk, tampered)
    gateway.validate(sensors[0].pk, tampered, bad_sig)

    agg = aggregate([sig for _, _, sig in messages])
    pks = [pk for pk, _, _ in messages]
    msgs = [msg for _, msg, _ in messages]
    ok = aggregate_verify(pks, msgs, agg)
    print({
        "aggregate_verify": ok,
        "valid_count": len(gateway.valid_messages),
        "rejected_count": len(gateway.rejected_messages),
    })


if __name__ == "__main__":
    run_demo()
