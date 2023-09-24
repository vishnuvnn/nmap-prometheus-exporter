#!/usr/bin/env python3

from __future__ import absolute_import
import prometheus_client
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
def expose_nmap_scan_results(nm):
    list_scanned_items = []

    for line in str(nm.csv()).splitlines():
        list_scanned_items.append(line)

    for line in list_scanned_items[1:]:
        host, _, _, prot, port, name, _, prod, *_ = line.split(";")
        metric_results.labels(host, prot, name, prod).set(float(port))

# Exposes stats of the scan in Prometheus format
def expose_nmap_scan_stats(nm):
    scanstats = nm.scanstats()
    metric_info.info({"time_elapsed": scanstats["elapsed"],
                      "uphosts": scanstats["uphosts"],
                      "downhosts": scanstats["downhosts"],
                      "totalhosts": scanstats["totalhosts"]})
    
def start_prometheus_server(exporter_port):
    prometheus_client.start_http_server(exporter_port)
    print(f"Prometheus HTTP server started on port {exporter_port}")
