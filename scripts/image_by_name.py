import asyncio
import json
import os
from pathlib import Path

import aiohttp
import unidecode
from tqdm import tqdm

D2O_FOLDER = os.path.join(Path(__file__).parent.parent, "output", "d2o")
D2O_ITEM_PATH = os.path.join(D2O_FOLDER, "Items.json")

D2I_PATH = os.path.join(Path(__file__).parent.parent, "output", "d2i.json")


def clean_item_name(name: str) -> str:
    return (
        unidecode.unidecode(name, "utf-8")
        .replace(" ", "_")
        .replace(".", "")
        .replace("'", "_")
        .replace("-", "_")
        .lower()
    )


async def get_image_from_icon_id_encyclopedia(
    session: aiohttp.ClientSession, name: str, icon_id: int
):
    IMG_FOLDER = os.path.join(Path(__file__).parent, "images")
    async with session.get(
        f"https://static.ankama.com/dofus/www/game/items/200/{icon_id}.png"
    ) as result:
        if result.status == 200:
            with open(
                os.path.join(IMG_FOLDER, f"{clean_item_name(name)}.png"), mode="wb"
            ) as file:
                file.write(await result.read())


def get_all_item_icon_id(items: list[dict], d2i_texts: dict) -> list[tuple[int, str]]:
    icon_id_by_names: list[tuple[int, str]] = []

    d2i_lookup = {int(key): value for key, value in d2i_texts.items()}

    for item in tqdm(items):
        name: str = d2i_lookup[item["nameId"]]
        icon_id_by_names.append((item["iconId"], name))
    return icon_id_by_names


async def fetch_all(session, icon_id_by_names: list[tuple[int, str]]):
    tasks = []
    for icon_id, name in icon_id_by_names:
        task = asyncio.create_task(
            get_image_from_icon_id_encyclopedia(session, name, icon_id)
        )
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res


async def main():
    with open(D2O_ITEM_PATH, encoding="utf8") as d2o_item_file, open(
        D2I_PATH, encoding="utf8"
    ) as d2i_file:
        items: list[dict] = json.load(d2o_item_file)
        d2i_texts = json.load(d2i_file)["texts"]
        icon_id_with_name = get_all_item_icon_id(items, d2i_texts)

    async with aiohttp.ClientSession() as session:
        await fetch_all(session, icon_id_with_name[:50])


if __name__ == "__main__":
    asyncio.run(main())
