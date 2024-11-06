Power Consumption Monitoring System
Overview

This system comprises a client application and a server application designed to monitor and record power consumption of a specified application. The client collects power consumption data and sends it to the server, which processes and stores the data, allowing for further analysis and visualization.
Components


1. Client Application
PowerConsumptionMonitor Class

    Purpose: Handles the power consumption monitoring using the Scaphandre tool.

    Attributes:

        command: The command to execute the monitored application.

        frequency: Frequency of sampling in milliseconds.

        timeout: Timeout for the monitoring process in seconds.

        server_url: URL where the CSV file will be uploaded.

    Methods:

        __init__: Initializes the monitoring object with command, frequency, timeout, and server_url.

        setup_logging: Configures the logging settings.

        clear_csv: Clears the CSV file.

        write_to_csv: Appends power consumption data to the CSV file.

        extract_app_name: Extracts the application name from the command.

        start_scaphandre_monitoring: Executes the monitoring command and processes the output.

        upload_csv: Uploads the CSV file to the specified server.

Flask Web API

    Purpose: Provides an endpoint to start the monitoring process.

    Endpoint: /start_monitoring

        Method: POST

        Parameters:

            command: The command to execute for monitoring.

            frequency: Frequency of sampling.

            timeout: Timeout for monitoring.

            server_url: URL to upload the CSV.

Run Command - python3 client.py 

<!-- Note
in file client_helper.py ,
variable CLIENT_NAME is hardcoded currently , if using multile clients use unique names for all the clients
 -->

2. Server Flask Application  

    Purpose: Provides various endpoints to interact with the monitoring system and manage data.

    Endpoints:

        /start_monitoring: Starts monitoring on the client side.

        /trigger_monitoring: Triggers monitoring with parameters sent in the request body.

        /upload_csv: Handles CSV uploads from the client.

        /get_data: Retrieves combined CSV data.

        /power: Queries power data based on specified parameters.

        /plot: Renders a plot based on the data.

CSVHandler Class (server_helper.py)

    Purpose: Manages CSV file operations, including saving, uploading, querying data, and parsing frequency.

Run Command - python3 server.py 



    
