#!/bin/bash

apt -y install curl jq ipvsadm libyajl2

EXTIP=$(curl -s telnetmyip.com|jq -r .ip)
if [ ! -e .env ]; then
    THREADS=$(nproc --all)
    PASSWORD=$(tr -dc a-zA-Z0-9 < /dev/urandom | head -c32 && echo)
    cat > .env << EOF
THREADS=$THREADS
PASSWORD=$PASSWORD
EOF
else
    . .env
fi

ipvsadm -C
ipvsadm -A -t ${EXTIP}:8444 -s rr
ipvsadm -A -t ${EXTIP}:8080 -s rr

docker compose up -d

CF=/etc/collectd/collectd.conf.d/curl_json.conf

echo "LoadPlugin curl_json" > $CF
echo "<Plugin curl_json>" >> $CF

for i in `seq 1 $THREADS`; do
    cont="pybitmessage-bootstrap-${i}"
    IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $cont 2>/dev/null)
    [ -z "$IP" ] && continue
    echo "Adding $IP"
    ipvsadm -a -t ${EXTIP}:8444 -r ${IP}:8444 -m
    ipvsadm -a -t ${EXTIP}:8080 -r ${IP}:8444 -m
    INSTANCE=$(echo $cont|tr - _)
    cat >> $CF << EOF
  <URL "http://$IP:8442/">
    Plugin "pybitmessagestatus"
    Instance "$INSTANCE"
    User "api"
    Password "$PASSWORD"
    Post "{\"jsonrpc\":\"2.0\",\"id\":\"id\",\"method\":\"clientStatus\",\"params\":[]}"
    <Key "result/networkConnections">
      Type "gauge"
      Instance "networkconnections"
    </Key>
    <Key "result/numberOfPubkeysProcessed">
      Type "counter"
      Instance "numberofpubkeysprocessed"
    </Key>
    <Key "result/numberOfMessagesProcessed">
      Type "counter"
      Instance "numberofmessagesprocessed"
    </Key>
    <Key "result/numberOfBroadcastsProcessed">
      Type "counter"
      Instance "numberofbroadcastsprocessed"
    </Key>
  </URL>
EOF
done
echo "</Plugin>" >> $CF
systemctl restart collectd

ipvsadm -l -n
