# Scraper Module (GetSmart)

## Visión General

Este módulo implementa el pipeline `scraper` usando **Domain-Driven Design (DDD)** dentro de `src/scraper/` con estas capas:

- `domain/`: modelos y reglas de negocio (ej. `MasterContext` en Pydantic).
- `application/`: orquestación de casos de uso (workers, ensamblado, síntesis, estado).
- `infrastructure/`: integraciones externas (IGDB, RAWG, Steam, Tavily, Gemini).
- `presentation/`: API HTTP de FastAPI (endpoints públicos).

### ¿Por qué no Celery/Redis?

Se decidió usar `FastAPI BackgroundTasks` + `asyncio.gather()` por simplicidad operativa:

- Menos infraestructura (sin broker Redis ni workers Celery).
- Menor complejidad para despliegue inicial (single-node).
- Excelente ajuste para I/O-bound (llamadas HTTP a APIs externas).
- Integración nativa con FastAPI para tareas en background.

Trade-off aceptado: no hay cola distribuida; el estado vive en memoria del proceso.

---

## El Pipeline Paso a Paso

## Fase 1: Ingestión (sin LLM)

Entrada: `POST /scrape` con payload `confirmed_game`.

Flujo:
1. Se encola una tarea de fondo con `BackgroundTasks`.
2. El orquestador corre 4 scrapers en paralelo con `asyncio.gather()`:
   - Design & Art
   - User Experience
   - Technology & Systems
   - Strategy & Market
3. Cada scraper consume fuentes duras (IGDB/RAWG/Steam/Tavily) y produce su Mini-Context.

**Importante**: en esta fase no se usa LLM.

## Fase 2: Análisis Paralelo (Gemini-2.5-flash)

Entrada: 4 Mini-Contexts de Fase 1.

Flujo:
1. Se ejecutan 4 workers de IA asíncronos en paralelo (`asyncio.gather()`).
2. Cada worker llama a Gemini `gemini-2.5-flash` con prompt estricto.
3. La respuesta se exige en JSON estructurado.
4. Se aplica parseo y validación robusta del JSON devuelto.

Salida: 4 JSONs de análisis validados (uno por macro-skill).

## Fase 3: Consolidación (Master-JSON)

Entrada: 4 JSONs validados de Fase 2.

Flujo:
1. Se ensamblan en un objeto `MasterContext` (Pydantic).
2. Se extrae `hard_data_summary` de cada partición.
3. Se calculan metadatos agregados (workers ejecutados/fallidos, confidence, evidence).

Salida: `Master-JSON` final para síntesis.

## Fase 4: Síntesis (Gemini-2.5-pro)

Entrada: Master-JSON de Fase 3.

Flujo:
1. `synthesize_markdown_report(...)` llama a Gemini `gemini-2.5-pro`.
2. Se solicita salida en Markdown profesional.
3. El markdown final se devuelve para persistencia/entrega.

Salida: reporte final en Markdown.

---

## Gestión de Estado (Frontend)

El frontend debe usar **HTTP Short Polling** cada 2 segundos contra:

`GET /api/v1/reports/{report_id}/status`

Estados posibles:
- `queued`
- `processing`
- `completed`
- `failed`

Recomendación frontend:
1. Llamar `POST /scrape`.
2. Tomar `report_id` de la respuesta.
3. Hacer polling cada 2 segundos hasta `completed` o `failed`.
4. En `completed`, leer `details` para resultados/resumen.

---

## Configuración y Ejecución

## Variables de entorno requeridas

Define estas variables antes de ejecutar:

- `IGDB_CLIENT_ID`
- `IGDB_ACCESS_TOKEN`
- `RAWG_API_KEY`
- `STEAM_API_KEY`
- `TAVILY_API_KEY`
- `GEMINI_API_KEY`

Variable especial de desarrollo local:

- `MOCK_TAVILY=true`
  - Cuando está en `true`, `tavily_client.py` devuelve datos simulados.
  - No consume cuota real de Tavily.

Ejemplo (Windows PowerShell):

```powershell
$env:IGDB_CLIENT_ID="..."
$env:IGDB_ACCESS_TOKEN="..."
$env:RAWG_API_KEY="..."
$env:STEAM_API_KEY="..."
$env:TAVILY_API_KEY="..."
$env:GEMINI_API_KEY="..."
$env:MOCK_TAVILY="true"
```

## Comando para levantar FastAPI

Desde la raíz del proyecto:

```bash
uvicorn src.scraper.presentation.api:router --reload
```

Si tu app principal monta el router desde otro módulo (recomendado), usa el módulo principal:

```bash
uvicorn backend.app.main:app --reload
```

---

## Pruebas (CURLs)

## 1) Disparar pipeline

```bash
curl -X POST "http://127.0.0.1:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "8f6f56d2-7d74-4f5f-8a79-0fcb1f6d3d12",
    "name": "Elden Ring",
    "release_year": 2022,
    "igdb_id": 119133,
    "rawg_id": 326243,
    "steam_app_id": 1245620,
    "aliases": ["ER"]
  }'
```

Respuesta esperada (ejemplo):

```json
{
  "status": "queued",
  "report_id": "8f6f56d2-7d74-4f5f-8a79-0fcb1f6d3d12",
  "message": "Scrape task started in background"
}
```

## 2) Polling de estado

```bash
curl "http://127.0.0.1:8000/api/v1/reports/8f6f56d2-7d74-4f5f-8a79-0fcb1f6d3d12/status"
```

Respuesta esperada (ejemplo):

```json
{
  "report_id": "8f6f56d2-7d74-4f5f-8a79-0fcb1f6d3d12",
  "status": "processing",
  "updated_at": "2026-06-25T20:20:10.123456+00:00",
  "message": "Scraping in progress",
  "details": {}
}
```

## 3) Polling automático cada 2 segundos (bash)

```bash
while true; do
  curl -s "http://127.0.0.1:8000/api/v1/reports/8f6f56d2-7d74-4f5f-8a79-0fcb1f6d3d12/status"; echo "";
  sleep 2;
done
```

---

## Nota operativa

El estado del pipeline actual está en memoria (`pipeline_status_store`).
Si el proceso de FastAPI reinicia, los estados anteriores se pierden.
Para producción, se recomienda persistir estado en base de datos.