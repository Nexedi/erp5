#!/bin/bash
# script to open to public interfaces to wendelin standalone service.
# the way to use it is to wget it and then simply run it.
# it requires socat command

ZOPE_PIDS="$(slapos node | grep 'zope\|notebook' | awk '{print substr($0, 59, 5);}')"

port=20000

for pid in $ZOPE_PIDS;
 do
  ip_port="$(netstat -lpn | grep $pid |awk '{print substr($0, 21, 17);}')";
  #echo $pid, $ip_port, $port

  # socat
  if [[ $ip_port == 2001* ]];
  then
    ipv6_ip=${ip_port:0:10}
    ipv6_port=${ip_port:11:15}
    socat TCP-LISTEN:$port,fork TCP:[$ipv6_ip]:$ipv6_port &
    echo "Jupiter node at http://<YOUR_VM_IP>:${port}/"
  else
    socat TCP-LISTEN:$port,fork TCP:$ip_port &
    echo "Zope node at http://<YOUR_VM_IP>:${port}/"
  fi

  # increase port base
  port=$((port+1))
 done