
%define __brp_mangle_shebangs /usr/bin/true

%define bindir  /usr/bin
%define sbindir /usr/sbin

Summary: Sentinel Python Application
Name: sentinel
Version: 1.9.5
Release: 0%{?dist}
License: GPL
URL: https://gitlab.com/krink/sentinel/-/archive/master/sentinel-master.tar.gz
Group: Applications/Internet
Source0: sentinel-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

%if 0%{?rhel} == 8
AutoReqProv: no
#Requires: python38
# Turn off the brp-python-bytecompile script
%global _python_bytecompile_extra 0
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%undefine __brp_python_bytecompile
%endif

%if 0%{?rhel} == 7
AutoReqProv: no
#Requires: python38
# Turn off the brp-python-bytecompile script
%global _python_bytecompile_extra 0
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%undefine __brp_python_bytecompile
%endif

%if 0%{?rhel} == 6
AutoReqProv: no
#Requires: python27
%endif

Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

Provides: sentinel

%description
Sentinel service daemon

%prep
tar xzvf %{SOURCE0}

%install
rm -rf $RPM_BUILD_ROOT

%if 0%{?rhel} == 8
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
cp sentinel-%{version}/pkg/linux.sentinel.service $RPM_BUILD_ROOT/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 7
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
cp sentinel-%{version}/pkg/linux.sentinel.service $RPM_BUILD_ROOT/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 6
mkdir -p $RPM_BUILD_ROOT/etc/init.d
cp sentinel-%{version}/pkg/sentinel.init $RPM_BUILD_ROOT/etc/init.d/sentinel
chmod 755 $RPM_BUILD_ROOT/etc/init.d/sentinel
%endif

mkdir -p $RPM_BUILD_ROOT/usr/sbin
cp sentinel-%{version}/pkg/sentinel.sh $RPM_BUILD_ROOT/usr/sbin/sentinel

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel

cp sentinel-%{version}/src/sentinel_server/sentinel.py $RPM_BUILD_ROOT/usr/libexec/sentinel/sentinel.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/sentinel.py

cp sentinel-%{version}/src/sentinel_server/tools.py $RPM_BUILD_ROOT/usr/libexec/sentinel/tools.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/tools.py

cp sentinel-%{version}/src/sentinel_server/store.py $RPM_BUILD_ROOT/usr/libexec/sentinel/store.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/store.py

cp sentinel-%{version}/src/sentinel_server/manuf.py $RPM_BUILD_ROOT/usr/libexec/sentinel/manuf.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/manuf.py

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel/db
cp sentinel-%{version}/src/sentinel_server/db/manuf $RPM_BUILD_ROOT/usr/libexec/sentinel/db/manuf

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ps
cp sentinel-%{version}/src/sentinel_server/modules/ps/ps.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ps/ps.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ps/ps.py

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/hv
cp sentinel-%{version}/src/sentinel_server/modules/hv/kvm.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/hv/kvm.py
cp sentinel-%{version}/src/sentinel_server/modules/hv/__init__.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/hv/__init__.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/hv/kvm.py

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/gitegridy
cp sentinel-%{version}/src/sentinel_server/modules/gitegridy/gitegridy.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/gitegridy/gitegridy.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/gitegridy/gitegridy.py

mkdir -p $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ipwhois
cp sentinel-%{version}/src/sentinel_server/modules/ipwhois/ipwhois.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ipwhois/ipwhois.py
cp sentinel-%{version}/src/sentinel_server/modules/ipwhois/__init__.py $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ipwhois/__init__.py
chmod 755 $RPM_BUILD_ROOT/usr/libexec/sentinel/modules/ipwhois/ipwhois.py


%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add user/group here if needed...
#echo "Add user/group here if needed..." >/dev/null 2>&1
#/usr/bin/getent group sentinel > /dev/null || /usr/sbin/groupadd -r sentinel
#/usr/bin/getent passwd sentinel > /dev/null || /usr/sbin/useradd -r -d /usr/libexec/sentinel -s /sbin/nologin -g sentinel sentinel

