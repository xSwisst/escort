from fastapi import APIRouter

from .addresses import router as addresses_router
from .cards import router as cards_router
from .cities import router as cities_router
from .clients import router as clients_router
from .forms import router as forms_router
from .info import router as info_router
from .invoices import router as invoices_router
from .orders import router as orders_router
from .profile import router as profile_router

router = APIRouter(prefix="/client/v1", tags=["client-v1"])
router.include_router(clients_router)
router.include_router(forms_router)
router.include_router(info_router)
router.include_router(profile_router)
router.include_router(addresses_router)
router.include_router(cities_router)
router.include_router(invoices_router)
router.include_router(cards_router)
router.include_router(orders_router)

__all__ = ["router"]
