#!/bin/bash
# script to open to public interfaces to wendelin standalone service.
# the way to use it is to wget it and then simply run it.
# it requires socat command

ZOPE_PIDS="$(slapos node | grep 'zope\|jupyter-lab' | awk '{print substr($0, 91, 5);}')"
LOCAL_IPv4="$(/sbin/ifconfig ens3 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"

port=20000

for pid in $ZOPE_PIDS;
 do
  # remove any trailing character in case PID is less than 5 digits
  pid="$(echo ${pid} | sed 's/,//')"
  ip_port="$(netstat -lpn --inet --inet6 | grep " $pid"/ |awk '{print substr($0, 21, 17);}')";
  echo $pid, $ip_port, $port

  # socat
  if [[ $ip_port == 2001* ]];
  then
    ipv6_ip=${ip_port:0:10}
    ipv6_port=${ip_port:11:15}
    socat TCP-LISTEN:$port,fork TCP:[$ipv6_ip]:$ipv6_port &
    echo "Jupyter node at https://${LOCAL_IPv4}:${port}/"
  else
    socat TCP-LISTEN:$port,fork TCP:$ip_port &
    echo "Zope node at http://${LOCAL_IPv4}:${port}/"
  fi

  # increase port base
  port=$((port+1))
 done