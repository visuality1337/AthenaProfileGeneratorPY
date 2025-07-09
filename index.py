import requests
import json
import os
import math
import logging
from pathlib import Path
import yaml
import time
from datetime import datetime, timedelta
import shutil

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file {config_path} not found")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_path}: {str(e)}")
        raise

def configure_logging(config):
    log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
    handlers = []
    if config.get('log_to_console', True):
        handlers.append(logging.StreamHandler())
    if config.get('log_file'):
        handlers.append(logging.FileHandler(config['log_file']))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

FIXED_BACKEND_VALUES = {
    "AthenaEmoji": "AthenaDance",
    "AthenaSpray": "AthenaDance",
    "AthenaToy": "AthenaDance",
    "AthenaPetCarrier": "AthenaBackpack",
    "AthenaPet": "AthenaBackpack",
    "SparksDrum": "SparksDrums",
    "SparksMic": "SparksMicrophone"
}

def create_template_if_not_exists(template_path: str, config: dict) -> dict:
    """Create athena_template.json if it doesn't exist and return its contents."""
    if not os.path.exists(template_path) or config.get('overwrite_template', False):
        logger.warning(f"{template_path} not found or overwrite enabled. Creating default template.")
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

def validate_json(data: dict) -> bool:
    """Validate JSON data."""
    try:
        json.dumps(data)
        return True
    except ValueError as e:
        logger.error(f"JSON validation failed: {str(e)}")
        return False

def check_cache(config: dict) -> dict:
    """Check if cached API response exists and is valid."""
    cache_file = config.get('cache_file', 'cosmetics_cache.json')
    cache_expiry_hours = config.get('cache_expiry_hours', 24)
    
    if not config.get('cache_api_response', False) or not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - cache_time < timedelta(hours=cache_expiry_hours):
            logger.info(f"Using cached API response from {cache_file}")
            return cached['data']
        else:
            logger.info(f"Cache expired for {cache_file}")
            return None
    except Exception as e:
        logger.error(f"Failed to read cache: {str(e)}")
        return None

def save_cache(data: dict, config: dict):
    """Save API response to cache."""
    if not config.get('cache_api_response', False):
        return
    
    cache_file = config.get('cache_file', 'cosmetics_cache.json')
    try:
        with open(cache_file, 'w') as f:
            json.dump({'data': data}, f, indent=2)
        logger.info(f"Saved API response to cache: {cache_file}")
    except Exception as e:
        logger.error(f"Failed to save cache: {str(e)}")

def fetch_cosmetics(config: dict) -> dict:
    """Fetch cosmetics data with retries."""
    cached_data = check_cache(config)
    if cached_data:
        return cached_data

    url = config.get('api_url', 'https://fortnite-api.com/v2/cosmetics')
    timeout = config.get('timeout', 30)
    retries = config.get('retry_attempts', 3)
    retry_delay = config.get('retry_delay', 2)

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching cosmetics data (attempt {attempt}/{retries})...")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()['data']
            save_cache(data, config)
            logger.info("Successfully fetched cosmetics data")
            return data
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt} failed: {str(e)}")
            if attempt == retries:
                logger.error("Max retries reached. Aborting.")
                raise
            time.sleep(retry_delay)

def main():
    logger.info("Fortnite Athena Profile Generator by visuality1337)")
    
    try:
        config = load_config()
    except Exception:
        return
    
    configure_logging(config)
    logger.info("Starting generation process...")

    output_dir = Path(config.get('output_directory', '.')).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    template_path = output_dir / config.get('template_file', 'athena_template.json')
    output_path = output_dir / config.get('output_file', 'athena.json')

    try:
        athena = create_template_if_not_exists(template_path, config)
    except Exception:
        return

    try:
        data = fetch_cosmetics(config)
    except Exception:
        return

    processed_items = 0
    max_items = config.get('max_items', 0)
    skip_modes = config.get('skip_modes', ['lego', 'beans'])
    include_types = config.get('include_types', [])
    exclude_types = config.get('exclude_types', [])
    min_rarity = config.get('min_rarity', '').lower()

    for mode in data.keys():
        if mode in skip_modes:
            logger.info(f"Skipping mode: {mode}")
            continue

        logger.info(f"Processing mode: {mode}")
        for item in data[mode]:
            if config.get('exclude_random_items', True) and "random" in item["id"].lower():
                logger.debug(f"Skipping random item: {item['id']}")
                continue

            if mode == "tracks":
                item["type"] = item.get("type", {"backendValue": "SparksSong"})
            elif "type" not in item:
                logger.warning(f"Item {item.get('id', 'unknown')} in mode {mode} missing 'type' key. Skipping.")
                continue

            backend_value = item["type"].get("backendValue")
            if not backend_value:
                logger.warning(f"Item {item.get('id', 'unknown')} in mode {mode} has no backendValue. Skipping.")
                continue

            if include_types and backend_value not in include_types:
                continue
            if backend_value in exclude_types:
                continue

            if min_rarity and item.get('rarity', {}).get('value', '').lower() < min_rarity:
                continue

            if backend_value in FIXED_BACKEND_VALUES:
                item["type"]["backendValue"] = FIXED_BACKEND_VALUES[backend_value]
                logger.debug(f"Fixed backend value for {item['id']}: {backend_value} -> {item['type']['backendValue']}")

            item_id = f"{item['type']['backendValue']}:{item['id']}"

            variants = []
            if config.get('include_variants', True) and item.get("variants"):
                for obj in item["variants"]:
                    variant_data = {
                        "channel": obj.get("channel", ""),
                        "active": obj.get("options", [{}])[0].get("tag", "") if config.get('variant_default_active', True) else "",
                        "owned": [variant.get("tag", "") for variant in obj.get("options", [])]
                    }
                    variants.append(variant_data)

            athena["items"][item_id] = {
                "templateId": item_id,
                "attributes": {
                    "max_level_bonus": 0,
                    "level": config.get('default_level', 1),
                    "item_seen": True,
                    "xp": config.get('default_xp', 0),
                    "variants": variants,
                    "favorite": config.get('mark_all_favorite', False)
                },
                "quantity": 1
            }
            processed_items += 1
            if max_items > 0 and processed_items >= max_items:
                logger.info(f"Reached max items limit: {max_items}")
                break
            if processed_items % config.get('batch_size', 100) == 0:
                logger.info(f"Processed {processed_items} items")
        if max_items > 0 and processed_items >= max_items:
            break

    if config.get('validate_json', True) and not validate_json(athena):
        return

    if config.get('backup_output', True) and output_path.exists():
        try:
            backup_path = output_path.with_suffix(config.get('backup_suffix', '.bak'))
            shutil.copy2(output_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {str(e)}")

    try:
        with open(output_path, 'w') as f:
            json.dump(athena, f, indent=2 if config.get('pretty_print', True) else None)
        file_stats = os.stat(output_path)
        logger.info(f"Successfully generated and saved to {output_path} ({get_file_size(file_stats.st_size)})")
        logger.info(f"Total items processed: {processed_items}")
    except Exception as e:
        logger.error(f"Failed to save {output_path}: {str(e)}")

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()