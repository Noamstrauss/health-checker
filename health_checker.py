import ruamel.yaml
import argparse
import sys
import json
from time import time, sleep
import requests
from loguru import logger
import pyfiglet
from urllib.parse import urlparse
from typing import List, Dict, Any

VERSION = "1.0"
LOOP_INTERVAL = 15


def load_config(file_path) -> List[Dict[str, Any]]:
    """
    Parse the YAML configuration file
    """
    try:
        yaml = ruamel.yaml.YAML(typ='safe', pure=True)

        with open(file_path, 'r') as stream:
            config = yaml.load(stream)

            logger.info(f"Successfully parsed configuration from {file_path}")
            return config

    except FileNotFoundError:
        logger.error(f"Error: Config file not found at path: {file_path}")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"Unexpected error reading config file: {exc}")
        sys.exit(1)


def domain_parser(url) -> str:
    """
    Extract the domain from a URL
    """

    domain = urlparse(url).netloc
    return domain


def http_request(endpoint: Dict[str, Any]) -> bool:
    """
    Send http request to check endpoint availability
    """

    start_time = time()
    try:
        response = requests.request(
            method=endpoint.get('method', 'GET'),
            url=endpoint['url'],
            headers=endpoint.get('headers', {}),
            json=json.loads(endpoint['body']) if endpoint.get('body') else None,
            timeout=0.5
        )
        latency = (time() - start_time) * 1000
        is_up = (200 <= response.status_code < 300) and (latency < 500)
        logger.debug(
            f"{endpoint.get('name', endpoint['url'])}: "
            f"status={response.status_code}, "
            f"latency={latency:.2f}ms, "
            f"up={is_up}"
        )

        return is_up
    except requests.RequestException as e:
        logger.error(f"Request failed for {endpoint['name']}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error for {endpoint.get('name', endpoint['url'])}: {e}")
        return False


def calculate_availability(results: Dict[str, List[bool]]) -> Dict[str, float]:
    """
    Calculate availability percentage for each domain
    """
    availability = {}
    for domain, checks in results.items():
        up_count = sum(checks)
        availability[domain] = round((up_count / len(checks)) * 100, 1)
    return availability


def main():
    welcome_banner = pyfiglet.figlet_format("HTTP Health Checker")
    print(welcome_banner)
    print(f"Version: {VERSION}\n")

    parser = argparse.ArgumentParser(description="HTTP endpoint health checker")
    parser.add_argument("-c", "--config_file_path", help="Path to the YAML configuration file", required=True, type=str)
    parser.add_argument("--log-level", help="Log level (default: INFO)", default="INFO", type=str, choices=["debug", "info", "warning", "error"],)
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}", level=args.log_level.upper())

    endpoints = load_config(args.config_file_path)
    logger.info(f"Loaded {len(endpoints)} endpoints")
    logger.info(f"Starting health check loop every {LOOP_INTERVAL} seconds...")
    logger.info("--------------------------------------------------------")

    domain_results = {}
    try:
        while True:
            for endpoint in endpoints:
                domain = domain_parser(endpoint['url'])

                if domain not in domain_results:
                    domain_results[domain] = []

                is_up = http_request(endpoint)
                domain_results[domain].append(is_up)

            availability = calculate_availability(domain_results)
            for domain, percentage in availability.items():
                logger.info(f"{domain} has {percentage}% availability percentage")
            logger.info("--------------------------------------------------------")

            sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Closing up shop..")


if __name__ == "__main__":
    main()
