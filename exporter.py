#!/usr/bin/env python3

from __future__ import absolute_import
import prometheus_client
import time
import sys
import os
import nmap
import logging

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
            file_name = os.getenv('SCAN_FILE', '/app/portscanip.nmap')
            try:
                with open(file_name, 'r') as f:
                    targets = f.read().replace("\n", " ").strip()
                    logger.info("Loaded scan targets from %s", file_name)
            except OSError as e:
                logger.error("Could not open/read file %s: %s", file_name, str(e))
                sys.exit(1)

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

