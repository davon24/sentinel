
#docker run -v `pwd`:/build -it ubuntu:18.04

apt-get update
apt-get install -y build-essential
apt-get install -y curl

bash /build/pkg_dpkg.sh

apt-get install -y rsync
bash /build/pkg_dpkg_runtime.sh


