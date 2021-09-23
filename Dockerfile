FROM centos/python-36-centos7

WORKDIR /FrexT

COPY requirements.txt /FrexT/requirements.txt
RUN ["pip", "install", "-r", "requirements.txt"]
