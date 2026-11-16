from __future__ import annotations

from core.settings import settings
from shared.http import ServiceClient

from .addresses import AddressesApi
from .cards import CardsApi
from .clients import ClientApi
from .forms import FormsApi
from .info import InfoApi
from .invoices import InvoicesApi
from .orders import OrdersApi
from .profile import ProfileApi


class MainApiClient:
    def __init__(self) -> None:
        self._http = ServiceClient(
            settings.API_BASE_URL,
            settings.API_SECRET_KEY,
            service_name="main",
            target_audience=settings.API_AUDIENCE,
        )
        self.clients = ClientApi(self._http)
        self.forms = FormsApi(self._http)
        self.info = InfoApi(self._http)
        self.profile = ProfileApi(self._http)
        self.addresses = AddressesApi(self._http)
        self.invoices = InvoicesApi(self._http)
        self.cards = CardsApi(self._http)
        self.orders = OrdersApi(self._http)

    async def close(self) -> None:
        await self._http.close()


api_client = MainApiClient()
