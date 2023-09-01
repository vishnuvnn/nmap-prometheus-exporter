#!/usr/bin/env python

from __future__ import absolute_import, print_function
import argparse
import prometheus_client
import time
import sys
import nmap
import csv
import os

# Constants
DEFAULT_FILE_PATH = "portscanip.nmap"
DEFAULT_PORT = 9808
DEFAULT_FREQUENCY = 3600

# Function to read targets from a file
def read_targets(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip().replace("\n", " ")
    except OSError as e:
        print(f"Could not open/read file: {file_path}. Error: {e}")
        sys.exit(1)

# Exposes results of the scan in prometheus format
def nmap_scan_results(nm, metric_results):
    metric_results.clear()
    list_scanned_items = [line for line in csv.reader(nm.stdout.splitlines())]
    
    for item in list_scanned_items[1:]:
        host, _, _, prot, port, name, _, prod, *_ = item
        metric_results.labels(host, prot, name, prod).set(port)

# Exposes stats of the scan in prometheus format
def nmap_scan_stats(nm, metric_info):
    metric_info.clear()
    scanstats = nm.scanstats()
    metric_info.info({
        "time_elapsed": scanstats["elapsed"],
        "uphosts": scanstats["uphosts"],
        "downhosts": scanstats["downhosts"],
        "totalhosts": scanstats["totalhosts"]
    })

# Main function
def main(args):
    # Print logo
    with open('ascii_logo.txt', 'r') as file:
        # Read and print the content
        content = file.read()
        print(content)
    nm = nmap.PortScanner()
    
    while True:
        targets = read_targets(args.file)
        
        # Actual Nmap scan
        nm.scan(targets)
        nmap_scan_results(nm, metric_results)
        nmap_scan_stats(nm, metric_info)
        
        # To control scanning frequency
        time.sleep(args.frequency)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nmap Prometheus Exporter')
    parser.add_argument('-f', '--file', help=f'File with list of target IP addresses [default: {DEFAULT_FILE_PATH}]', metavar='filename', default=DEFAULT_FILE_PATH)
    parser.add_argument('-p', '--port', type=int, help=f'Port to expose metrics [default: {DEFAULT_PORT}]', metavar='port', default=DEFAULT_PORT)
    parser.add_argument('-c', '--frequency', type=int, help=f'Frequency of nmap scan in seconds [default: {DEFAULT_FREQUENCY}]', metavar='frequency', default=DEFAULT_FREQUENCY)
    args = parser.parse_args()
    
    metric_results = prometheus_client.Gauge("nmap_scan_results", "Holds the scanned result", ["host", "protocol", "name", "product_detected"])
    metric_info = prometheus_client.Info("nmap_scan_stats", "Holds details about the scan")
    
    prometheus_client.start_http_server(args.port)
    main(args)
