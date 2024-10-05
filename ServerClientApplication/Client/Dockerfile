FROM ubuntu:22.04

# Update the package list and install Python and necessary tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip \
    linux-tools-common linux-tools-generic \
    linux-tools-6.8.0-45-generic linux-cloud-tools-6.8.0-45-generic && \
    apt-get clean

# Create a symlink for python if necessary
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory
WORKDIR /Client

# Copy the current directory contents into the container at /Client
COPY . /Client

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt install -y sudo
 


# Expose port 5000 for Flask app
EXPOSE 5000

# Set the default command to run your Python script
CMD ["python", "client.py"]
