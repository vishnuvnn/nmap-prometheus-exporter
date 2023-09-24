#!/usr/bin/env python3

from __future__ import absolute_import
import prometheus_client
import time
import sys
import os
import nmap
import logging
from modules.azure_ip_fetcher import fetch_azure_ips

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Prometheus metrics without clearing them
metric_results = prometheus_client.Gauge("nmap_scan_results",
                                         "Holds the scanned result",
                                         ["host",
                                          "protocol",
                                          "name",
                                          "product_detected"])
metric_info = prometheus_client.Info("nmap_scan_stats",
                                     "Holds details about the scan")

def read_targets_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            targets = f.read().strip().split("\n")
        return targets
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading targets from file: {str(e)}")
        return []

# Exposes results of the scan in Prometheus format
def nmap_scan_results(nm):
    list_scanned_items = []

    for line in str(nm.csv()).splitlines():
        list_scanned_items.append(line)

    for line in list_scanned_items[1:]:
        host, _, _, prot, port, name, _, prod, *_ = line.split(";")
        metric_results.labels(host, prot, name, prod).set(float(port))

# Exposes stats of the scan in Prometheus format
def nmap_scan_stats(nm):
    scanstats = nm.scanstats()
    metric_info.info({"time_elapsed": scanstats["elapsed"],
                      "uphosts": scanstats["uphosts"],
                      "downhosts": scanstats["downhosts"],
                      "totalhosts": scanstats["totalhosts"]})

# Main function
def main():
    try:
        # Print logo
        with open('ascii_logo.txt', 'r') as file:
            # Read and print the content
            content = file.read()
            print(content)

        nm = nmap.PortScanner()

        while True:
            # Fetch targets based on the selected source
            target_source = os.getenv('TARGET_SOURCE', 'file')

            if target_source == "file":
                target_file = os.getenv('TARGET_FILE', '/app/portscanip.nmap')
                targets = read_targets_from_file(target_file)
            elif target_source == "azure":
                required_env_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_SUBSCRIPTION_ID']
                missing_vars = [var for var in required_env_vars if os.getenv(var) is None]

                if missing_vars:
                    # Handle the case where some Azure environment variables are missing
                    error_message = f"The following Azure environment variables are missing: {', '.join(missing_vars)}"
                    raise EnvironmentError(error_message)
                else:
                    client_id = os.getenv('AZURE_CLIENT_ID')
                    client_secret = os.getenv('AZURE_CLIENT_SECRET')
                    tenant_id = os.getenv('AZURE_TENANT_ID')
                    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
                    
                    # Create a ClientSecretCredential for authentication
                    credential = ClientSecretCredential(
                        client_id=client_id,
                        client_secret=client_secret,
                        tenant_id=tenant_id
                    )
                    
                    # Use the function from the modules directory
                    azure_targets = fetch_azure_ips(credential, subscription_id)
                    # space seperated string
                    targets = " ".join(azure_targets)

            else:
                # Handle the case when the target source is neither "file" nor "azure"
                logger.error("Invalid target source specified: %s", target_source)
                sys.exit(1)  # Exit with an error code

            logger.info("Scanning targets: %s", targets)
            try:
                nm.scan(targets)
                nmap_scan_results(nm)
                nmap_scan_stats(nm)
                logger.info("Scan completed successfully")
            except nmap.nmap.PortScannerError as e:
                logger.error("Nmap scan failed: %s", str(e))

            scan_frequency = float(os.getenv('SCAN_FREQUENCY', '36000'))
            logger.info("Sleeping for %s seconds", scan_frequency)
            time.sleep(scan_frequency)

    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Exiting.")
        sys.exit(0)  # Exit gracefully
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))

if __name__ == '__main__':
    prometheus_client.start_http_server(int(os.getenv('EXPORTER_PORT', '9808')))
    main()
