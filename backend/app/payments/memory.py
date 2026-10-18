from app.domain.models import Checkout, Mandate, Receipt, Transaction


class PaymentStore:
    def __init__(self) -> None:
        self.checkouts: dict[str, Checkout] = {}
        self.mandates: dict[str, Mandate] = {}
        self.receipts: dict[str, Receipt] = {}
        self.by_share: dict[str, str] = {}
        self.by_checkout: dict[str, str] = {}
        self.transactions: dict[str, Transaction] = {}
        self.token_by_checkout: dict[str, str] = {}

    def clear(self) -> None:
        self.checkouts.clear()
        self.mandates.clear()
        self.receipts.clear()
        self.by_share.clear()
        self.by_checkout.clear()
        self.transactions.clear()
        self.token_by_checkout.clear()


store = PaymentStore()
