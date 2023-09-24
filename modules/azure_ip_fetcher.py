import requests
import logging
from azure.identity import ClientSecretCredential  # Import from Azure SDK
from azure.mgmt.subscription import SubscriptionClient  # Import from Azure SDK

logger = logging.getLogger(__name__)

def fetch_azure_ips(credential, subscription_id):
    try:
        # Azure API endpoint for listing public IP addresses
        azure_api_url = "https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/publicIPAddresses?api-version=2020-12-01"

        # Azure API request headers
        headers = {
            "Authorization": f"Bearer {credential.get_token('https://management.azure.com').token}",
            "Content-Type": "application/json"
        }

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
            return ip_addresses
        else:
            # Handle API request errors
            logger.error(f"Failed to fetch Azure public IP addresses. Status code: {response.status_code}")
            return []
    except Exception as e:
        # Handle exceptions
        logger.error(f"Error fetching Azure public IP addresses: {str(e)}")
        return []
