#!/usr/bin/env python3

from __future__ import absolute_import
import os
from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to fetch public IP addresses from file
def fetch_ips_from_file(file_path):
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

# Function to fetch public IP addresses from Azure
def fetch_azure_ips(client_id, client_secret, tenant_id, subscription_id):
    try:
        # Azure API URL for fetching public IP addresses
        azure_api_url = "https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Network/publicIPAddresses?api-version=2021-02-01"

        # Specify the scope for the Azure Management API
        scope = "https://management.azure.com/.default"

        # Create a ClientSecretCredential for authentication
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, scope=scope)

        # Create a SubscriptionClient to list all accessible subscriptions
        subscription_client = SubscriptionClient(credential)

        # Fetch a list of all subscriptions
        subscriptions = list(subscription_client.subscriptions.list())

        # Extract subscription IDs from the list
        subscription_ids = [subscription.subscription_id for subscription in subscriptions]


        # Azure API request headers
        headers = {
            "Authorization": f"Bearer {credential.get_token(scope).token}",  # Specify the scope here
            "Content-Type": "application/json"
        }

        all_ip_addresses = []

        for subscription_id in subscription_ids:
            # Make the API request to Azure Resource Manager
            response = requests.get(
                azure_api_url.format(subscription_id=subscription_id, resource_group=""),
                headers=headers
            )

            if response.status_code == 200:
                # Parse the JSON response to extract public IP addresses
                data = response.json()
                ip_addresses = []
    
                for ip_resource in data.get("value", []):
                    ip_address = ip_resource.get("properties", {}).get("ipAddress")
                    if ip_address:
                        ip_addresses.append(ip_address)
                # Add the IP addresses from the current subscription to the list
                all_ip_addresses.extend(ip_addresses)

            else:
                # Handle API request errors
                logger.error(f"Failed to fetch Azure public IP addresses. Status code: {response.status_code}")
                return []
        return all_ip_addresses
    except Exception as e:
        # Handle exceptions
        logger.error(f"Error fetching Azure public IP addresses: {str(e)}")
        return []

