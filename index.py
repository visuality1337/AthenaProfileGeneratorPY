import requests
import json
import os
import math
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('athena_generator.log')
    ]
)
logger = logging.getLogger(__name__)

FIXED_BACKEND_VALUES = {
    "AthenaEmoji": "AthenaDance",
    "AthenaSpray": "AthenaDance",
    "AthenaToy": "AthenaDance",
    "AthenaPetCarrier": "AthenaBackpack",
    "AthenaPet": "AthenaBackpack",
    "SparksDrum": "SparksDrums",
    "SparksMic": "SparksMicrophone"
}

def create_template_if_not_exists(template_path: str) -> dict:
    """Create athena_template.json if it doesn't exist and return its contents."""
    if not os.path.exists(template_path):
        logger.warning(f"{template_path} not found. Creating default template.")
        default_template = {"items": {}}
        try:
            with open(template_path, 'w') as f:
                json.dump(default_template, f, indent=2)
            logger.info(f"Created default {template_path}")
        except Exception as e:
            logger.error(f"Failed to create {template_path}: {str(e)}")
            raise
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {template_path}: {str(e)}")
        raise

def get_file_size(bytes_size: int) -> str:
    """Convert bytes to human-readable file size."""
    sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    if bytes_size == 0:
        return "N/A"
    i = int(math.floor(math.log(bytes_size) / math.log(1024)))
    if i == 0:
        return f"{bytes_size} {sizes[i]}"
    return f"{(bytes_size / math.pow(1024, i)):.1f} {sizes[i]}"

def main():
    logger.info("Fortnite Athena Profile Generator by visuality1337")
    logger.info("Starting generation process...")

    template_path = Path(__file__).parent / "athena_template.json"
    output_path = Path(__file__).parent / "athena.json"

    try:
        athena = create_template_if_not_exists(template_path)
    except Exception as e:
        logger.error(f"Template initialization failed: {str(e)}")
        return

    # officer...
    try:
        logger.info("Fetching cosmetics data from Fortnite API...")
        response = requests.get("https://fortnite-api.com/v2/cosmetics")
        response.raise_for_status()
        data = response.json()['data']
        logger.info("Successfully fetched cosmetics data")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch cosmetics data: {str(e)}")
        return

    # processing the officer
    processed_items = 0
    for mode in data.keys():
        if mode in ["lego", "beans"]:
            logger.info(f"Skipping mode: {mode}")
            continue

        logger.info(f"Processing mode: {mode}")
        for item in data[mode]:
            if "random" in item["id"].lower():
                logger.debug(f"Skipping random item: {item['id']}")
                continue

            if mode == "tracks":
                item["type"] = {"backendValue": "SparksSong"}

            backend_value = item["type"]["backendValue"]
            if backend_value in FIXED_BACKEND_VALUES:
                item["type"]["backendValue"] = FIXED_BACKEND_VALUES[backend_value]
                logger.debug(f"Fixed backend value for {item['id']}: {backend_value} -> {item['type']['backendValue']}")

            item_id = f"{item['type']['backendValue']}:{item['id']}"

            variants = []
            if item.get("variants"):
                for obj in item["variants"]:
                    variant_data = {
                        "channel": obj.get("channel", ""),
                        "active": obj.get("options", [{}])[0].get("tag", ""),
                        "owned": [variant.get("tag", "") for variant in obj.get("options", [])]
                    }
                    variants.append(variant_data)

            athena["items"][item_id] = {
                "templateId": item_id,
                "attributes": {
                    "max_level_bonus": 0,
                    "level": 1,
                    "item_seen": True,
                    "xp": 0,
                    "variants": variants,
                    "favorite": False
                },
                "quantity": 1
            }
            processed_items += 1
            if processed_items % 100 == 0:
                logger.info(f"Processed {processed_items} items")

    try:
        with open(output_path, 'w') as f:
            json.dump(athena, f, indent=2)
        file_stats = os.stat(output_path)
        logger.info(f"Successfully generated and saved to {output_path} ({get_file_size(file_stats.st_size)})")
        logger.info(f"Total items processed: {processed_items}")
    except Exception as e:
        logger.error(f"Failed to save athena.json: {str(e)}")

if __name__ == "__main__":
    main()