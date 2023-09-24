#!/usr/bin/env python3

from __future__ import absolute_import
import time
import sys
import os
import nmap
import logging
from modules.ip_fetcher import fetch_azure_ips, fetch_ips_from_file
from modules.prometheus_format import expose_nmap_scan_results, expose_nmap_scan_stats, start_prometheus_server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
                required_env_vars = ['TARGET_FILE']
                missing_vars = [var for var in required_env_vars if os.getenv(var) is None]
                
                if missing_vars:
                    # Handle the case where some Azure environment variables are missing
                    error_message = f"The following environment variables are missing: {', '.join(missing_vars)}"
                    raise EnvironmentError(error_message)
                else:
                    target_file = os.getenv('TARGET_FILE', '/app/portscanip.nmap')
                    targets = fetch_ips_from_file(target_file)

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
                    
                    # Use the function from the modules directory
                    azure_targets = fetch_azure_ips(client_id, client_secret, tenant_id, subscription_id)
                    # space seperated string
                    print(azure_targets)
                    targets = " ".join(azure_targets)

            else:
                # Handle the case when the target source is neither "file" nor "azure"
                logger.error("Invalid target source specified: %s", target_source)
                # Exit with an error code
                sys.exit(1)

            logger.info("Scanning targets: %s", targets)
            try:
                nm.scan(targets)
                expose_nmap_scan_results(nm)
                expose_nmap_scan_stats(nm)
                logger.info("Scan completed successfully")
            except nmap.nmap.PortScannerError as e:
                logger.error("Nmap scan failed: %s", str(e))

            scan_frequency = float(os.getenv('SCAN_FREQUENCY', '36000'))
            logger.info("Sleeping for %s seconds", scan_frequency)
            time.sleep(scan_frequency)

    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Exiting.")
        # Exit gracefully
        sys.exit(0)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))

if __name__ == '__main__':
    # Pass the desired port as an argument when calling the function
    EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '9808'))
    start_prometheus_server(EXPORTER_PORT)
    main()
