from wonderwords import RandomWord
from uuid import uuid4
from datetime import datetime
import os
import json
import pandas as pd
import random

# Constants
PRICE_MIN: int = 100
PRICE_MAX: int = 1_000_000
DIMENSION_MIN: int = 10
DIMENSION_MAX: int = 1_000
TAXONOMY_FILE_PATH = "taxonomy.csv"
ENUM_DIR = ""
BLACK_LIST_ATTRIBUTES = ["size"]

# Classes
class OnSearch:
    def __init__(self, taxonomy_path: str, enum_path: str):
        global TAXONOMY_FILE_PATH, ENUM_DIR
        TAXONOMY_FILE_PATH = taxonomy_path
        ENUM_DIR = enum_path
        self.RWORD = RandomWord()
        self.random_item_generator = RandomItemGenerator()
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

    def create_descriptor(self, descriptor_envelope: dict, name: str = ""):
        descriptor_envelope["name"] = "Seller NP"
        if name != "":
            descriptor_envelope["name"] = name

        descriptor_envelope["symbol"] = "https://www.example.com"
        descriptor_envelope["short_desc"] = "short description"
        descriptor_envelope["long_desc"] = "long description"

    def create_providers(self, provider_envelope: dict, n_item: int):
        provider_envelope["id"] = str(uuid4())
        provider_envelope["fulfillments"] = [{"id": 1, "type": "delivery"}, {"id": 2, "type": "pickup"}]
        provider_envelope["items"] = [self.random_item_generator.create_item() for _ in range(n_item)]

class RandomItemGenerator:
    def __init__(self, ):
        self.attribute_type_list = []
        self.category_attribute_dict = dict()
        self.attribute_enum_dict = dict()
        self.load_attribute_criteria()
        self.clean_attribute_list()
        self.load_attribute_enums()
        self.category_list: list[str] = list(self.category_attribute_dict.keys())

    def clean_attribute_list(self):
        self.attribute_type_list = [str(attr).strip('*').lstrip().rstrip().lower().replace(' ', '_') for attr in self.attribute_type_list]

    def load_attribute_enums(self):
        for attr in self.attribute_type_list:
            if attr in BLACK_LIST_ATTRIBUTES:
                continue
            enum_path = os.path.join(ENUM_DIR, attr + ".json")
            if not os.path.isfile(enum_path):
                print(f"{enum_path} not found")
                continue
            with open(enum_path, "r") as enum_file:
                json_attr = json.load(enum_file)
                if attr != "colour":
                    self.attribute_enum_dict[attr] = json_attr[attr]
                else:
                    self.attribute_enum_dict[attr] = []
                    for colour_name, _ in json_attr[attr]:
                        self.attribute_enum_dict[attr].append(colour_name)


    def load_attribute_criteria(self):
        df = pd.read_csv(TAXONOMY_FILE_PATH, skiprows=1)
        self.attribute_type_list = list(df.columns)[1:] #ignore the category column still need to clean each
        for _, row in df.iterrows():
            category_name = ""
            for attr_col_name, attr_value in row.items():
                if category_name == "":
                    self.category_attribute_dict[attr_value] = dict()
                    category_name = attr_value
                else:
                    clean_attr_col_name = str(attr_col_name).strip('*').strip().lower().replace(' ', '_')
                    if clean_attr_col_name == "comments":
                        continue
                    if pd.isna(attr_value):
                        self.category_attribute_dict[category_name][clean_attr_col_name] = "NA"
                    else:
                        self.category_attribute_dict[category_name][clean_attr_col_name] = str(attr_value)

    def generate_random_cateogry(self):
        return random.choice(self.category_list)

    def create_item(self) -> dict:
        item_dict = {}
        item_dict["id"] = str(uuid4())
        item_dict["price"] = random.randint(PRICE_MIN, PRICE_MAX)
        item_dict["category_id"] = self.generate_random_cateogry()
        item_dict["fulfillment_id"] = random.choice([1, 2])
        item_dict["tags"] = dict()
        self.create_item_tags(item_dict["tags"], item_dict["category_id"])
        return item_dict

    def create_item_tags(self, item_dict: dict, category_name: str):
        item_dict["code"], item_dict["list"] = "attribute", [] # list[index] = {"code": attribute_name, "value": attribute_value}
        def create_tag(attr_code):
            return {"code": attr_code, "value": random.choice(self.attribute_enum_dict[attr_code])}
        for attr_name, attr_type in self.category_attribute_dict[category_name].items():
            if attr_type == "NA":
                continue
            if attr_name in ["weight", "length", "breadth", "height"]: # column can be filled with a random integer
                item_dict["list"].append({"code": attr_name, "value": random.randint(DIMENSION_MIN, DIMENSION_MAX)})
            elif attr_name in self.attribute_enum_dict:
                item_dict["list"].append(create_tag(attr_name))
            else: 
                continue # neither it's a integer column and niether enums are available, need to fixed by protocol managers

