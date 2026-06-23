import asyncio
import aiohttp
import json


async def test_design_art_http_endpoint():
    """Test the design art HTTP endpoint."""
    url = "http://localhost:8000/api/macro-skills/design-art/"
    
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
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Print the result in a readable format
                    print("\n" + "="*80)
                    print("HTTP ENDPOINT TEST RESULTS")
                    print("="*80)
                    print(f"Status: {response.status}")
                    print(f"Game: {result['metadata']['game_name']}")
                    print(f"Generated at: {result['metadata']['generated_at']}")
                    print(f"Overall confidence: {result['confidence']['overall_score']:.2f}")

                    print("\nCategory Scores:")
                    for category, score in result['confidence']['category_scores'].items():
                        print(f"  {category}: {score:.2f}")

                    print("\nGameplay Overview:")
                    print(f"  {result['analysis']['gameplay']['overview']}")

                    print("\nArt Direction Overview:")
                    print(f"  {result['analysis']['art_direction']['overview']}")

                    print("\nSummary Design Philosophy:")
                    print(f"  {result['summary']['design_philosophy']}")
                    
                    if result['confidence']['data_quality_notes']:
                        print(f"\nData Quality Notes:")
                        for note in result['confidence']['data_quality_notes']:
                            print(f"  - {note}")
                    
                    print("\n" + "="*80)
                    print("HTTP ENDPOINT TEST SUCCESSFUL!")
                    print("="*80)
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"ERROR: HTTP {response.status}")
                    print(f"Response: {error_text}")
                    return False
        
        except aiohttp.ClientError as e:
            print(f"ERROR: Connection failed: {e}")
            print("Make sure the FastAPI server is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"ERROR: Request failed: {e}")
            return False


if __name__ == "__main__":
    asyncio.run(test_design_art_http_endpoint())