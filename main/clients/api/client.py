from __future__ import annotations

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
        self.clients = ClientApi()
        self.forms = FormsApi()
        self.info = InfoApi()
        self.profile = ProfileApi()
        self.addresses = AddressesApi()
        self.invoices = InvoicesApi()
        self.cards = CardsApi()
        self.orders = OrdersApi()

    async def close(self) -> None:
        pass


api_client = MainApiClient()
