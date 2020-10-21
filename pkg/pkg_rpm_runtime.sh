#!/bin/bash

basedir=`dirname $0`

ver=`awk '/^Version: / {print $2}' $basedir/sentinel-runtime.spec`

mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} >/dev/null 2>&1

#https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
if [ ! -f ~/rpmbuild/SOURCES/Python-3.8.6.tgz ]; then
  curl -k https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz >~/rpmbuild/SOURCES/Python-3.8.6.tgz
  tar xvf ~/rpmbuild/SOURCES/Python-3.8.6.tgz -C ~/rpmbuild/SOURCES/
fi

#https://www.sqlite.org/2020/sqlite-autoconf-3330000.tar.gz
if [ ! -f ~/rpmbuild/SOURCES/sqlite-autoconf-3330000.tar.gz ]; then
  curl -k https://www.sqlite.org/2020/sqlite-autoconf-3330000.tar.gz >~/rpmbuild/SOURCES/sqlite-autoconf-3330000.tar.gz
  tar xvf ~/rpmbuild/SOURCES/sqlite-autoconf-3330000.tar.gz -C ~/rpmbuild/SOURCES/
fi

cd ~/rpmbuild/SOURCES/sqlite-autoconf-3330000
./configure --prefix=/usr/libexec/sentinel/runtime
make 
make install

cd ~/rpmbuild/SOURCES/Python-3.8.6
LD_RUN_PATH=/usr/libexec/sentinel/runtime/lib ./configure --enable-optimizations --prefix=/usr/libexec/sentinel/runtime
LD_RUN_PATH=/usr/libexec/sentinel/runtime/lib make
LD_RUN_PATH=/usr/libexec/sentinel/runtime/lib make altinstall

cd /usr/libexec/sentinel
mkdir sentinel-runtime-$ver
mv runtime sentinel-runtime-$ver/
tar cvfz sentinel-runtime-$ver.tar.gz sentinel-runtime-$ver
cp sentinel-runtime-$ver.tar.gz ~/rpmbuild/SOURCES/

cd ~/

cp $basedir/sentinel-runtime.spec ~/rpmbuild/SPECS/sentinel-runtime.spec
#rpmbuild -tb ~/rpmbuild/SOURCES/sentinel-runtime-$ver.tar.gz
rpmbuild -ba ~/rpmbuild/SPECS/sentinel-runtime.spec

mkdir -p $basedir/package >/dev/null 2>&1
#cp ~/rpmbuild/SRPMS/*.rpm $basedir/package/
cp ~/rpmbuild/RPMS/x86_64/*.rpm $basedir/package/ >/dev/null 2>&1
#cp ~/rpmbuild/RPMS/noarch/*.rpm $basedir/package/


