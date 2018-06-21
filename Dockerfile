# A container for PyBitmessage daemon

FROM python:2.7-slim
WORKDIR /bitmessaged
ADD . /bitmessaged
RUN python2 setup.py install
EXPOSE 8444 8442
ENV BITMESSAGE_HOME /bitmessaged
CMD ["pybitmessage", "-d"]
