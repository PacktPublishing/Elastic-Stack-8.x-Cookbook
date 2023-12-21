FROM python:3.10-slim as base

# Install gcc and python3-dev for building certain Python packages
RUN apt-get update && apt-get install -y gcc python3-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /favoriteservice


# Add the application
COPY . .

EXPOSE 5000
ENTRYPOINT [ "python", "main.py" ]