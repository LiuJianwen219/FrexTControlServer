FROM centos/python-36-centos7

COPY requirements.txt /tmp
RUN ["pip", "install", "-r", "/tmp/requirements.txt"]

# copy source
COPY ./ /FrexT

# port
EXPOSE 8040

# workdir
WORKDIR /FrexT

# start
ENTRYPOINT ["python", "main.py"]
