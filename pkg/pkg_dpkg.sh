#!/bin/bash

basedir=`dirname $0`

mkdir ~/dpkgbuild >/dev/null 2>&1

if [ ! -f ~/dpkgbuild/sentinel-master.tar.gz ]; then
  curl -k https://gitlab.com/krink/sentinel/-/archive/master/sentinel-master.tar.gz >~/dpkgbuild/sentinel-master.tar.gz
fi

tar xvf ~/dpkgbuild/sentinel-master.tar.gz -C ~/dpkgbuild/

ver=`awk '/^Version: / {print $2}' ~/dpkgbuild/sentinel-master/pkg/control`

mkdir -p ~/dpkgbuild/sentinel/usr/libexec/sentinel

cp ~/dpkgbuild/sentinel-master/python/sentinel.py ~/dpkgbuild/sentinel/usr/libexec/sentinel/sentinel.py
cp ~/dpkgbuild/sentinel-master/python/tools.py ~/dpkgbuild/sentinel/usr/libexec/sentinel/tools.py
cp ~/dpkgbuild/sentinel-master/python/store.py ~/dpkgbuild/sentinel/usr/libexec/sentinel/store.py
cp ~/dpkgbuild/sentinel-master/python/manuf.py ~/dpkgbuild/sentinel/usr/libexec/sentinel/manuf.py

mkdir ~/dpkgbuild/sentinel/usr/libexec/sentinel/db
cp ~/dpkgbuild/sentinel-master/python/db/manuf ~/dpkgbuild/sentinel/usr/libexec/sentinel/db/

mkdir -p ~/dpkgbuild/sentinel/usr/libexec/sentinel/modules/ps
cp ~/dpkgbuild/sentinel-master/python/modules/ps/ps.py ~/dpkgbuild/sentinel/usr/libexec/sentinel/modules/ps/ps.py

mkdir -p ~/dpkgbuild/sentinel/lib/systemd/system
cp ~/dpkgbuild/sentinel-master/pkg/linux.sentinel.service ~/dpkgbuild/sentinel/lib/systemd/system/sentinel.service

mkdir -p ~/dpkgbuild/sentinel/usr/sbin
cp ~/dpkgbuild/sentinel-master/pkg/sentinel.sh ~/dpkgbuild/sentinel/usr/sbin/sentinel

mkdir  ~/dpkgbuild/sentinel/DEBIAN
cp ~/dpkgbuild/sentinel-master/pkg/control ~/dpkgbuild/sentinel/DEBIAN/

mkdir -p $basedir/package >/dev/null 2>&1

cd ~/dpkgbuild
dpkg-deb --build sentinel
cp sentinel.deb sentinel-${ver}_amd64.deb
cp sentinel.deb $basedir/package/sentinel-${ver}_amd64.deb 


