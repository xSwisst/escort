from aiogram import Router

from bot.handlers.models_catalog import router as models_catalog_router
from bot.handlers.models_order import router as models_order_router
from bot.handlers.models_payment import router as models_payment_router

router = Router(name="models")
router.include_router(models_catalog_router)
router.include_router(models_order_router)
router.include_router(models_payment_router)
