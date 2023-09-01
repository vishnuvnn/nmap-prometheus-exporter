![Project Logo](logo.png)

**Description**:

This Docker application sets up the Nmap Prometheus Exporter, a versatile Python utility designed to scan and monitor network hosts and services using Nmap. It exposes the scan results and statistics in Prometheus-compatible format. This exporter helps network administrators and DevOps teams gain insights into their network infrastructure, making it easier to detect changes, assess security, and maintain network health.

**Key Features**:

-   **Dockerized**: Easily deploy the Nmap Prometheus Exporter as a Docker container.
-   **Cross-Platform**: Platform-independent codebase ensuring compatibility with various operating systems.
-   **Automated Scanning**: Regularly scans a list of target IP addresses defined in the `portscanip.nmap` file.
-   **Prometheus Integration**: Exposes scan results and statistics as Prometheus metrics for easy monitoring and alerting.
-   **Customizable**: Easily configure the scan frequency, target file, and Prometheus port.
-   **Efficient**: Uses the Nmap library for efficient and comprehensive network scanning.
-   **Open Source**: Licensed under [LICENSE_NAME] for community contribution and collaboration.

## Prerequisites

Before running the Docker application, ensure you have the following prerequisites installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)


## Usage

1. 📥 **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/your-username/nmap-prometheus-exporter.git` 

2.  📂 **Navigate to the project directory**:
    
    bashCopy code
    
    `cd nmap-prometheus-exporter` 
    
3.  ✍️ Create a `portscanip.nmap` file in the project directory with a list of target IP addresses to scan.
    
4.  🛠️ Customize the scanning parameters and frequency by modifying the `docker-compose.yml` file:
    
    -   `FILE_PATH`: Path to the `portscanip.nmap` file inside the container.
    -   `PORT`: Port to expose Prometheus metrics.
    -   `FREQUENCY`: Frequency of Nmap scans in seconds.
5.  🏗️ **Build the Docker image**:
    
    bashCopy code
    
    `docker-compose build` 
    
6.  ▶️ **Start the Docker container**:
    
    bashCopy code
    
    `docker-compose up -d` 
    
7.  🖥️ **Access Prometheus metrics** at `http://localhost:9808/metrics` (assuming you are running this on your local machine). Adjust the URL as needed based on your environment.
    
8.  🛑 To stop and remove the container, use the following command:
    
    bashCopy code
    
    `docker-compose down`    
7.  **Access Prometheus metrics** at `http://localhost:9808/metrics` (assuming you are running this on your local machine). Adjust the URL as needed based on your environment.
    
8.  To stop and remove the container, use the following command:
    
    bashCopy code
    
    `docker-compose down`
    

## Environment Variables

You can customize the scanning parameters by modifying the environment variables in the `docker-compose.yml` file:

-   `FILE_PATH`: Path to the `portscanip.nmap` file inside the container.
-   `PORT`: Port to expose Prometheus metrics.
-   `FREQUENCY`: Frequency of Nmap scans in seconds.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

-   [Nmap](https://nmap.org/) - The network scanner used for scanning.
-   [Prometheus](https://prometheus.io/) - The monitoring and alerting toolkit.
-   [Docker](https://www.docker.com/) - The containerization platform.
-   [Docker Compose](https://docs.docker.com/compose/) - The tool for defining and running multi-container Docker applications.

Feel free to modify this `README.md` to include more specific instructions or information about your application.
