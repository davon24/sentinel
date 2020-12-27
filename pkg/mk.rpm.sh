
#docker run -v `pwd`:/build -it centos:7
#bash /build/mk.rpm.sh

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

yum -y update
yum install -y rpm-build
bash /build/pkg_rpm.sh

yum -y update
yum -y groupinstall "Development Tools"
yum -y install openssl-devel bzip2-devel libffi-devel

bash /build/pkg_rpm_runtime.sh




