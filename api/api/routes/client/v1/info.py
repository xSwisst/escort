from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import service_session
from services.clients.service import ClientService
from schemas.client import InfoAgreementResponse

router = APIRouter(prefix="/info", tags=["client-info"])


@router.get("/agreement", response_model=InfoAgreementResponse)
async def agreement_info(
    user_id: int = Query(...),
    session: AsyncSession = Depends(service_session),
) -> InfoAgreementResponse:
    agreement = await ClientService(session).get_active_agreement(user_id)
    if not agreement:
        return InfoAgreementResponse()
    return InfoAgreementResponse(
        agreement_id=agreement.agreement_id,
        title=agreement.title,
        document_url=agreement.document_url,
    )