%post
# Add serivces for startup
%if 0%{?rhel} == 6
  echo "rh6"
  echo "install /etc/init.d/sentinel"
       /sbin/chkconfig --add sentinel 
  if [ $1 = 1 ]; then #1 install
    echo "start sentinel"
        /etc/init.d/sentinel start
  else
    echo "restart sentinel"
        /etc/init.d/sentinel restart
  fi
%endif

%if 0%{?rhel} == 7
  echo "systemctl daemon-reload"
        systemctl daemon-reload
  if [ $1 = 1 ]; then #1 install
    echo "systemctl enable sentinel"
          systemctl enable sentinel
    echo "systemctl start sentinel"
          systemctl start sentinel
  else
    echo "systemctl restart sentinel"
          systemctl restart sentinel
  fi
%endif

%if 0%{?rhel} == 8
  echo "systemctl daemon-reload"
        systemctl daemon-reload
  if [ $1 = 1 ]; then #1 install
    echo "systemctl enable sentinel"
          systemctl enable sentinel
    echo "systemctl start sentinel"
          systemctl start sentinel
  else
    echo "systemctl restart sentinel"
          systemctl restart sentinel
  fi
%endif


#end post

%postun
#echo "postrun.done"

%files
%defattr(-,root,root)
/usr/sbin/sentinel

%if 0%{?rhel} == 8
/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 7
/lib/systemd/system/sentinel.service
%endif

%if 0%{?rhel} == 6
/etc/init.d/sentinel
%endif

%dir /usr/libexec/sentinel
%config(noreplace) /usr/libexec/sentinel/db/manuf
/usr/libexec/sentinel/sentinel.py
/usr/libexec/sentinel/manuf.py
/usr/libexec/sentinel/store.py
/usr/libexec/sentinel/tools.py
/usr/libexec/sentinel/modules/ps/ps.py
/usr/libexec/sentinel/modules/hv/kvm.py
/usr/libexec/sentinel/modules/hv/__init__.py
/usr/libexec/sentinel/modules/gitegridy/gitegridy.py
/usr/libexec/sentinel/modules/ipwhois/ipwhois.py
/usr/libexec/sentinel/modules/ipwhois/__init__.py

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

%exclude /usr/libexec/sentinel/*.pyc
%exclude /usr/libexec/sentinel/*.pyo
%exclude /usr/libexec/sentinel/modules/ps/*.pyc
%exclude /usr/libexec/sentinel/modules/ps/*.pyo
%exclude /usr/libexec/sentinel/modules/hv/*.pyc
%exclude /usr/libexec/sentinel/modules/hv/*.pyo
%exclude /usr/libexec/sentinel/modules/gitegridy/*.pyc
%exclude /usr/libexec/sentinel/modules/gitegridy/*.pyo
%exclude /usr/libexec/sentinel/modules/ipwhois/*.pyc
%exclude /usr/libexec/sentinel/modules/ipwhois/*.pyo

%changelog
* Tue Feb 28 2023 Karl Rink <karl@rink.us> v1.9.0-0
- 1.9.0-0 release ♒

* Mon Jan 09 2023 Karl Rink <karl@rink.us> v1.8.6-0
- 1.8.6-0 release 🎉

* Fri Nov 11 2022 Karl Rink <karl@rink.us> v1.8.5-0
- 1.8.5-0 release 🎖

* Sat Oct 08 2022 Karl Rink <karl@rink.us> v1.8.3-0
- 1.8.3-0 release 🎃

* Fri Sep 23 2022 Karl Rink <karl@rink.us> v1.8.2-0
- 1.8.2-0 release

* Thu Sep 22 2022 Karl Rink <karl@rink.us> v1.8.1-0
- 1.8.1-0 release 🍁

* Wed Sep 21 2022 Karl Rink <karl@rink.us> v1.8.0-0
- 1.8.0-0 release 🍁

* Wed Mar 10 2021 Karl Rink <karl@rink.us> v1.6.15-1
- 1.6.15-1 release 🍀

* Wed Feb 10 2021 Karl Rink <karl@rink.us> v1.6.14-1
- 1.6.14-1 release

* Sun Jan 31 2021 Karl Rink <karl@rink.us> v1.6.13-1
- 1.6.13-1 Kent Bradley Hovland

* Thu Jan 28 2021 Karl Rink <karl@rink.us> v1.6.12-1
- 1.6.12-1

