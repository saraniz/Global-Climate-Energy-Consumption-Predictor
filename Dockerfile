# here we are using the official python image from the docker hub. we are using the slim version because it is smaller in size and it has only the necessary packages installed. we are also specifying the version of python as 3.10 because our application is compatible with this version.
FROM python:3.10-slim

# here we are setting the working directory to /app because we want to copy our files to this directory and run our application from this directory.
WORKDIR /app

# here we are installing the build-essential package because it is required to build some of the dependencies of our application. we are also removing the apt cache to reduce the size of our image.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# here this command end fullstop(.) because it say destination of current directory where we should copy the requirements.txt file. if we write requirements.txt then it will copy the file with name requirements.txt but if we write fullstop(.) then it will copy the file with same name as in our local system.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy all the files from our local system to the container. here we are copying all the files because we have only one file which is main.py but if we have more files then we can copy all the files at once.
COPY . .

# here we are exposing the port 8000 because our application will run on this port and we want to access it from outside the container.
EXPOSE 8000

# here we are using uvicorn to run our application. we are specifying the host as
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]