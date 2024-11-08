Power Consumption Monitoring System - User Guide
Overview

The Power Consumption Monitoring System is designed to monitor and record power consumption of a specified application, consisting of both client and server components. The client collects power usage data and sends it to the server for further processing, storage, and visualization.
Deployment Steps
Prerequisites

    Python 3: Ensure that Python 3 is installed on both the client and server machines.
    Scaphandre: Install Scaphandre on the client machine to handle power consumption data collection.
    Flask: Install Flask on both the client and server for running the API.

Installation Steps
Step 1: Clone the Repository

Clone the project repository to both client and server systems.



    git clone https://github.com/aweSAM12/power-analysis-tool.git
    cd https://github.com/aweSAM12/power-analysis-tool.git

Step 2: Install Dependencies

Install the necessary dependencies for both client and server applications:
    
    pip install -r requirements.txt

Step 3: Configure Client

    Update client_helper.py:
        Modify the CLIENT_NAME variable to provide a unique identifier for each client, especially if you are deploying multiple clients.

    Set Monitoring Parameters (optional):
        In client.py, specify the default values for command, frequency, timeout, and server_url, or provide these when making API calls.

Step 4: Run the Client Application

To start monitoring power consumption on the client:

    python3 client.py

This will initialize the PowerConsumptionMonitor and make the client ready to receive API calls for starting monitoring.
Step 5: Run the Server Application

Start the server to handle client uploads, data management, and data visualization:

    python3 server.py

Step 6: Access Endpoints

Server Application

    Endpoints for Data Management:
        <server-url:5001>/ : Trigger client-side monitoring.
        <server-url:5001>/plot: Generates visualizations.

Notes

    Ensure network connectivity between client and server for successful data uploads.
    Log files for both client and server applications are generated for troubleshooting and monitoring system performance.


