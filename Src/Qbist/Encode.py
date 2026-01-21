"""Encode quantum circuits into the QBIST JSON schema."""

from __future__ import annotations

from datetime import datetime, timezone
from numbers import Number
from pathlib import Path
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional


QBISTPayload = Dict[str, Any]


def _serialize_param(param: Any) -> Any:
    """Serialize a gate parameter into a JSON-friendly representation."""
    if isinstance(param, Number):
        return param
    if isinstance(param, str):
        return param
    if hasattr(param, "name"):
        return str(param)
    if isinstance(param, Iterable) and not isinstance(param, (bytes, bytearray)):
        return [
            _serialize_param(item)
            for item in param
        ]
    return str(param)


def _metadata_payload(seed: Optional[int], metadata: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    base = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
    }
    if metadata:
        base.update(metadata)
    return base


def _from_qiskit(circuit: Any, seed: Optional[int], metadata: Optional[Mapping[str, Any]]) -> QBISTPayload:
    operations: List[Dict[str, Any]] = []
    for instruction, qargs, cargs in circuit.data:
        operations.append(
            {
                "name": instruction.name,
                "qubits": [qubit.index for qubit in qargs],
                "clbits": [clbit.index for clbit in cargs],
                "params": [_serialize_param(param) for param in instruction.params],
            }
        )
    return {
        "qubits": list(range(circuit.num_qubits)),
        "operations": operations,
        "metadata": _metadata_payload(seed, metadata),
    }


def _from_structure(structure: Mapping[str, Any], seed: Optional[int], metadata: Optional[Mapping[str, Any]]) -> QBISTPayload:
    qbist_metadata = _metadata_payload(seed, metadata)
    if "metadata" in structure and isinstance(structure["metadata"], Mapping):
        qbist_metadata.update(structure["metadata"])
    return {
        "qubits": list(structure["qubits"]),
        "operations": list(structure["operations"]),
        "metadata": qbist_metadata,
    }


def circuit_to_qbist(
    circuit: Any,
    *,
    seed: Optional[int] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> QBISTPayload:
    """Convert a Qiskit circuit or custom structure into a QBIST payload."""
    if hasattr(circuit, "num_qubits") and hasattr(circuit, "data"):
        return _from_qiskit(circuit, seed, metadata)
    if isinstance(circuit, Mapping) and "qubits" in circuit and "operations" in circuit:
        return _from_structure(circuit, seed, metadata)
    raise TypeError("Unsupported circuit format for QBIST encoding")


def write_qbist_json(
    circuit: Any,
    path: str | Path,
    *,
    seed: Optional[int] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> QBISTPayload:
    """Write a QBIST JSON file and return the encoded payload."""
    payload = circuit_to_qbist(circuit, seed=seed, metadata=metadata)
    output_path = Path(path)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload
