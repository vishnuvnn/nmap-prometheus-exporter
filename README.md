<h1 align="center">
  <img src="logo.png" alt="nmap-prometheus-exporter Logo" width="150" />
</h1>

# nmap-prometheus-exporter

**Description**:

This Docker application sets up the Nmap Prometheus Exporter, a versatile Python utility designed to scan and monitor network hosts and services using Nmap. It exposes the scan results and statistics in a Prometheus-compatible format. This exporter helps network administrators and DevOps teams gain insights into their network infrastructure, making it easier to detect changes, assess security, and maintain network health.

**Key Features**:

-   **Dockerized**: Easily deploy the Nmap Prometheus Exporter as a Docker container.
-   **Cross-Platform**: Platform-independent codebase ensuring compatibility with various operating systems.
-   **Automated Scanning**: Regularly scans a list of target IP addresses by dynamically fetching from Azure or a file.
-   **Prometheus Integration**: Exposes scan results and statistics as Prometheus metrics for easy monitoring and alerting.
-   **Customizable**: Easily configure the scan frequency, target file, and Prometheus port.
-   **Efficient**: Uses the Nmap library for efficient and comprehensive network scanning.
-   **Open Source**: Licensed under the MIT License for community contribution and collaboration.

## Prerequisites

Before running the Docker application, ensure you have the following prerequisites installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Usage

1. **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/your-username/nmap-prometheus-exporter.git
   ```

2.  **Navigate to the project directory**:
    
    
    `cd nmap-prometheus-exporter` 
    
3.  Create a `.env` file in the project directory with your environment variables. See the example in the `.env` section below.


4.  **Build the Docker image**:
    
    `docker-compose build` 
    
5.  **Start the Docker container**:
    
    `docker-compose up -d` 
    
6.  **Access Prometheus metrics** at `http://localhost:9808/metrics` (assuming you are running this on your local machine). Adjust the URL as needed based on your environment.
    
7.  To stop and remove the container, use the following command:
    
    
    `docker-compose down` 
    

### Environment Variables (`.env` file)

Create a `.env` file in the project directory with the following variables:

If the list of IPs needs to be fetched from `azure` :
Replace the placeholders (`your_azure_client_id`, `your_azure_client_secret`, `your_azure_tenant_id`, and `your_azure_subscription_id`) with your actual Azure credentials.

```bash
TARGET_SOURCE=azure
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
SCAN_FREQUENCY=36000
EXPORTER_PORT=9808
```

If the list of IPs need to be fetched from  `file` :
Uncomment volume mount part from `docker-compose.yml` & replace `/path/to/your/portscanip.nmap`

Where `portscanip.nmap` is line terminated list of IP addresses


```bash
TARGET_SOURCE=file
TARGET_FILE=/app/portscanip.nmap
SCAN_FREQUENCY=36000
EXPORTER_PORT=9808
```


## Adding Prometheus Target and Alert Rules

To monitor your `nmap-prometheus-exporter` instance effectively, you can configure Prometheus to scrape metrics from it and set up alert rules for potential issues. Here's how you can do it:

### Prometheus Target Configuration

1.  Edit your Prometheus configuration file, typically named `prometheus.yml`.
    
2.  Add a new job configuration under `scrape_configs` to specify the target to scrape metrics from your `nmap-prometheus-exporter` instance. Replace `<exporter-host>` with the hostname or IP address where your exporter is running and `<port>` with the configured port (default: 9808).
    
```yaml
    - job_name: nmap
      scrape_interval: 60s
      scrape_timeout: 30s
      metrics_path: "/metrics"
      static_configs:
      - targets: ['<exporter-host>:<port>']
        labels:
          cloud: CLOUD_NAME # Replace "CLOUD_NAME" with your cloud provider (aws, azure, gcp, or any other)
```
    
3.  Save the `prometheus.yml` file.
    
4.  Restart Prometheus to apply the changes.
    

### Alert Rules Configuration

To set up alert rules for your `nmap-prometheus-exporter`, follow these steps:

1.  Edit your Prometheus alerting rules file, typically named `alert.rules.yml`.
    
2.  Add your alerting rules to the file. Here's an example rule that alerts when the `nmap-exporter` service is down:
    

yamlCopy code
```yaml
`groups:
  - alert: awsNmapExporterDown
    expr: up{job="nmap"} == 0
    for: 1m
    labels:
      severity: Critical
      frequency: Daily
    annotations:
      summary: "Nmap Exporter is down (instance {{ $labels.instance_name }})"
      description: "Nmap Exporter is down\n VALUE = {{ $value }}\n for instance {{ $labels.instance_name }}"

  # Replace "CLOUD_NAME" with the one that was added with the target
  # Multiple alerts can men created for each cloud or ports
  - alert: Port22_CLOUD_NAME
    expr: nmap_scan_results{cloud="CLOUD_NAME"} == 22 
    labels:
      severity: Critical
      frequency: Daily
    annotations:
      summary: "Port 22 is open to the world on an instance in CLOUD_NAME with IP address {{ $labels.host }}"
      description: "Port 22 is open to the world on an instance in "CLOUD_NAME" with IP address {{ $labels.host }}"
``` 

3.  Save the `alert.rules.yml` file.
    
4.  Reload Prometheus to apply the new alert rules.
    

With these configurations in place, Prometheus will scrape metrics from your `nmap-prometheus-exporter`, and alerting rules will trigger alerts based on defined conditions. Customize the alerting rules to fit your monitoring needs.

### Generate Grafana Dashboard

To visualize the metrics collected by `nmap-prometheus-exporter` in Grafana, follow these steps:

1.  Open your web browser and navigate to your Grafana instance's URL.
    
2.  Log in to Grafana if you're not already logged in.
    
3.  Once logged in, click on the "Configuration" gear icon in the left sidebar.
    
4.  In the Configuration menu, click on "Data Sources."
    
5.  You should now see a list of data sources configured in your Grafana instance.
    
6.  Replace "YOUR_DS_NAME" with the Prometheus data source name where `nmap-prometheus-exporter`'s metrics are present in the following command:
    
    bashCopy code
    
    `DATASOURCE="YOUR_DS_NAME" ; sed "s/PROMETHEUS_DS_PLACEHOLDER/$DATASOURCE/g" dashboard_template.json` 
    
    Run the command from the repository's root directory to generate the Grafana dashboard for the metrics.
    
7.  You can import this JSON directly to Grafana as a dashboard.
    

### Importing Grafana Dashboard

1.  Log in to your Grafana instance if you're not already logged in.
    
2.  In the left sidebar, click on the "Create" (⨁) icon and select "Dashboard."
    
3.  On the new dashboard screen, click on "Import" in the upper right corner.
    
4.  You will be prompted to provide a Grafana.com Dashboard URL or JSON file. Since we generated a JSON file earlier, select "Upload .json File."
    
5.  Click on "Upload .json File," and then choose the JSON file generated from the previous step (usually named `nmap-exporter-dashboard.json`).
    
6.  After selecting the JSON file, click "Open" or "Upload" to proceed.
    
7.  Grafana will automatically parse the JSON file and create a new dashboard based on the configuration.
    
8.  Once the dashboard is imported, you can customize it further by adding additional panels, modifying queries, or adjusting the layout to suit your monitoring needs.
    
9.  Save the dashboard by clicking on the floppy disk icon or by pressing `Ctrl + S` (or `Cmd + S` on macOS).
    
10.  Finally, you can access and view your newly imported dashboard from the Grafana home screen or the dashboard list.
    

Now you have successfully imported the Grafana dashboard that visualizes the metrics collected by the `nmap-prometheus-exporter` into your Grafana instance.

Remember to adapt the configuration to your specific environment and requirements.

## License

This project is licensed under the MIT License - see the [LICENSE](https://chat.openai.com/c/LICENSE) file for details.

## Acknowledgments

-   [Nmap](https://nmap.org/) - The network scanner used for scanning.
-   [Prometheus](https://prometheus.io/) - The monitoring and alerting toolkit.
-   [Docker](https://www.docker.com/) - The containerization platform.
-   [Docker Compose](https://docs.docker.com/compose/) - The tool for defining and running multi-container Docker applications.
-   [Grafana](https://grafana.com/) - The visualization and monitoring platform.

**Logo Credit:** The logo design used in this project was crafted with the assistance of [LogoMakr.com/app](https://logomakr.com/app). We appreciate the creative support from LogoMakr in shaping our visual identity.
