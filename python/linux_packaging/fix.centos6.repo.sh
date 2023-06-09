#!/bin/bash

CENTOS_RELEASE=`cat /etc/centos-release | cut -d ' ' -f3 | awk -F'.' '{print $1}'`

if [ $CENTOS_RELEASE == 6 ]; then

cat <<-'EOE' > /etc/yum.repos.d/CentOS-Base.repo

[base]
name=CentOS-$releasever - Base
baseurl=https://vault.centos.org/6.10/os/$basearch/
gpgcheck=0
enabled=1

[updates]
name=CentOS-$releasever - Updates
baseurl=https://vault.centos.org/6.10/updates/$basearch/
gpgcheck=0
enabled=1

[extras]
name=CentOS-$releasever - Extras
baseurl=https://vault.centos.org/6.10/extras/$basearch/
gpgcheck=0
enabled=1

EOE

fi


