#!/bin/bash

basedir=`dirname $0`

mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} >/dev/null 2>&1

if [ ! -f ~/rpmbuild/SOURCES/sentinel-$ver.tar.gz ]; then
  curl -k https://gitlab.com/krink/sentinel/-/archive/master/sentinel-master.tar.gz >~/rpmbuild/SOURCES/sentinel-master.tar.gz
fi

tar xvf ~/rpmbuild/SOURCES/sentinel-master.tar.gz -C ~/rpmbuild/SOURCES/

ver=`awk '/^Version: / {print $2}' ~/rpmbuild/SOURCES/sentinel-master/pkg/sentinel.spec`
cp ~/rpmbuild/SOURCES/sentinel-master/pkg/sentinel.spec ~/rpmbuild/SPECS/sentinel.spec

mv ~/rpmbuild/SOURCES/sentinel-master ~/rpmbuild/SOURCES/sentinel-$ver
cd ~/rpmbuild/SOURCES/
tar cvfz sentinel-$ver.tar.gz sentinel-$ver
cd -

#rpmbuild -tb ~/rpmbuild/SOURCES/sentinel-$ver.tar.gz
rpmbuild -ba ~/rpmbuild/SPECS/sentinel.spec

mkdir -p $basedir/package >/dev/null 2>&1
cp ~/rpmbuild/SRPMS/*.rpm $basedir/package/
#cp ~/rpmbuild/RPMS/x86_64/*.rpm $basedir/package/ >/dev/null 2>&1
cp ~/rpmbuild/RPMS/noarch/*.rpm $basedir/package/


