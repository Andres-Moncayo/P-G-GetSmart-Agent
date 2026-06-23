import asyncio
from app.services.macro_skills.design_art_service import DesignArtService
from app.models.macro_skills.design_art_models import DesignArtInputModel, MiniContextMetadata
import json
from pydantic import HttpUrl


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
            "sources": sources[:2],  # First 2 sources for gameplay
            "evidence_count": 60,
            "confidence_score": 0.75
        },
        "level_design": {
            "sources": sources[1:3],  # Last 2 sources for level design
            "evidence_count": 45,
            "confidence_score": 0.65
        },
        "narrative": {
            "sources": sources[:1],  # First source for narrative
            "evidence_count": 30,
            "confidence_score": 0.55
        },
        "art_direction": {
            "sources": sources[2:],  # Last source for art direction
            "evidence_count": 25,
            "confidence_score": 0.50
        },
        "sound_design": {
            "sources": sources[:2],  # First 2 sources for sound
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
    
    try:
        # Run analysis
        result = await service.analyze(input_data)
        
        # Print the result in a readable format
        print("\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80)
        print(f"Game: {result.metadata.game_name}")
        print(f"Generated at: {result.metadata.generated_at}")
        print(f"Overall confidence: {result.confidence.overall_score:.2f}")

        print("\nCategory Scores:")
        for category, score in result.confidence.category_scores.model_dump().items():
            print(f"  {category}: {score:.2f}")

        print("\nGameplay Overview:")
        print(f"  {result.analysis.gameplay.overview}")

        print("\nArt Direction Overview:")
        print(f"  {result.analysis.art_direction.overview}")

        print("\nSummary Design Philosophy:")
        print(f"  {result.summary.design_philosophy}")
        
        if result.confidence.data_quality_notes:
            print(f"\nData Quality Notes:")
            for note in result.confidence.data_quality_notes:
                print(f"  - {note}")
        
        print(f"\nFull JSON Output:")
        # Convert model to JSON-serializable dict
        result_dict = result.model_dump()
        # Convert HttpUrl objects to strings for JSON serialization
        
        def convert_urls_to_strings(obj):
            if isinstance(obj, dict):
                return {k: convert_urls_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_urls_to_strings(item) for item in obj]
            elif isinstance(obj, HttpUrl):
                return str(obj)
            else:
                return obj
        
        json_result = convert_urls_to_strings(result_dict)
        print(json.dumps(json_result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_design_art_endpoint())