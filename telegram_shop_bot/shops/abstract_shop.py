from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price: str
    reference: str
    image_ref: str

    def get_info(self):
        return self.name, self.price, self.reference, self.image_ref


class Shop(ABC):

    start_url = None

    @abstractmethod
    def find_items(self, item: str, num: int):
        pass

    @abstractmethod
    def _get_name(self):
        pass

    @abstractmethod
    def _get_price(self):
        pass

    @abstractmethod
    def _get_picture_ref(self):
        pass

    @abstractmethod
    def _get_reference(self):
        pass

