
%define __brp_mangle_shebangs /usr/bin/true
#%global __mangle_shebangs_exclude ^$
#%global __mangle_shebangs_exclude_from /usr/libexec/sentinel/runtime/lib/

%global _python_bytecompile_extra 0

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%define bindir  /usr/bin
%define sbindir /usr/sbin

Summary: Sentinel Python 3.8.6 runtime tools
Name: sentinel-runtime
Version: 1.6.28
Release: 1%{?dist}
License: GPL
#URL: https://gitlab.com/krink/sentinel/-/archive/master/sentinel-master.tar.gz
Group: Applications/Internet
Source0: sentinel-runtime-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: x86_64

%if 0%{?rhel} == 8
AutoReqProv: no
#Requires: python38
#BuildRequires: /usr/bin/pathfix.py
%endif

%if 0%{?rhel} == 7
AutoReqProv: no
#Requires: python38
%endif

%if 0%{?rhel} == 6
AutoReqProv: no
#Requires: python27
%endif

Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

Provides: sentinel-runtime

%description
Sentinel service runtime tools

%prep
tar xzvf %{SOURCE0}

%if 0%{?rhel} == 8
#pathfix.py -pni "%{__python3} %{py3_shbang_opts}" .
%endif

%install
rm -rf $RPM_BUILD_ROOT
#exit 0

%if 0%{?rhel} == 8
#mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
#cp sentinel-%{version}/pkg/linux.sentinel.service $RPM_BUILD_ROOT/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 7
#mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
#cp sentinel-%{version}/pkg/linux.sentinel.service $RPM_BUILD_ROOT/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 6
#mkdir -p $RPM_BUILD_ROOT/etc/init.d
#cp sentinel-%{version}/pkg/sentinel.init $RPM_BUILD_ROOT/etc/init.d/sentinel
#chmod 755 $RPM_BUILD_ROOT/etc/init.d/sentinel
%endif

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel

mv sentinel-runtime-%{version}/runtime $RPM_BUILD_ROOT/usr/libexec/sentinel/
#cp -a /usr/libexec/sentinel/runtime $RPM_BUILD_ROOT/usr/libexec/sentinel/

#cp sentinel-%{version}/python/sentinel.py $RPM_BUILD_ROOT/usr/libexec/sentinel/sentinel.py
#chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/sentinel.py

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add user/group here if needed...
#echo "Add user/group here if needed..." >/dev/null 2>&1
#/usr/bin/getent group sentinel > /dev/null || /usr/sbin/groupadd -r sentinel
#/usr/bin/getent passwd sentinel > /dev/null || /usr/sbin/useradd -r -d /usr/libexec/sentinel -s /sbin/nologin -g sentinel sentinel

%post
# Add serivces for startup
#%if 0%{?rhel} == 6
#  echo "rh6"
#  echo "install /etc/init.d/sentinel"
#       /sbin/chkconfig --add sentinel 
#  if [ $1 = 1 ]; then #1 install
#    echo "start sentinel"
#        /etc/init.d/sentinel start
#  else
#    echo "restart sentinel"
#        /etc/init.d/sentinel restart
#  fi
#%endif
#
#%if 0%{?rhel} == 7
#  echo "systemctl daemon-reload"
#        systemctl daemon-reload
#  if [ $1 = 1 ]; then #1 install
#    echo "systemctl enable sentinel"
#          systemctl enable sentinel
#    echo "systemctl start sentinel"
#          systemctl start sentinel
#  else
#    echo "systemctl restart sentinel"
#          systemctl restart sentinel
#  fi
#%endif
#end post

%postun
#echo "postrun.done"

%files
%defattr(-,root,root)

%if 0%{?rhel} == 8
#/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 7
#/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 6
#/etc/init.d/sentinel
%endif

#----

#%dir /usr/libexec/sentinel/runtime
/usr/libexec/sentinel/runtime/*

#----

%if 0%{?rhel} == 8
#%exclude /usr/lib/python2.7/site-packages/scrawl/*.pyc
#%exclude /usr/lib/python2.7/site-packages/scrawl/*.pyo
%endif

%if 0%{?rhel} == 7
#%exclude /usr/lib/python2.7/site-packages/scrawl/*.pyc
#%exclude /usr/lib/python2.7/site-packages/scrawl/*.pyo
%endif

%if 0%{?rhel} == 6
#%exclude /usr/lib/python2.6/site-packages/scrawl/*.pyc
#%exclude /usr/lib/python2.6/site-packages/scrawl/*.pyo
%endif

#%exclude /usr/libexec/sentinel/runtime/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/*/*/*/*/*/*/*/*/*/*/*.pyc
#%exclude /usr/libexec/sentinel/runtime/lib/python3.8/test/*
#%exclude /usr/libexec/sentinel/runtime/include/*

#%exclude /usr/libexec/sentinel/Python3.8.6/*.pyo
#%exclude /usr/libexec/sentinel/Python3.8.6/modules/ps/*.pyc
#%exclude /usr/libexec/sentinel/Python3.8.6/modules/ps/*.pyo

%changelog
* Wed Mar 10 2021 Karl Rink <karl@rink.us> v1.6.15-1
- 1.6.15-1 release 🍀

* Wed Feb 10 2021 Karl Rink <karl@rink.us> v1.6.14-1
- 1.6.14-1 release

* Sun Jan 31 2021 Karl Rink <karl@rink.us> v1.6.13-1
- 1.6.13-1 Kent Bradley Hovland

* Thu Jan 28 2021 Karl Rink <karl@rink.us> v1.6.12-1
- 1.6.12-1


