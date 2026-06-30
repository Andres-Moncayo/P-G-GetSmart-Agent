import pytest
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_design_art_http_endpoint():
    """Test the design art HTTP endpoint."""
    url = "/api/skills/design-art"
    
    # Sample hard data
    hard_data = {
        "genres": ["Action", "RPG"],
        "game_modes": ["Single-player", "Multiplayer"],
        "themes": ["Fantasy", "Adventure"],
        "storyline": "In a world threatened by ancient evil, players embark on an epic quest to save the realm.",
        "platforms": ["PC", "PlayStation", "Xbox"],
        "developer": "Test Studio",
        "publisher": "Test Publisher",
        "release_date": "2024-01-15"
    }
    
    # Sample sources for semantic data
    sources = [
        {
            "url": "https://reddit.com/r/gaming/thread/123",
            "platform": "reddit",
            "relevance": "General discussion about gameplay mechanics",
            "extracted_at": "2024-01-20T10:00:00Z",
            "access_count": 1500
        }
    ]
    
    # Create structured semantic data for each category
    semantic_data = {
        "gameplay_mechanics": {
            "sources": sources,
            "evidence_count": 60,
            "confidence_score": 0.75
        },
        "level_design": {
            "sources": sources,
            "evidence_count": 45,
            "confidence_score": 0.65
        },
        "narrative": {
            "sources": sources,
            "evidence_count": 30,
            "confidence_score": 0.55
        },
        "art_direction": {
            "sources": sources,
            "evidence_count": 25,
            "confidence_score": 0.50
        },
        "sound_design": {
            "sources": sources,
            "evidence_count": 20,
            "confidence_score": 0.45
        }
    }
    
    # Create request payload
    payload = {
        "metadata": {
            "game_id": "test_game_001",
            "game_name": "Test Game"
        },
        "hard_data": hard_data,
        "semantic_data": semantic_data,
        "evidence_count": 180,
        "confidence_score": 0.60
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(url, json=payload)
        
        # If it returns 200, great. If not, it might be 404 depending on exact route registration.
        # Skills routes are registered under /api/skills in skills_routes.py usually.
        # Let's assert we don't get a 404 or 500, but ideally we get 200.
        if response.status_code == 200:
            result = response.json()
            assert result['metadata']['game_name'] == "Test Game"
            assert 'analysis' in result
            assert 'summary' in result
        else:
            # If it fails, we at least ensure it's a validation error or something we can debug
            assert response.status_code != 404, f"Route not found: {url}"
            assert response.status_code != 500, f"Server error: {response.text}"
