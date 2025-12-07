# AIstormfy Phase 1 (Hybrid MVP)

Bu repo, çok-ajanlı beyin fırtınası seansları için hafif bir orkestrasyon çekirdeği sağlar. Her "Storm Pack" farklı alanlara ait persona setlerini, fazları ve deliverable şablonlarını tanımlar.

## Mimarinin Özeti
- **Model Adapter Katmanı:** `core/providers.py` içinde `LLMProvider` arayüzü, OpenAI entegrasyonu için `OpenAIProvider`, geleceğe dönük `AnthropicProvider` iskeleti ve test/CLI için `DummyProvider` bulunur.
- **Storm Pack DSL:** `core/models.py` veri sınıfları ve `packs/*.json` dosyaları meta bilgiler, personas, phases ve deliverables yapılarını taşır.
- **Orkestrasyon:** `core/storm_runner.py` storm pack fazlarını yürütür, transcript tutar ve oturum sonunda deliverable üretir.
- **API:** `api/main.py` basit FastAPI endpoint'i (`POST /run_storm`) ile storm pack'i çağırır.

## Geliştirme ve Çalıştırma
1. Bağımlılıkları yükle:
   ```bash
   pip install -r requirements.txt
   ```

2. API'yi başlat:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

3. Seedlings pack'ini çalıştırmak için örnek çağrı:
   ```bash
   curl -X POST http://localhost:8000/run_storm \
     -H "Content-Type: application/json" \
     -d '{
       "pack_id": "seedlings",
       "user_input": "12 yaşındaki meraklı bir çocuk için fen merakı nasıl desteklenir?",
       "context": {"age": 12, "interests": ["fen", "oyun"]}
     }'
   ```

CLI tarzı kullanım için Python örneği:
```python
from core.providers import DummyProvider
from core.storm_runner import StormPackLoader, StormRunner

loader = StormPackLoader()
pack = loader.load("seedlings")
runner = StormRunner(provider_registry={"default": DummyProvider()}, default_model="dummy")
result = runner.run(pack, user_input="12 yaşındaki çocuk için bilim projesi", context={"age": 12})
print(result.transcript)
print(result.deliverables)
```

## Testler
Pytest ile dummy sağlayıcı üzerinden uçtan uca akışı doğrulayabilirsiniz:
```bash
pytest
```
