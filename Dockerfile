FROM debian:8

RUN apt-get -y update && apt-get -y install locales apt-utils

RUN export LANGUAGE=en_US.UTF-8 && \
    export LANG=en_US.UTF-8 && \
    export LC_ALL=en_US.UTF-8 && \
    locale-gen en_US.UTF-8 && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install git python=2.7.9-1

ADD . /PyBitmessage

ENV bm_api_host 0.0.0.0
ENV bm_api_port 8442
ENV bm_api_username bm-user
ENV bm_api_password placeholder

# Initialize keys.dat
RUN mkdir -p ~/.config/PyBitmessage/; \
  touch ~/.config/PyBitmessage/keys.dat; \
  chmod 0600 ~/.config/PyBitmessage/keys.dat; \
  python /PyBitmessage/src/bitmessagemain.py & sleep 3; \
  kill $!; \
  echo "daemon = true\n"\
"apienabled = true\n"\
"apiinterface = $bm_api_host\n"\
"apiport = $bm_api_port\n"\
"apiusername = $bm_api_username\n"\
"apipassword = $bm_api_password\n"\
    >>  ~/.config/PyBitmessage/keys.dat;

EXPOSE $bm_api_port
EXPOSE 8444

RUN ln -sf /dev/stdout /var/log/pybitmessage.log

ENTRYPOINT ["python","/PyBitmessage/src/bitmessagemain.py", ">> /var/log/pybitmessage.log 2>&1"]
