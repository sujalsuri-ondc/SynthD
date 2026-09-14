import random
import aiofiles
import json
from tqdm import tqdm
import asyncio
from fsearch import on_search
from pathlib import Path
import os
import pickle
import toml

CONFIG = dict()

def load_config():
    global CONFIG
    with open("config.toml", "r") as config:
        CONFIG = toml.load(config)

async def write_payload(path: str, payload: dict):
    serialized_data = pickle.dumps(payload)
    async with aiofiles.open(path, "wb+") as write_file:
        await write_file.write(serialized_data)

async def main():
    payload_generator = on_search.OnSearch(CONFIG["resources"]["TAXONOMY_FILE"], CONFIG["resources"]["ENUM_DIR"])
    save_path = os.path.join(CONFIG["resources"]["SAVE_DIR"], CONFIG["resources"]["CATEGORY_NAME"])
    Path(save_path).mkdir(parents=True, exist_ok=True)

    for i_snp in tqdm(range(CONFIG["constants"]["N_SNP"])):
        n_provider = random.randint(CONFIG["constants"]["N_PROVIDER_MIN"], CONFIG["constants"]["N_PROVIDER_MAX"])
        item_per_provider = [random.randint(CONFIG["constants"]["ITEM_PER_PROVIDER_MIN"], CONFIG["constants"]["ITEM_PER_PROVIDER_MAX"]) for _ in range(n_provider)]
        payload = payload_generator.create_payload(n_provider, item_per_provider)
        await write_payload(os.path.join(save_path, f"payload_{i_snp}.pkl"), payload)

def debug_file():
    with open(CONFIG["resources"]["DEBUG_FILE_PATH"], "rb") as f:
        data = pickle.load(f)
    with open("testfile.json", "w+") as f:
        json.dump(data, f)

if __name__ == "__main__":
    load_config()
    if len(CONFIG) != 0:
        if CONFIG["global"]["CREATE_DATASET"]:
            asyncio.run(main())
        if CONFIG["global"]["DEBUG_FILE"]:
            debug_file()
