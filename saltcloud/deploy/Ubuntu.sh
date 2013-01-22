#!/bin/bash

mkdir -p /etc/salt/pki
echo '{{ vm['priv_key'] }}' > /etc/salt/pki/minion.pem
echo '{{ vm['pub_key'] }}' > /etc/salt/pki/minion.pub
echo "{{ minion }}" > /etc/salt/minion

apt-get update
apt-get install -y python-software-properties

# 'echo' simulates pressing [enter]
echo | add-apt-repository -y ppa:saltstack/salt
apt-get update
apt-get install -y salt-minion
service salt-minion start
