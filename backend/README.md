# GetSmart Backend

Backend API server for GetSmart - Game Analysis Pipeline with real-time progress tracking.

## Features

### 🚀 Enhanced Pipeline Tracking
- **Real-time progress monitoring** with detailed phase breakdown
- **Subtask-level tracking** with individual progress percentages
- **Multi-state support**: `waiting`, `running`, `paused`, `blocked`, `completed`, `failed`
- **API timeout handling** with automatic fallback
- **Visual feedback** in frontend with color-coded states

### 📊 Progress Tracking Features

#### States and Colors
- **🔄 Running**: Amber/Orange (`bg-amber-500`) - with spinner animation
- **⏸️ Paused**: Yellow (`bg-yellow-500`) - with pause icon
- **🚫 Blocked**: Dark Red (`bg-red-700`) - with lock icon
- **❌ Failed**: Red (`bg-red-500`) - with X icon
- **✅ Completed**: Green (`bg-success`) - with checkmark

#### API Timeout Management
```python
# Automatic timeout detection (default: 10 seconds)
await pipeline_tracker.start_api_call(
    report_id="your-report-id", 
    api_name="IGDB", 
    timeout_seconds=10
)

# Manual timeout setting per API
api_timeouts = {
    "IGDB": 8,
    "RAWG": 10, 
    "Steam": 15,
    "Tavily": 5
}
```

#### Subtask Progress Tracking
```python
# Start a subtask
await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, "Buscando en bases de datos")

# Update progress (0-100%)
await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Buscando en bases de datos", 75.0)

# Handle special states
await pipeline_tracker.pause_subtask(report_id, Phase.SCRAPING, "Buscando en bases de datos", "Waiting for API rate limit")
await pipeline_tracker.block_subtask(report_id, Phase.SCRAPING, "Buscando en bases de datos", "API not responding")
await pipeline_tracker.fail_subtask(report_id, Phase.SCRAPING, "Buscando en bases de datos", "API returned 404")
```

## Usage

### 1. Pipeline with Subtasks and Timeouts

```python
from app.services.pipeline_tracker import pipeline_tracker
from app.models.pipelines import Phase

async def run_analysis_pipeline(report_id: str):
    # Start phase
    await pipeline_tracker.start_phase(report_id, Phase.SCRAPING)
    
    # Start subtasks
    subtasks = ["Buscando en bases de datos", "Obteniendo datos del juego", "Recopilando reseñas"]
    
    for subtask in subtasks:
        await pipeline_tracker.start_subtask(report_id, Phase.SCRAPING, subtask)
    
    # Try APIs with automatic timeout
    apis = ["IGDB", "RAWG", "Steam"]
    
    for api_name in apis:
        try:
            # Start API call with timeout
            await pipeline_tracker.start_api_call(
                report_id, 
                api_name, 
                {"game": game_name},
                timeout_seconds=10  # Auto-fails if takes longer
            )
            
            # Your actual API call here
            result = await call_api_safely(api_name, game_name)
            
            # Mark as completed
            await pipeline_tracker.complete_api_call(report_id, api_name, len(result))
            
            # Update subtask progress
            progress = (apis.index(api_name) + 1) / len(apis) * 100
            await pipeline_tracker.update_subtask_progress(
                report_id, Phase.SCRAPING, "Obteniendo datos del juego", progress
            )
            
        except Exception as e:
            # API failed - pipeline automatically marks as failed due to timeout
            logger.error(f"{api_name} failed: {e}")
            continue
    
    # Complete phase
    await pipeline_tracker.complete_phase(report_id, Phase.SCRAPING)
```

### 2. Frontend Integration

The frontend automatically picks up the enhanced tracking:

```typescript
// Dashboard.tsx - Subtask states with colors
const getSubtaskState = (phaseIndex: number, substepIndex: number, substepName: string) => {
  const phaseKey = ['scraping', 'analysis', 'synthesis', 'storage'][phaseIndex];
  const phaseData = status?.phases?.[phaseKey];
  
  if (phaseData?.tasks) {
    const task = phaseData.tasks.find((t) => t.name === substepName);
    if (task) {
      return task.status; // 'running', 'paused', 'blocked', 'failed', 'completed'
    }
  }
  
  // Fallback logic...
};

// Colors are automatically applied based on state:
// - running: bg-amber-500 text-amber-500 (spinner icon)
// - paused: bg-yellow-500 text-yellow-500 (pause icon)  
// - blocked: bg-red-700 text-red-700 (lock icon)
// - failed: bg-red-500 text-red-500 (times icon)
// - completed: bg-success text-success (check icon)
```

## Configuration

### API Timeouts
Default timeouts can be configured per API:

```python
# pipeline_main.py - Configure timeouts per API
API_TIMEOUTS = {
    "IGDB": 8,      # Fast API
    "RAWG": 10,     # Medium API  
    "Steam": 15,    # Slow API
    "Tavily": 5     # Very fast API
}
```

### Progress Updates
Real-time updates every 1.5 seconds in frontend:

```javascript
// Polling interval for updates
const pollInterval = setInterval(async () => {
  const statusData = await apiClient.getReportStatus(reportId);
  setStatus(statusData);
}, 1500); // 1.5 seconds
```

## Pipeline Flow

### 1. Scraping Phase (30% weight)
- 🔍 Buscando en bases de datos
- 📥 Obteniendo datos del juego  
- 📊 Recopilando reseñas
- **Auto-fallback**: If one API times out, automatically tries next

### 2. Analysis Phase (40% weight)  
- 🧠 Tech Systems
- 📈 Strategy & Market
- ⚡ Optimization
- 🎯 Spec Detection

### 3. Synthesis Phase (20% weight)
- 🔄 Procesando resultados
- 💡 Creando insights
- 🔗 Construyendo correlaciones

### 4. Storage Phase (10% weight)
- ✅ Validando datos
- 💾 Almacenando resultados
- 📑 Actualizando índices

## Development

### Run API Server
```bash
cd backend
python -m app.main
```

### Testing Pipeline
```bash
python test_pipeline_timeout.py  # Test API timeouts
python test_subtask_tracking.py   # Test subtask progress
```

## Troubleshooting

### Q: APIs keep timing out
A: Increase timeout in `start_api_call()`:
```python
await pipeline_tracker.start_api_call(
    report_id, "Steam", {}, timeout_seconds=30  # Increase from 10s
);
```

### Q: Progress not updating in frontend
A: Ensure you're calling `update_subtask_progress()` with percentage (0-100):
```python
await pipeline_tracker.update_subtask_progress(report_id, Phase.SCRAPING, "Subtask name", 50.0);
```

### Q: Want to pause a subtask
A: Use the pause state:
```python
await pipeline_tracker.pause_subtask(report_id, Phase.SCRAPING, "Subtask name", "Reason for pause");
```