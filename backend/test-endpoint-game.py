import httpx
import asyncio
import uuid

async def test_minecraft_pipeline():
    """Test the full Minecraft pipeline via the correct endpoint"""
    url = "http://localhost:8000/scraper/analyze"
    
    # Usar el UUID que genera el frontend
    game_id = str(uuid.uuid4())
    game_data = {
        "game_id": game_id,
        "name": "Minecraft",
        "release_year": 2011,
        "rawg_id": 1132,
        "steam_app_id": None,
        "aliases": []
    }
    
    print("Starting pipeline for Minecraft...")
    print(f"URL: {url}")
    print(f"Game ID: {game_id}")
    print(f"Request body: {game_data}")
    print("=" * 50)
    
    # Increased timeout to handle longer processing
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            response = await client.post(url, json=game_data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print("-" * 30)
            print(f"Response Text: {response.text}")
            print("-" * 30)
            
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
                print(f"JSON Response: {data}")
                if "report_id" in data:
                    report_id = data["report_id"]
                    print(f"Report ID: {report_id}")
                    return report_id
                else:
                    print("No report_id in response")
                    return None
            else:
                print("Response is not JSON")
                return None
                
        except httpx.TimeoutException:
            print("TIMEOUT: El backend no responde en 60 segundos (esto es normal, el pipeline está procesando)")
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None

async def test_status(report_id: str):
    """Test the status endpoint"""
    url = f"http://localhost:8000/scraper/api/v1/reports/{report_id}/status"
    
    print(f"\nTesting status for report: {report_id}")
    
    for i in range(30):  # More iterations to see the full pipeline
        print(f"\nStatus Check #{i+1}...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Status: {data}")
                    if data.get("status") in ["completed", "failed"]:
                        print(f"Pipeline {data.get('status')}!")
                        return data.get("status") == "completed"
                else:
                    print(f"Status error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Status error: {e}")
        
        await asyncio.sleep(3)  # Wait 3 seconds between checks

    print("\nMaximum status checks reached")
    return False

if __name__ == "__main__":
    report_id = asyncio.run(test_minecraft_pipeline())
    if report_id:
        result = asyncio.run(test_status(report_id))
        if result:
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("\n❌ PIPELINE FAILED OR INCOMPLETE")
    else:
        print("\n⏱️ PIPELINE STARTED BUT PROCESSING TIME LONG (check backend logs)")