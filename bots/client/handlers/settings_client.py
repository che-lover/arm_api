import os
import httpx

API_V1 = os.getenv('API_BASE_URL', 'http://138.124.123.68:8080/api').rstrip('/') + '/v1'

async def fetch_bot_settings() -> dict:
    async with httpx.AsyncClient() as cli:
        resp = await cli.get(f"{API_V1}/settings/bot")
        if resp.status_code == 200:
            return resp.json().get('data') or {}
    return {}
