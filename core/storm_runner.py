from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Deliverable, Persona, Phase, StormPack, StormResult, Turn
from .providers import LLMProvider


class StormPackLoader:
    def __init__(self, packs_dir: str = "packs"):
        self.packs_dir = Path(packs_dir)

    def load(self, pack_id: str) -> StormPack:
        path = self.packs_dir / f"{pack_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Pack {pack_id} not found at {path}")
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return StormPack.from_dict(data)


class StormRunner:
    def __init__(
        self,
        provider_registry: Dict[str, LLMProvider],
        default_model: str,
    ):
        self.provider_registry = provider_registry
        self.default_model = default_model

    def _get_persona(self, personas: List[Persona], persona_id: str) -> Persona:
        for p in personas:
            if p.id == persona_id:
                return p
        raise ValueError(f"Persona {persona_id} not defined in pack")

    def _select_provider(self, persona: Persona) -> LLMProvider:
        provider_name = (persona.model or {}).get("provider", "default")
        if provider_name == "default":
            provider_name = "default"
        provider = self.provider_registry.get(provider_name)
        if provider is None:
            raise ValueError(f"Provider '{provider_name}' not registered")
        return provider

    def _build_messages(
        self,
        persona: Persona,
        phase: Phase,
        user_input: str,
        context: Optional[Dict[str, Any]],
        transcript: List[Turn],
    ) -> List[Dict[str, str]]:
        system_prompt = (
            f"You are {persona.display_name} acting as {persona.role}. "
            f"Your goal: {persona.goal}. Your style: {persona.style}. "
            f"Current phase objective: {phase.objective}."
        )
        history_snippets = [f"{t.persona_id}: {t.content}" for t in transcript]
        history = "\n".join(history_snippets)
        user_prompt = (
            f"User request: {user_input}.\n"
            f"Context: {json.dumps(context or {}, ensure_ascii=False)}\n"
            f"Transcript so far:\n{history}\n"
            f"Respond concisely as {persona.display_name}."
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def run_phase(
        self,
        pack: StormPack,
        phase: Phase,
        user_input: str,
        context: Optional[Dict[str, Any]],
        transcript: List[Turn],
    ) -> None:
        rounds = phase.rounds.get("min", 1)
        for round_index in range(1, rounds + 1):
            for persona_id in phase.turn_order:
                persona = self._get_persona(pack.personas, persona_id)
                provider = self._select_provider(persona)
                messages = self._build_messages(persona, phase, user_input, context, transcript)
                content = provider.generate(
                    model=(persona.model or {}).get("name", self.default_model),
                    messages=messages,
                    persona_id=persona.id,
                )
                transcript.append(
                    Turn(
                        phase_id=phase.id,
                        round_index=round_index,
                        persona_id=persona.id,
                        content=content,
                    )
                )

    def _deliverable_prompt(
        self,
        deliverable: Deliverable,
        transcript: List[Turn],
        user_input: str,
        context: Optional[Dict[str, Any]],
    ) -> str:
        history = "\n".join(
            [f"Phase {t.phase_id} | {t.persona_id}: {t.content}" for t in transcript]
        )
        return (
            f"You are producing deliverable '{deliverable.name}' ({deliverable.type}).\n"
            f"User request: {user_input}. Context: {json.dumps(context or {}, ensure_ascii=False)}\n"
            f"Transcript summary:\n{history}\n"
            f"Follow schema: {json.dumps(deliverable.schema or {}, ensure_ascii=False)}."
        )

    def generate_deliverables(
        self,
        pack: StormPack,
        transcript: List[Turn],
        user_input: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        outputs: Dict[str, Any] = {}
        for deliverable in pack.deliverables:
            if deliverable.when != "session_end":
                continue
            provider = self.provider_registry.get("default")
            if provider is None:
                raise ValueError("Default provider not registered for deliverables")
            messages = [
                {
                    "role": "system",
                    "content": "You are a collaborative AI summarizer creating structured outputs.",
                },
                {"role": "user", "content": self._deliverable_prompt(deliverable, transcript, user_input, context)},
            ]
            content = provider.generate(
                model=self.default_model,
                messages=messages,
                persona_id="deliverable_bot",
            )
            outputs[deliverable.id] = content
        return outputs

    def run(
        self, pack: StormPack, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> StormResult:
        transcript: List[Turn] = []
        for phase in pack.phases:
            self.run_phase(pack, phase, user_input, context, transcript)
        deliverables = self.generate_deliverables(pack, transcript, user_input, context)
        return StormResult(transcript=transcript, deliverables=deliverables)
