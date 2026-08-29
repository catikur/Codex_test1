from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Persona:
    id: str
    display_name: str
    role: str
    goal: str
    style: str
    model: Optional[Dict[str, Any]] = None


@dataclass
class Phase:
    id: str
    name: str
    objective: str
    turn_order: List[str]
    rounds: Dict[str, int] = field(default_factory=lambda: {"min": 1, "max": 1})


@dataclass
class Deliverable:
    id: str
    name: str
    type: str
    when: str = "session_end"
    schema: Optional[Dict[str, Any]] = None
    export_formats: Optional[List[str]] = None


@dataclass
class StormPack:
    meta: Dict[str, Any]
    personas: List[Persona]
    phases: List[Phase]
    deliverables: List[Deliverable]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StormPack":
        personas = [Persona(**p) for p in data.get("personas", [])]
        phases = [Phase(**p) for p in data.get("phases", [])]
        deliverables = [Deliverable(**d) for d in data.get("deliverables", [])]
        return StormPack(
            meta=data.get("meta", {}),
            personas=personas,
            phases=phases,
            deliverables=deliverables,
        )


@dataclass
class Turn:
    phase_id: str
    round_index: int
    persona_id: str
    content: str


@dataclass
class StormResult:
    transcript: List[Turn]
    deliverables: Dict[str, Any]
