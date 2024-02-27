#!/bin/bash

apt -y install curl jq ipvsadm

EXTIP=$(curl -s telnetmyip.com|jq -r .ip)
THREADS=$(nproc --all)
echo "THREADS=$THREADS" > .env

ipvsadm -C
ipvsadm -A -t ${EXTIP}:8444 -s rr
ipvsadm -A -t ${EXTIP}:8080 -s rr

docker compose up -d

for i in `seq 1 $THREADS`; do
	cont="pybitmessage-bootstrap-${i}"
	IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $cont 2>/dev/null)
	[ -z "$IP" ] && continue
	echo "Adding $IP"
	ipvsadm -a -t ${EXTIP}:8444 -r ${IP}:8444 -m
	ipvsadm -a -t ${EXTIP}:8080 -r ${IP}:8444 -m
done

ipvsadm -l
