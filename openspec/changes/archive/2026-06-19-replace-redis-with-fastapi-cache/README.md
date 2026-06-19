# Replace Redis with FastAPI Cache Implementation

## Purpose

Replace Redis caching with FastAPI in-memory caching for API responses in the scraper system. This simplifies the architecture by removing external Redis dependency while maintaining cache functionality.

## Key Changes

### 1. Cache Storage Replacement
- **From**: Redis external cache
- **To**: FastAPI in-memory caching
- **Benefits**: Simpler deployment, no external service required

### 2. Implementation Strategy
- Use FastAPI's built-in caching (via `fastapi-cache` or similar)
- Maintain same cache patterns and TTL (3600 seconds)
- Keep key format: `scraper:{game_id}:{api_source}:{endpoint_hash}`

### 3. Files to Modify

#### Core Specification Changes
- **`openspec/specs/scraper/scraper_contract.yaml`**
  - Update caching strategy section
  - Replace Redis storage with FastAPI in-memory
  - Keep same cache endpoints and TTL
  - Add FastAPI cache implementation notes

#### Dependency Changes
- **`backend/requirements.txt`**
  - Remove Redis-related dependencies
  - Add FastAPI caching library if needed

## Technical Implementation

### Cache Strategy Update
```yaml
caching:
  api_response_cache:
    enabled: true
    ttl_seconds: 3600
    storage: "FastAPI in-memory"  # Changed from Redis
    key_format: "scraper:{game_id}:{api_source}:{endpoint_hash}"
    
    cached_endpoints:
      - IGDB game metadata
      - RAWG game metadata  
      - Steam Storefront details
      - SteamSpy app details
```

### FastAPI Cache Implementation
```python
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.memory import InMemoryBackend

app = FastAPI()

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
```

## Benefits

1. **Simplified Deployment**: No Redis service to install/maintain
2. **Lower Infrastructure**: Fewer moving parts
3. **Same Performance**: In-memory cache provides comparable speeds
4. **Easier Development**: No external dependencies during development

## Considerations

- **Cache Persistence**: In-memory cache clears on app restart
- **Memory Usage**: Cache stored in application memory
- **Scalability**: For distributed deployment, consider external cache later

## Validation

After implementation, verify:
- Cache functionality works for all API endpoints
- TTL of 3600 seconds is respected
- Key format maintains consistency
- No Redis connection errors occur

## Files Changed

- `openspec/specs/scraper/scraper_contract.yaml` - Updated caching strategy
- `backend/requirements.txt` - Updated dependencies

## Status

**Status**: Ready for implementation  
**Priority**: Medium (simplification improvement)  
**Estimated Effort**: 2-4 hours  
**Risk Level**: Low (cache abstraction already in place)  

---

*This change maintains all existing cache behavior while simplifying the system architecture.*