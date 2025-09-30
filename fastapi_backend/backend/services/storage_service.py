import os
import json
import time
from typing import Dict, Any
from utils.config import get_settings
from utils.logging import get_logger
import httpx

logger = get_logger(__name__)

class StorageService:
    """Store session notes to OneDrive if configured, else local filesystem."""
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.STORAGE_PROVIDER.lower()
        self.local_path = self.settings.LOCAL_STORAGE_PATH
        os.makedirs(self.local_path, exist_ok=True)

    # PUBLIC_INTERFACE
    async def save_session_notes(self, session_id: str, notes: Dict[str, Any]) -> Dict[str, Any]:
        """Save session notes and return storage metadata."""
        payload = {
            "session_id": session_id,
            "timestamp": int(time.time()),
            "notes": notes
        }
        if self.provider == "onedrive":
            try:
                meta = await self._save_to_onedrive(session_id, payload)
                return {"provider": "onedrive", **meta}
            except Exception as e:
                logger.error(f"OneDrive save failed, falling back to local: {e}")
        # fallback local
        meta = self._save_to_local(session_id, payload)
        return {"provider": "local", **meta}

    def _save_to_local(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        fname = f"session_{session_id}.json"
        fpath = os.path.join(self.local_path, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return {"path": fpath}

    async def _save_to_onedrive(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        token = await self._get_graph_token()
        folder_id = self.settings.ONEDRIVE_FOLDER_ID
        if not folder_id:
            raise RuntimeError("ONEDRIVE_FOLDER_ID not configured")

        fname = f"session_{session_id}.json"
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{fname}:/content"
        # If using a specific drive ID:
        if self.settings.ONEDRIVE_DRIVE_ID:
            upload_url = f"https://graph.microsoft.com/v1.0/drives/{self.settings.ONEDRIVE_DRIVE_ID}/items/{folder_id}:/{fname}:/content"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.put(upload_url, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }, content=json.dumps(payload).encode("utf-8"))
            if resp.status_code >= 400:
                raise RuntimeError(f"Graph upload error: {resp.status_code} {resp.text}")
            data = resp.json()
            return {"onedrive_item_id": data.get("id"), "name": data.get("name")}

    async def _get_graph_token(self) -> str:
        tenant = self.settings.ONEDRIVE_TENANT_ID
        client_id = self.settings.ONEDRIVE_CLIENT_ID
        client_secret = self.settings.ONEDRIVE_CLIENT_SECRET
        authority = self.settings.ONEDRIVE_AUTHORITY
        scope = self.settings.ONEDRIVE_SCOPE

        if not all([tenant, client_id, client_secret]):
            raise RuntimeError("OneDrive credentials not fully configured")

        token_url = f"{authority}/{tenant}/oauth2/v2.0/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
            "grant_type": "client_credentials"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
            if resp.status_code >= 400:
                raise RuntimeError(f"Token error: {resp.status_code} {resp.text}")
            return resp.json().get("access_token")
