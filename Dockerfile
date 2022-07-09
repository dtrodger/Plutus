# Python base image
FROM 642030467107.dkr.ecr.us-west-1.amazonaws.com/python

# Set working directory
WORKDIR /usr/src/app

# Set required env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/src/app

# Copy project into image
COPY . .

# Install pip and requirements
RUN pip install --upgrade pip && pip install -r requirements.txt
