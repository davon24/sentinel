#!/bin/bash

basedir=`dirname $0`
ver=`awk '/^Version: / {print $2}' $basedir/control`

mkdir ~/dpkgbuild >/dev/null 2>&1

if [ ! -f ~/dpkgbuild/sentinel-$ver.tar.gz ]; then

  curl -k https://gitlab.com/krink/sentinel/-/archive/master/sentinel-master.tar.gz >~/dpkgbuild/sentinel-master.tar.gz
  tar xvf ~/dpkgbuild/sentinel-master.tar.gz -C ~/dpkgbuild/
  mv ~/dpkgbuild/sentinel-master ~/dpkgbuild/sentinel
  #mv ~/dpkgbuild/sentinel-master ~/dpkgbuild/sentinel-$ver
  #cd ~/dpkgbuild/
  #tar cvfz sentinel-$ver.tar.gz sentinel-$ver
  cd -

fi

mkdir  ~/dpkgbuild/sentinel/DEBIAN
cp $basedir/control ~/dpkgbuild/sentinel/DEBIAN/

cd ~/dpkgbuild
dpkg-deb --build sentinel
mv sentinel.deb sentinel-$ver_amd64.deb


