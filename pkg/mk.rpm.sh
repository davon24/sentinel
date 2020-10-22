
docker run -v `pwd`:/build -it centos:7

yum install -y rpm-build
bash /build/pkg_rpm.sh

yum -y update
yum -y groupinstall "Development Tools"
yum -y install openssl-devel bzip2-devel libffi-devel

bash /build/pkg_rpm_runtime.sh




