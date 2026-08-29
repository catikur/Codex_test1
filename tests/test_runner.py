from core.providers import DummyProvider
from core.storm_runner import StormPackLoader, StormRunner


def test_runner_produces_transcript_and_deliverable(tmp_path, monkeypatch):
    loader = StormPackLoader(packs_dir="packs")
    pack = loader.load("seedlings")

    provider_registry = {"default": DummyProvider(template="{persona}|{content}")}
    runner = StormRunner(provider_registry=provider_registry, default_model="dummy")

    result = runner.run(pack, user_input="12 yaş meraklı çocuk için bilim projesi", context={"age": 12})

    assert len(result.transcript) > 0
    assert set(result.deliverables.keys()) == {d.id for d in pack.deliverables}
    # Dummy provider echoes persona id
    assert any("pedagog" in turn.content for turn in result.transcript)
    first_deliverable = next(iter(result.deliverables.values()))
    assert isinstance(first_deliverable, str) and len(first_deliverable) > 0
