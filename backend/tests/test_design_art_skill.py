import pytest
from app.services.macro_skills.design_art_skill.design_art_service import DesignArtService
from app.models.macro_skills.design_art_models import DesignArtInputModel, MiniContextMetadata

@pytest.mark.asyncio
async def test_design_art_endpoint():
    """Test the design art service with a sample request."""
    service = DesignArtService()
    
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
        },
        {
            "url": "https://example.com/review1",
            "platform": "blogs",
            "relevance": "In-depth review of game mechanics",
            "extracted_at": "2024-01-21T14:30:00Z",
            "access_count": 800
        },
        {
            "url": "https://gaming-news.com/article",
            "platform": "news",
            "relevance": "News coverage of game reception",
            "extracted_at": "2024-01-22T09:15:00Z",
            "access_count": 2000
        }
    ]
    
    # Create structured semantic data for each category
    semantic_data = {
        "gameplay_mechanics": {
            "sources": sources[:2],
            "evidence_count": 60,
            "confidence_score": 0.75
        },
        "level_design": {
            "sources": sources[1:3],
            "evidence_count": 45,
            "confidence_score": 0.65
        },
        "narrative": {
            "sources": sources[:1],
            "evidence_count": 30,
            "confidence_score": 0.55
        },
        "art_direction": {
            "sources": sources[2:],
            "evidence_count": 25,
            "confidence_score": 0.50
        },
        "sound_design": {
            "sources": sources[:2],
            "evidence_count": 20,
            "confidence_score": 0.45
        }
    }
    
    # Create input model
    input_data = DesignArtInputModel(
        metadata=MiniContextMetadata(
            game_id="test_game_001",
            game_name="Test Game"
        ),
        hard_data=hard_data,
        semantic_data=semantic_data,
        evidence_count=180,
        confidence_score=0.60
    )
    
    result = await service.analyze(input_data)
    
    assert result is not None
    assert result.metadata.game_name == "Test Game"
    assert result.confidence.overall_score >= 0.0
    assert hasattr(result.analysis, "gameplay")
    assert hasattr(result.analysis, "art_direction")
    assert hasattr(result.summary, "design_philosophy")
