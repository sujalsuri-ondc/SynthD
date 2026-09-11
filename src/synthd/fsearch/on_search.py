from wonderwords import RandomWord
from uuid import uuid4
from datetime import datetime


# Constants


# Classes
class OnSearch:
    def __init__(self):
        self.RWORD = RandomWord()
        self.n_provider = -1
        self.n_item_provider = []

    def create_payload(self, n_provider: int, n_item_provider : list[int]) -> dict:
        on_search = dict()
        self.n_provider, self.n_item_provider = n_provider, n_item_provider
        on_search["context"], on_search["message"] = dict(), dict()
        self.create_context(on_search["context"])
        self.create_message(on_search["message"])
        return on_search


    def create_context(self, context_envelope: dict):
        bpp_id = str(uuid4())
        context_envelope["domain"] = "RET13"
        context_envelope["country"] = "IND"
        context_envelope["action"] = "On_Search"
        context_envelope["city"] = "std:080"
        context_envelope["core_version"] = "1.0.0"
        context_envelope["bap_id"] = "gcr.ondc.org"
        context_envelope["bap_uri"] = "https://www.gcr.ondc.org"
        context_envelope["bpp_id"] = bpp_id
        context_envelope["bpp_uri"] =  ".".join(["https://www.seller", bpp_id, "com"])
        context_envelope["transaction_id"] = str(uuid4())
        context_envelope["message_id"] = str(uuid4())
        context_envelope["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def create_message(self, message_envelope: dict):
        message_envelope["catalog"] = dict()
        self.create_catalog(message_envelope["catalog"])

    def create_catalog(self, catalog_envelope: dict): 
        catalog_envelope["bpp/descriptor"] = dict()
        catalog_envelope["bpp/providers"] = [dict() for _ in range(self.n_provider)]

        self.create_descriptor(catalog_envelope["bpp/descriptor"])

        for i_provider in range(self.n_provider):
            self.create_providers(catalog_envelope["bpp/providers"][i_provider], self.n_item_provider[i_provider])

    def create_descriptor(self, descriptor_envelope: dict):
        descriptor_envelope["name"] = "Seller NP"
        descriptor_envelope["symbol"] = "https://www.example.com"
        descriptor_envelope["short_desc"] = "short description"
        descriptor_envelope["long_desc"] = "long description"

    def create_providers(self, provider_envelope: dict, n_item: int):
        pass

class RandomGenerator:
    def __init__(self, ):
        self.load_attribute_enums()
        self.load_attribute_criteria()

    def load_attribute_enums(self,):
        pass

    def load_attribute_criteria(self,):
        pass

