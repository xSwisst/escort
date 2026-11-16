from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import user_session_auth
from backend.clients.api import api_client
from backend.schemas.models import FavoriteCodesResponse
from backend.services.models import build_favorite_codes_response

router = APIRouter(prefix="/web-app/api/v1/favorites", tags=["web-app-favorites"])


@router.get("", response_model=FavoriteCodesResponse)
async def get_favorite_codes(session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    favorites = await api_client.client_v1.get_favorites(user_id=int(session_payload["user_id"]))
    return build_favorite_codes_response(favorites)


@router.put("/{form_code}", response_model=FavoriteCodesResponse)
async def add_favorite(form_code: str, session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    user_id = int(session_payload["user_id"])
    favorites = await api_client.client_v1.get_favorites(user_id=user_id)
    codes = {item["form_code"] if isinstance(item, dict) else item.form_code for item in getattr(favorites, "items", [])}
    if form_code not in codes:
        await api_client.client_v1.toggle_favorite(user_id=user_id, form_code=form_code)
    updated = await api_client.client_v1.get_favorites(user_id=user_id)
    return build_favorite_codes_response(updated)


@router.delete("/{form_code}", response_model=FavoriteCodesResponse)
async def remove_favorite(form_code: str, session_payload: dict = Depends(user_session_auth)) -> FavoriteCodesResponse:
    user_id = int(session_payload["user_id"])
    favorites = await api_client.client_v1.get_favorites(user_id=user_id)
    codes = {item["form_code"] if isinstance(item, dict) else item.form_code for item in getattr(favorites, "items", [])}
    if form_code in codes:
        await api_client.client_v1.toggle_favorite(user_id=user_id, form_code=form_code)
    updated = await api_client.client_v1.get_favorites(user_id=user_id)
    return build_favorite_codes_response(updated)
