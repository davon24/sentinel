

./sentinel.py update-job vuln-scan-1 '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.159"]}'
./sentinel.py update-job vuln-scan-2 '{"repeat": "5min", "job": "vuln-scan", "ips": ["192.168.0.1", "192.168.0.2"]}'

./sentinel.py update-job vuln-scan-1-subnet '{"time": "2020-09-20 00:00:00", "job": "vuln-scan", "ips": ["192.168.0.1/24"]}'


----



# vuln scan your home gateway device

🎃 krink@Karls-MBP bin % sentinel vuln-scan 192.168.0.1
hostLst: ['192.168.0.1']
Starting Nmap 7.80 ( https://nmap.org ) at 2020-10-29 19:25 PDT
Pre-scan script results:
| broadcast-avahi-dos:
|   Discovered hosts:
|     224.0.0.251
|   After NULL UDP avahi packet DoS (CVE-2011-1002).
|_  Hosts are all up (not vulnerable).
Nmap scan report for 192.168.0.1
Host is up (0.0064s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
53/tcp   open  domain
8443/tcp open  https-alt
|_http-aspnet-debug: ERROR: Script execution failed (use -d to debug)
| http-enum:
|   /blog/: Blog
|   /weblog/: Blog
|   /weblogs/: Blog
|   /wordpress/: Blog
|   /wiki/: Wiki
|   /mediawiki/: Wiki
|   /tikiwiki/: Tikiwiki
|   /j2ee/examples/servlets/: Oracle j2ee examples
|   /j2ee/examples/jsp/: Oracle j2ee examples
|   /dsc/: Trend Micro Data Loss Prevention Virtual Appliance
|   /reg_1.htm: Polycom IP phone
|   /adr.htm: Snom IP Phone
|   /line_login.htm?l=1: Snom IP Phone
|   /globalSIPsettings.html: Aastra IP Phone
|   /SIPsettingsLine1.html: Aastra IP Phone
|   /websvn/: WEBSVN Repository
|   /repos/: Possible code repository
|   /repo/: Possible code repository
|   /svn/: Possible code repository
|   /cvs/: Possible code repository
|   /frontend/x3/: CPanel
|   /egroupware/: eGroupware
|   /aphpkb/: Andys PHP Knowledgebase
|   /webedition/we/include/we_modules/: Web Edition
|   /webedition/: Web Edition
|   /Examples/: Possible documentation files
|   /ocsreports/: OCS Inventory
|   /forum/: Forum
|   /forums/: Forum
|   /smf/: Forum
|   /phpbb/: Forum
|   /manager/: Possible admin folder
|   /admin/: Possible admin folder
|   /admin/admin/: Possible admin folder
|   /administrator/: Possible admin folder
|   /moderator/: Possible admin folder
|   /webadmin/: Possible admin folder
|   /adminarea/: Possible admin folder
|   /bb-admin/: Possible admin folder
|   /adminLogin/: Possible admin folder
|   /admin_area/: Possible admin folder
|   /panel-administracion/: Possible admin folder
|   /instadmin/: Possible admin folder
|   /memberadmin/: Possible admin folder
|   /administratorlogin/: Possible admin folder
|   /adm/: Possible admin folder
|   /siteadmin/login.html: Possible admin folder
|   /admin/index.html: Possible admin folder
|   /admin/login.html: Possible admin folder
|   /admin/admin.html: Possible admin folder
|   /admin_area/login.html: Possible admin folder
|   /admin_area/index.html: Possible admin folder
|   /admincp/: Possible admin folder
|   /admincp/index.asp: Possible admin folder
|   /admincp/index.html: Possible admin folder
|   /admin/account.html: Possible admin folder
|   /adminpanel.html: Possible admin folder
|   /webadmin.html: Possible admin folder
|   /webadmin/index.html: Possible admin folder
|   /webadmin/admin.html: Possible admin folder
|   /webadmin/login.html: Possible admin folder
|   /admin/admin_login.html: Possible admin folder
|   /admin_login.html: Possible admin folder
|   /panel-administracion/login.html: Possible admin folder
|   /admin_area/admin.html: Possible admin folder
|   /bb-admin/index.html: Possible admin folder
|   /bb-admin/login.html: Possible admin folder
|   /bb-admin/admin.html: Possible admin folder
|   /admin/home.html: Possible admin folder
|   /pages/admin/admin-login.html: Possible admin folder
|   /admin/admin-login.html: Possible admin folder
|   /admin-login.html: Possible admin folder
|   /admin/adminLogin.html: Possible admin folder
|   /adminLogin.html: Possible admin folder
|   /home.html: Possible admin folder
|   /adminarea/index.html: Possible admin folder
|   /adminarea/admin.html: Possible admin folder
|   /admin/controlpanel.html: Possible admin folder
|   /admin.html: Possible admin folder
|   /admin/cp.html: Possible admin folder
|   /cp.html: Possible admin folder
|   /moderator.html: Possible admin folder
|   /administrator/index.html: Possible admin folder
|   /administrator/login.html: Possible admin folder
|   /user.html: Possible admin folder
|   /administrator/account.html: Possible admin folder
|   /administrator.html: Possible admin folder
|   /login.html: Possible admin folder
|   /modelsearch/login.html: Possible admin folder
|   /moderator/login.html: Possible admin folder
|   /adminarea/login.html: Possible admin folder
|   /panel-administracion/index.html: Possible admin folder
|   /panel-administracion/admin.html: Possible admin folder
|   /modelsearch/index.html: Possible admin folder
|   /modelsearch/admin.html: Possible admin folder
|   /admincontrol/login.html: Possible admin folder
|   /adm/index.html: Possible admin folder
|   /adm.html: Possible admin folder
|   /moderator/admin.html: Possible admin folder
|   /account.html: Possible admin folder
|   /controlpanel.html: Possible admin folder
|   /admincontrol.html: Possible admin folder
|   /adm1n/: Possible admin folder
|   /4dm1n/: Possible admin folder
|   /account.asp: Possible admin folder
|   /admin/account.asp: Possible admin folder
|   /admin/index.asp: Possible admin folder
|   /admin/login.asp: Possible admin folder
|   /admin/admin.asp: Possible admin folder
|   /admin_area/admin.asp: Possible admin folder
|   /admin_area/login.asp: Possible admin folder
|   /admin_area/index.asp: Possible admin folder
|   /bb-admin/index.asp: Possible admin folder
|   /bb-admin/login.asp: Possible admin folder
|   /bb-admin/admin.asp: Possible admin folder
|   /admin/home.asp: Possible admin folder
|   /admin/controlpanel.asp: Possible admin folder
|   /admin.asp: Possible admin folder
|   /pages/admin/admin-login.asp: Possible admin folder
|   /admin/admin-login.asp: Possible admin folder
|   /admin-login.asp: Possible admin folder
|   /admin/cp.asp: Possible admin folder
|   /cp.asp: Possible admin folder
|   /administrator/account.asp: Possible admin folder
|   /administrator.asp: Possible admin folder
|   /login.asp: Possible admin folder
|   /modelsearch/login.asp: Possible admin folder
|   /moderator.asp: Possible admin folder
|   /moderator/login.asp: Possible admin folder
|   /administrator/login.asp: Possible admin folder
|   /moderator/admin.asp: Possible admin folder
|   /controlpanel.asp: Possible admin folder
|   /user.asp: Possible admin folder
|   /admincp/login.asp: Possible admin folder
|   /admincontrol.asp: Possible admin folder
|   /adminpanel.asp: Possible admin folder
|   /webadmin.asp: Possible admin folder
|   /webadmin/index.asp: Possible admin folder
|   /webadmin/admin.asp: Possible admin folder
|   /webadmin/login.asp: Possible admin folder
|   /admin/admin_login.asp: Possible admin folder
|   /admin_login.asp: Possible admin folder
|   /panel-administracion/login.asp: Possible admin folder
|   /adminLogin.asp: Possible admin folder
|   /admin/adminLogin.asp: Possible admin folder
|   /home.asp: Possible admin folder
|   /adminarea/index.asp: Possible admin folder
|   /adminarea/admin.asp: Possible admin folder
|   /adminarea/login.asp: Possible admin folder
|   /panel-administracion/index.asp: Possible admin folder
|   /panel-administracion/admin.asp: Possible admin folder
|   /modelsearch/index.asp: Possible admin folder
|   /modelsearch/admin.asp: Possible admin folder
|   /administrator/index.asp: Possible admin folder
|   /admincontrol/login.asp: Possible admin folder
|   /adm/admloginuser.asp: Possible admin folder
|   /admloginuser.asp: Possible admin folder
|   /admin2.asp: Possible admin folder
|   /admin2/login.asp: Possible admin folder
|   /admin2/index.asp: Possible admin folder
|   /adm/index.asp: Possible admin folder
|   /adm.asp: Possible admin folder
|   /adm_auth.asp: Possible admin folder
|   /memberadmin.asp: Possible admin folder
|   /administratorlogin.asp: Possible admin folder
|   /siteadmin/login.asp: Possible admin folder
|   /siteadmin/index.asp: Possible admin folder
|   /account.aspx: Possible admin folder
|   /admin/account.aspx: Possible admin folder
|   /admin/index.aspx: Possible admin folder
|   /admin/login.aspx: Possible admin folder
|   /admin/admin.aspx: Possible admin folder
|   /admin_area/admin.aspx: Possible admin folder
|   /admin_area/login.aspx: Possible admin folder
|   /admin_area/index.aspx: Possible admin folder
|   /bb-admin/index.aspx: Possible admin folder
|   /bb-admin/login.aspx: Possible admin folder
|   /bb-admin/admin.aspx: Possible admin folder
|   /admin/home.aspx: Possible admin folder
|   /admin/controlpanel.aspx: Possible admin folder
|   /admin.aspx: Possible admin folder
|   /pages/admin/admin-login.aspx: Possible admin folder
|   /admin/admin-login.aspx: Possible admin folder
|   /admin-login.aspx: Possible admin folder
|   /admin/cp.aspx: Possible admin folder
|   /cp.aspx: Possible admin folder
|   /administrator/account.aspx: Possible admin folder
|   /administrator.aspx: Possible admin folder
|   /login.aspx: Possible admin folder
|   /modelsearch/login.aspx: Possible admin folder
|   /moderator.aspx: Possible admin folder
|   /moderator/login.aspx: Possible admin folder
|   /administrator/login.aspx: Possible admin folder
|   /moderator/admin.aspx: Possible admin folder
|   /controlpanel.aspx: Possible admin folder
|   /user.aspx: Possible admin folder
|   /admincp/index.aspx: Possible admin folder
|   /admincp/login.aspx: Possible admin folder
|   /admincontrol.aspx: Possible admin folder
|   /adminpanel.aspx: Possible admin folder
|   /webadmin.aspx: Possible admin folder
|   /webadmin/index.aspx: Possible admin folder
|   /webadmin/admin.aspx: Possible admin folder
|   /webadmin/login.aspx: Possible admin folder
|   /admin/admin_login.aspx: Possible admin folder
|   /admin_login.aspx: Possible admin folder
|   /panel-administracion/login.aspx: Possible admin folder
|   /adminLogin.aspx: Possible admin folder
|   /admin/adminLogin.aspx: Possible admin folder
|   /home.aspx: Possible admin folder
|   /adminarea/index.aspx: Possible admin folder
|   /adminarea/admin.aspx: Possible admin folder
|   /adminarea/login.aspx: Possible admin folder
|   /panel-administracion/index.aspx: Possible admin folder
|   /panel-administracion/admin.aspx: Possible admin folder
|   /modelsearch/index.aspx: Possible admin folder
|   /modelsearch/admin.aspx: Possible admin folder
|   /administrator/index.aspx: Possible admin folder
|   /admincontrol/login.aspx: Possible admin folder
|   /adm/admloginuser.aspx: Possible admin folder
|   /admloginuser.aspx: Possible admin folder
|   /admin2.aspx: Possible admin folder
|   /admin2/login.aspx: Possible admin folder
|   /admin2/index.aspx: Possible admin folder
|   /adm/index.aspx: Possible admin folder
|   /adm.aspx: Possible admin folder
|   /adm_auth.aspx: Possible admin folder
|   /memberadmin.aspx: Possible admin folder
|   /administratorlogin.aspx: Possible admin folder
|   /siteadmin/login.aspx: Possible admin folder
|   /siteadmin/index.aspx: Possible admin folder
|   /administr8.asp: Possible admin folder
|   /administr8.aspx: Possible admin folder
|   /administr8/: Possible admin folder
|   /administer/: Possible admin folder
|   /administracao.asp: Possible admin folder
|   /administracao.aspx: Possible admin folder
|   /administracion.asp: Possible admin folder
|   /administracion.aspx: Possible admin folder
|   /administrators/: Possible admin folder
|   /adminpro/: Possible admin folder
|   /admins/: Possible admin folder
|   /admins.asp: Possible admin folder
|   /admins.aspx: Possible admin folder
|   /maintenance/: Possible admin folder
|   /Lotus_Domino_Admin/: Possible admin folder
|   /hpwebjetadmin/: Possible admin folder
|   /_admin/: Possible admin folder
|   /_administrator/: Possible admin folder
|   /_administrador/: Possible admin folder
|   /_admins/: Possible admin folder
|   /_administrators/: Possible admin folder
|   /_administradores/: Possible admin folder
|   /_administracion/: Possible admin folder
|   /_4dm1n/: Possible admin folder
|   /_adm1n/: Possible admin folder
|   /_Admin/: Possible admin folder
|   /system_administration/: Possible admin folder
|   /system-administration/: Possible admin folder
|   /system-admin/: Possible admin folder
|   /system-admins/: Possible admin folder
|   /system-administrators/: Possible admin folder
|   /administracion-sistema/: Possible admin folder
|   /Administracion/: Possible admin folder
|   /Admin/: Possible admin folder
|   /Administrator/: Possible admin folder
|   /Manager/: Possible admin folder
|   /Adm/: Possible admin folder
|   /systemadmin/: Possible admin folder
|   /AdminLogin.asp: Possible admin folder
|   /AdminLogin.aspx: Possible admin folder
|   /admin108/: Possible admin folder
|   /pec_admin/: Possible admin folder
|   /system/admin/: Possible admin folder
|   /plog-admin/: Possible admin folder
|   /ESAdmin/: Possible admin folder
|   /axis2-admin/: Possible admin folder
|   /_sys/: Possible admin folder
|   /admin_cp.asp: Possible admin folder
|   /sitecore/admin/: Possible admin folder
|   /sitecore/login/admin/: Possible admin folder
|   /backup/: Possible backup
|   /backups/: Possible backup
|   /bak/: Possible backup
|   /back/: Possible backup
|   /cache/backup/: Possible backup
|   /admin/backup/: Possible backup
|   /clientaccesspolicy.xml: Microsoft Silverlight crossdomain policy
|   /atom/: RSS or Atom feed
|   /atom.aspx: RSS or Atom feed
|   /atom.xml: RSS or Atom feed
|   /rss/: RSS or Atom feed
|   /rss.aspx: RSS or Atom feed
|   /rss.xml: RSS or Atom feed
|   /example/: Sample scripts
|   /examples/: Sample scripts
|   /iissamples/: Sample scripts
|   /j2eeexamples/: Sample scripts
|   /j2eeexamplesjsp/: Sample scripts
|   /sample/: Sample scripts
|   /ncsample/: Sample scripts
|   /fpsample/: Sample scripts
|   /cmsample/: Sample scripts
|   /samples/: Sample scripts
|   /mono/1.1/index.aspx: Sample scripts
|   /login/: Login page
|   /login.htm: Login page
|   /test.asp: Test page
|   /test/: Test page
|   /test.htm: Test page
|   /test.html: Test page
|   /webmail/: Mail folder
|   /mail/: Mail folder
|   /log/: Logs
|   /log.htm: Logs
|   /log.asp: Logs
|   /log.aspx: Logs
|   /logs/: Logs
|   /logs.htm: Logs
|   /logs.asp: Logs
|   /logs.aspx: Logs
|   /wwwlog/: Logs
|   /wwwlogs/: Logs
|   /mail_log_files/: Logs
|   /mono/: Mono
|   /crossdomain.xml: Adobe Flash crossdomain policy
|   /uploadtester.asp: Free ASP Upload Shell
|   /eyeos/: Possible eyeOS installation
|   /appServer/jvmReport.jsf?instanceName=server&pageTitle=JVM%20Report: Oracle GlashFish Server Information
|   /common/appServer/jvmReport.jsf?pageTitle=JVM%20Report: Oracle GlashFish Server Information
|   /common/appServer/jvmReport.jsf?reportType=summary&instanceName=server: Oracle GlashFish Server Information
|   /sourcebans/: SourceBans - Steam server application
|   /tiny_mce/plugins/filemanager/: Tiny MCE File Upload
|   /TopToolArea.html: Alteon OS BBI (Nortell)
|   /switchSystem.html: Alteon OS BBI (Nortell)
|   /ajaxfilemanager/: AJAX File Manager
|   /nagios3/: Nagios3
|   /test/logon.html: Jetty
|   /cacti/: Cacti Web Monitoring
|   /imc/: 3Com Intelligent Management Center
|   /imcws/: 3Com Intelligent Management Center
|   /partymgr/: Apache OFBiz
|   /Uploadify/: Uploadify
|   /syssite/: ShopEx
|   /dhost/: Novell eDirectory
|   /setup/password_required.html: 2WIRE GATEWAY
|   /zp-core/: Zen Photo
|   /amember/: aMember
|   /Portal0000.htm: SCADA Siemens PCS7
|   /arcsight/: Arcsight
|   /beef/: BeEF Browser Exploitation Framework
|   /BEEF/: BeEF Browser Exploitation Framework
|   /javascript/sorttable.js: Secunia NSI
|   /deploymentmanager/: IBM Proventia
|   /officescan/console/html/ClientInstall/officescannt.htm: Trend Micro OfficeScan Server
|   /dotDefender/: dotDefender Web Application Firewall
|   /actuator/: Spring Boot Actuator endpoint
|   /auditevents/: Spring Boot Actuator endpoint
|   /autoconfig/: Spring Boot Actuator endpoint
|   /beans/: Spring Boot Actuator endpoint
|   /configprops/: Spring Boot Actuator endpoint
|   /env/: Spring Boot Actuator endpoint
|   /flyway/: Spring Boot Actuator endpoint
|   /health/: Spring Boot Actuator endpoint
|   /loggers/: Spring Boot Actuator endpoint
|   /liquibase/: Spring Boot Actuator endpoint
|   /metrics/: Spring Boot Actuator endpoint
|   /mappings/: Spring Boot Actuator endpoint
|   /trace/: Spring Boot Actuator endpoint
|   /heapdump/: Spring MVC Endpoint
|   /jolokia/: Spring MVC Endpoint
|   /vmware/: VMWare
|   /ui/: VMWare
|   /en/welcomeRes.js: VMWare
|   /citrix/: Citrix
|   /Citrix/: Citrix
|   /Citrix/MetaFrame/auth/login.aspx: Citrix
|   /sw/auth/login.aspx: Citrix
|   /citrix/AccessPlatform/auth/clientscripts/: Citrix
|   /AccessPlatform/auth/clientscripts/: Citrix
|   /Citrix//AccessPlatform/auth/clientscripts/cookies.js: Citrix
|   /Citrix/AccessPlatform/auth/clientscripts/login.js: Citrix
|   /Citrix/PNAgent/config.xml: Citrix
|   /cpqlogin.htm?RedirectUrl=/&RedirectQueryString=: HP System Management Homepage
|   /ie_index.htm: HP Integrated Lights Out
|   /rrc.htm: Raritan Remote Client
|   /axis2/: Apache Axis2
|   /invoker/: JBoss Console
|   /jmx-console/: JBoss Console
|   /admin-console/: JBoss Console
|   /CFIDE/Administrator/startstop.html: ColdFusion Admin Console
|   /flexfm/: Flex File Manager
|   /hp/device/webAccess/index.htm: HP Printer
|   /phpmyadmin/: phpMyAdmin
|   /phpMyAdmin/: phpMyAdmin
|   /PHPMyAdmin/: phpMyAdmin
|   /PMA/: phpMyAdmin
|   /pma/: phpMyAdmin
|   /dbadmin/: phpMyAdmin
|   /myadmin/: phpMyAdmin
|   /php-my-admin/: phpMyAdmin
|   /phpMyAdmin2/: phpMyAdmin
|   /phpMyAdmin-2/: phpMyAdmin
|   /phpMyAdmin-2.2.3/: phpMyAdmin
|   /phpMyAdmin-2.2.6/: phpMyAdmin
|   /phpMyAdmin-2.5.1/: phpMyAdmin
|   /phpMyAdmin-2.5.4/: phpMyAdmin
|   /phpMyAdmin-2.5.5-rc1/: phpMyAdmin
|   /phpMyAdmin-2.5.5-rc2/: phpMyAdmin
|   /phpMyAdmin-2.5.5/: phpMyAdmin
|   /phpMyAdmin-2.5.5-pl1/: phpMyAdmin
|   /phpMyAdmin-2.5.6-rc1/: phpMyAdmin
|   /phpMyAdmin-2.5.6-rc2/: phpMyAdmin
|   /phpMyAdmin-2.5.6/: phpMyAdmin
|   /phpMyAdmin-2.5.7/: phpMyAdmin
|   /phpMyAdmin-2.5.7-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.0-alpha/: phpMyAdmin
|   /phpMyAdmin-2.6.0-alpha2/: phpMyAdmin
|   /phpMyAdmin-2.6.0-beta1/: phpMyAdmin
|   /phpMyAdmin-2.6.0-beta2/: phpMyAdmin
|   /phpMyAdmin-2.6.0-rc1/: phpMyAdmin
|   /phpMyAdmin-2.6.0-rc2/: phpMyAdmin
|   /phpMyAdmin-2.6.0-rc3/: phpMyAdmin
|   /phpMyAdmin-2.6.0/: phpMyAdmin
|   /phpMyAdmin-2.6.0-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.0-pl2/: phpMyAdmin
|   /phpMyAdmin-2.6.0-pl3/: phpMyAdmin
|   /phpMyAdmin-2.6.1-rc1/: phpMyAdmin
|   /phpMyAdmin-2.6.1-rc2/: phpMyAdmin
|   /phpMyAdmin-2.6.1/: phpMyAdmin
|   /phpMyAdmin-2.6.1-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.1-pl2/: phpMyAdmin
|   /phpMyAdmin-2.6.1-pl3/: phpMyAdmin
|   /phpMyAdmin-2.6.2-rc1/: phpMyAdmin
|   /phpMyAdmin-2.6.2-beta1/: phpMyAdmin
|   /phpMyAdmin-2.6.2/: phpMyAdmin
|   /phpMyAdmin-2.6.2-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.3/: phpMyAdmin
|   /phpMyAdmin-2.6.3-rc1/: phpMyAdmin
|   /phpMyAdmin-2.6.3-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.4-rc1/: phpMyAdmin
|   /phpMyAdmin-2.6.4-pl1/: phpMyAdmin
|   /phpMyAdmin-2.6.4-pl2/: phpMyAdmin
|   /phpMyAdmin-2.6.4-pl3/: phpMyAdmin
|   /phpMyAdmin-2.6.4-pl4/: phpMyAdmin
|   /phpMyAdmin-2.6.4/: phpMyAdmin
|   /phpMyAdmin-2.7.0-beta1/: phpMyAdmin
|   /phpMyAdmin-2.7.0-rc1/: phpMyAdmin
|   /phpMyAdmin-2.7.0-pl1/: phpMyAdmin
|   /phpMyAdmin-2.7.0-pl2/: phpMyAdmin
|   /phpMyAdmin-2.7.0/: phpMyAdmin
|   /phpMyAdmin-2.8.0-beta1/: phpMyAdmin
|   /phpMyAdmin-2.8.0-rc1/: phpMyAdmin
|   /phpMyAdmin-2.8.0-rc2/: phpMyAdmin
|   /phpMyAdmin-2.8.0/: phpMyAdmin
|   /phpMyAdmin-2.8.0.1/: phpMyAdmin
|   /phpMyAdmin-2.8.0.2/: phpMyAdmin
|   /phpMyAdmin-2.8.0.3/: phpMyAdmin
|   /phpMyAdmin-2.8.0.4/: phpMyAdmin
|   /phpMyAdmin-2.8.1-rc1/: phpMyAdmin
|   /phpMyAdmin-2.8.1/: phpMyAdmin
|   /phpMyAdmin-2.8.2/: phpMyAdmin
|   /sqlmanager/: phpMyAdmin
|   /php-myadmin/: phpMyAdmin
|   /phpmy-admin/: phpMyAdmin
|   /mysqladmin/: phpMyAdmin
|   /mysql-admin/: phpMyAdmin
|   /websql/: phpMyAdmin
|   /_phpmyadmin/: phpMyAdmin
|   /srvnam.htm: Lotus Domino
|   /Pages/Default.aspx: MS Sharepoint
|   /_admin/operations.aspx: MS Sharepoint
|   /_layouts/viewlsts.aspx: MS Sharepoint
|   /forms/allitems.aspx: MS Sharepoint
|   /forms/webfldr.aspx: MS Sharepoint
|   /forms/mod-view.aspx: MS Sharepoint
|   /forms/my-sub.aspx: MS Sharepoint
|   /pages/categoryresults.aspx: MS Sharepoint
|   /categories/viewcategory.aspx: MS Sharepoint
|   /editdocs.aspx: MS Sharepoint
|   /workflowtasks/allitems.aspx: MS Sharepoint
|   /lists/tasks/: MS Sharepoint
|   /categories/allcategories.aspx: MS Sharepoint
|   /categories/SOMEOTHERDIR/allcategories.aspx: MS Sharepoint
|   /mycategories.aspx: MS Sharepoint
|   /lists/: MS Sharepoint
|   /lists/allitems.aspx: MS Sharepoint
|   /lists/default.aspx: MS Sharepoint
|   /lists/allposts.aspx: MS Sharepoint
|   /lists/archive.aspx: MS Sharepoint
|   /lists/byauthor.aspx: MS Sharepoint
|   /lists/calendar.aspx: MS Sharepoint
|   /lists/mod-view.aspx: MS Sharepoint
|   /lists/myposts.aspx: MS Sharepoint
|   /lists/my-sub.aspx: MS Sharepoint
|   /lists/allcomments.aspx: MS Sharepoint
|   /lists/mycomments.aspx: MS Sharepoint
|   /_layouts/userdisp.aspx: MS Sharepoint
|   /_layouts/help.aspx: MS Sharepoint
|   /_layouts/download.aspx: MS Sharepoint
|   /projectserver/Home/HomePage.asp: MS Project Server
|   /projectserver/Tasks/Taskspage.asp: MS Project Server
|   /exchweb/bin/auth/owalogon.asp: Outlook Web Access
|   /owa/: Outlook Web Access
|   /tsweb/: Remote Desktop Web Connection
|   /reportserver/: Microsoft SQL Report Service
|   /HW_logo.html: Huawei HG 530
|   /_vti_bin/: Frontpage file or folder
|   /_vti_cnf/: Frontpage file or folder
|   /_vti_log/: Frontpage file or folder
|   /_vti_pvt/: Frontpage file or folder
|   /_vti_txt/: Frontpage file or folder
|   /postinfo.html: Frontpage file or folder
|   /_vti_pvt/_x_todo.htm: Frontpage file or folder
|   /_vti_pvt/_x_todoh.htm: Frontpage file or folder
|   /.svn/: Subversion folder
|   /cwhp/auditLog.do?file=..\..\..\..\..\..\..\boot.ini: Possible CiscoWorks (CuOM 8.0 and 8.5) Directory traversal (CVE-2011-0966) (Windows)
|   /cwhp/auditLog.do?file=..\..\..\..\..\..\..\Program%20Files\CSCOpx\MDC\Tomcat\webapps\triveni\WEB-INF\classes\schedule.properties: Possible CiscoWorks (CuOM 8.0 and 8.5) Directory traversal (CVE-2011-0966) (Windows)
|   /cwhp/auditLog.do?file=..\..\..\..\..\..\..\Program%20Files\CSCOpx\lib\classpath\com\cisco\nm\cmf\dbservice2\DBServer.properties: Possible CiscoWorks (CuOM 8.0 and 8.5) Directory traversal (CVE-2011-0966) (Windows)
|   /cwhp/auditLog.do?file=..\..\..\..\..\..\..\Program%20Files\CSCOpx\log\dbpwdChange.log: Possible CiscoWorks (CuOM 8.0 and 8.5) Directory traversal (CVE-2011-0966) (Windows)
|   /Info.live.htm: Possible DD-WRT router Information Disclosure (BID 45598)
|   /plugins/PluginController.php?path=..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fwindows%2fwin.ini%00: OrangeHRM 2.6.3 Local File Inclusion
|   /wp-includes/js/scriptaculous/sound.js: Wordpress version 2.3 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-includes/js/codepress/codepress.js: Wordpress version 2.8 found.
|   /readme.html: Interesting, a readme.
|   /pligg/readme.html: Interesting, a readme.
|   /digg/readme.html: Interesting, a readme.
|   /news/readme.html: Interesting, a readme.
|   /tinymcpuk/filemanager/browser.html: CMS Lokomedia
|   /admin/libraries/ajaxfilemanager/ajaxfilemanager.php: Log1 CMS
|   /scripts/fckeditor/editor/filemanager/connectors/test.html: Digitalus CMS/FCKEditor File upload
|   /scripts/fckeditor/editor/filemanager/connectors/uploadtest.html: Digitalus CMS/FCKEditor File upload
|   /fckeditor/editor/filemanager/connectors/test.html: phpmotion/FCKeditor File upload
|   /fckeditor/editor/filemanager/upload/test.html: Geeklog/FCKeditor File upload
|   /admin/view/javascript/fckeditor/editor/filemanager/connectors/test.html: OpenCart/FCKeditor File upload
|   /fckeditor/editor/filemanager/connectors/php/config.php: DM File Manager/FCKeditor File upload
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/php/connector.php: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/asp/connector.asp: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/aspx/connector.aspx: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/cfm/connector.cfm: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/lasso/connector.lasso: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/perl/connector.cgi: PHPnuke/Remote File Download
|   /includes/FCKeditor/editor/filemanager/browser/default/connectors/py/connector.py: PHPnuke/Remote File Download
|   /FCKEditor/editor/filemanager/browser/default/connectors/test.html: EgO or osCMax/FCKeditor File upload
|   /admin/includes/tiny_mce/plugins/tinybrowser/upload.php: CompactCMS or B-Hind CMS/FCKeditor File upload
|   /Backstage/Components/FreeTextBox/ftb.imagegallery.aspx: Luftguitar CMS/File upload
|   /_plugin/fckeditor/editor/filemanager/connectors/test.html: SweetRice/FCKeditor File upload
|   /html/news_fckeditor/editor/filemanager/upload/php/upload.php: cardinalCms/FCKeditor File upload
|   /fckeditor/editor/filemanager/connectors/test.html: LightNEasy/FCKeditor File upload
|   /admin/includes/FCKeditor/editor/filemanager/upload/test.html: ASP Simple Blog / FCKeditor File Upload
|   /editor/editor/filemanager/upload/test.html: Tadbir / File Upload
|   /Providers/HtmlEditorProviders/Fck/fcklinkgallery.aspx: DotNetNuke / File Upload
|   /assetmanager/assetmanager.asp: Asset Manager/Remote File upload
|   /admin/jscript/upload.html: Lizard Cart/Remote File upload
|   /admin/jscript/upload.asp: Lizard Cart/Remote File upload
|   /db/: BlogWorx Database
|   /admin/environment.xml: Moodle files
|   /nfservlets/servlet/SPSRouterServlet/: netForensics
|   /0/: Potentially interesting folder
|   /1/: Potentially interesting folder
|   /2/: Potentially interesting folder
|   /3/: Potentially interesting folder
|   /4/: Potentially interesting folder
|   /5/: Potentially interesting folder
|   /6/: Potentially interesting folder
|   /7/: Potentially interesting folder
|   /8/: Potentially interesting folder
|   /9/: Potentially interesting folder
|   /10/: Potentially interesting folder
|   /a/: Potentially interesting folder
|   /b/: Potentially interesting folder
|   /c/: Potentially interesting folder
|   /d/: Potentially interesting folder
|   /e/: Potentially interesting folder
|   /f/: Potentially interesting folder
|   /g/: Potentially interesting folder
|   /h/: Potentially interesting folder
|   /i/: Potentially interesting folder
|   /j/: Potentially interesting folder
|   /k/: Potentially interesting folder
|   /l/: Potentially interesting folder
|   /m/: Potentially interesting folder
|   /n/: Potentially interesting folder
|   /o/: Potentially interesting folder
|   /p/: Potentially interesting folder
|   /q/: Potentially interesting folder
|   /r/: Potentially interesting folder
|   /s/: Potentially interesting folder
|   /t/: Potentially interesting folder
|   /u/: Potentially interesting folder
|   /v/: Potentially interesting folder
|   /w/: Potentially interesting folder
|   /x/: Potentially interesting folder
|   /y/: Potentially interesting folder
|   /z/: Potentially interesting folder
|   /acceso/: Potentially interesting folder
|   /access/: Potentially interesting folder
|   /accesswatch/: Potentially interesting folder
|   /acciones/: Potentially interesting folder
|   /account/: Potentially interesting folder
|   /accounting/: Potentially interesting folder
|   /active/: Potentially interesting folder
|   /activex/: Potentially interesting folder
|   /admcgi/: Potentially interesting folder
|   /admisapi/: Potentially interesting folder
|   /AdvWebAdmin/: Potentially interesting folder
|   /agentes/: Potentially interesting folder
|   /Agent/: Potentially interesting folder
|   /Agents/: Potentially interesting folder
|   /AlbumArt_/: Potentially interesting folder
|   /AlbumArt/: Potentially interesting folder
|   /Album/: Potentially interesting folder
|   /allow/: Potentially interesting folder
|   /analog/: Potentially interesting folder
|   /anthill/: Potentially interesting folder
|   /apache/: Potentially interesting folder
|   /app/: Potentially interesting folder
|   /applets/: Potentially interesting folder
|   /appl/: Potentially interesting folder
|   /application/: Potentially interesting folder
|   /applications/: Potentially interesting folder
|   /applmgr/: Potentially interesting folder
|   /apply/: Potentially interesting folder
|   /appsec/: Potentially interesting folder
|   /apps/: Potentially interesting folder
|   /archive/: Potentially interesting folder
|   /archives/: Potentially interesting folder
|   /ar/: Potentially interesting folder
|   /asa/: Potentially interesting folder
|   /asp/: Potentially interesting folder
|   /atc/: Potentially interesting folder
|   /aut/: Potentially interesting folder
|   /authadmin/: Potentially interesting folder
|   /auth/: Potentially interesting folder
|   /author/: Potentially interesting folder
|   /authors/: Potentially interesting folder
|   /aw/: Potentially interesting folder
|   /ayuda/: Potentially interesting folder
|   /b2-include/: Potentially interesting folder
|   /backend/: Potentially interesting folder
|   /bad/: Potentially interesting folder
|   /banca/: Potentially interesting folder
|   /banco/: Potentially interesting folder
|   /bank/: Potentially interesting folder
|   /banner01/: Potentially interesting folder
|   /banner/: Potentially interesting folder
|   /banners/: Potentially interesting folder
|   /bar/: Potentially interesting folder
|   /batch/: Potentially interesting folder
|   /bb-dnbd/: Potentially interesting folder
|   /bbv/: Potentially interesting folder
|   /bdata/: Potentially interesting folder
|   /bdatos/: Potentially interesting folder
|   /beta/: Potentially interesting folder
|   /billpay/: Potentially interesting folder
|   /bin/: Potentially interesting folder
|   /binaries/: Potentially interesting folder
|   /binary/: Potentially interesting folder
|   /boadmin/: Potentially interesting folder
|   /boot/: Potentially interesting folder
|   /bottom/: Potentially interesting folder
|   /browse/: Potentially interesting folder
|   /browser/: Potentially interesting folder
|   /bsd/: Potentially interesting folder
|   /btauxdir/: Potentially interesting folder
|   /bug/: Potentially interesting folder
|   /bugs/: Potentially interesting folder
|   /bugzilla/: Potentially interesting folder
|   /buy/: Potentially interesting folder
|   /buynow/: Potentially interesting folder
|   /cached/: Potentially interesting folder
|   /cache/: Potentially interesting folder
|   /cache-stats/: Potentially interesting folder
|   /caja/: Potentially interesting folder
|   /card/: Potentially interesting folder
|   /cards/: Potentially interesting folder
|   /cart/: Potentially interesting folder
|   /cash/: Potentially interesting folder
|   /caspsamp/: Potentially interesting folder
|   /catalog/: Potentially interesting folder
|   /cbi-bin/: Potentially interesting folder
|   /ccard/: Potentially interesting folder
|   /ccards/: Potentially interesting folder
|   /cd-cgi/: Potentially interesting folder
|   /cd/: Potentially interesting folder
|   /cdrom/: Potentially interesting folder
|   /ce_html/: Potentially interesting folder
|   /cert/: Potentially interesting folder
|   /certificado/: Potentially interesting folder
|   /certificate/: Potentially interesting folder
|   /cfappman/: Potentially interesting folder
|   /cfdocs/: Potentially interesting folder
|   /cfide/: Potentially interesting folder
|   /cgi-914/: Potentially interesting folder
|   /cgi-915/: Potentially interesting folder
|   /cgi-auth/: Potentially interesting folder
|   /cgi-bin2/: Potentially interesting folder
|   /cgi-bin/: Potentially interesting folder
|   /cgibin/: Potentially interesting folder
|   /cgi.cgi/: Potentially interesting folder
|   /cgi-csc/: Potentially interesting folder
|   /cgi-exe/: Potentially interesting folder
|   /cgi/: Potentially interesting folder
|   /cgi-home/: Potentially interesting folder
|   /cgi-lib/: Potentially interesting folder
|   /cgilib/: Potentially interesting folder
|   /cgi-local/: Potentially interesting folder
|   /cgi-perl/: Potentially interesting folder
|   /cgi-scripts/: Potentially interesting folder
|   /cgiscripts/: Potentially interesting folder
|   /cgis/: Potentially interesting folder
|   /cgi-shl/: Potentially interesting folder
|   /cgi-shop/: Potentially interesting folder
|   /cgi-sys/: Potentially interesting folder
|   /cgi-weddico/: Potentially interesting folder
|   /cgi-win/: Potentially interesting folder
|   /cgiwin/: Potentially interesting folder
|   /class/: Potentially interesting folder
|   /classes/: Potentially interesting folder
|   /cliente/: Potentially interesting folder
|   /clientes/: Potentially interesting folder
|   /client/: Potentially interesting folder
|   /clients/: Potentially interesting folder
|   /cm/: Potentially interesting folder
|   /cobalt-images/: Potentially interesting folder
|   /code/: Potentially interesting folder
|   /com/: Potentially interesting folder
|   /comments/: Potentially interesting folder
|   /common/: Potentially interesting folder
|   /communicator/: Potentially interesting folder
|   /company/: Potentially interesting folder
|   /comp/: Potentially interesting folder
|   /compra/: Potentially interesting folder
|   /compras/: Potentially interesting folder
|   /compressed/: Potentially interesting folder
|   /conecta/: Potentially interesting folder
|   /conf/: Potentially interesting folder
|   /config/: Potentially interesting folder
|   /configs/: Potentially interesting folder
|   /configure/: Potentially interesting folder
|   /connect/: Potentially interesting folder
|   /console/: Potentially interesting folder
|   /contact/: Potentially interesting folder
|   /contacts/: Potentially interesting folder
|   /content/: Potentially interesting folder
|   /content.ie5/: Potentially interesting folder
|   /controlpanel/: Potentially interesting folder
|   /core/: Potentially interesting folder
|   /corp/: Potentially interesting folder
|   /correo/: Potentially interesting folder
|   /counter/: Potentially interesting folder
|   /credit/: Potentially interesting folder
|   /cron/: Potentially interesting folder
|   /crons/: Potentially interesting folder
|   /crypto/: Potentially interesting folder
|   /CS/: Potentially interesting folder
|   /csr/: Potentially interesting folder
|   /css/: Potentially interesting folder
|   /cuenta/: Potentially interesting folder
|   /cuentas/: Potentially interesting folder
|   /currency/: Potentially interesting folder
|   /cust/: Potentially interesting folder
|   /customer/: Potentially interesting folder
|   /customers/: Potentially interesting folder
|   /custom/: Potentially interesting folder
|   /CVS/: Potentially interesting folder
|   /cvsweb/: Potentially interesting folder
|   /cybercash/: Potentially interesting folder
|   /darkportal/: Potentially interesting folder
|   /database/: Potentially interesting folder
|   /databases/: Potentially interesting folder
|   /datafiles/: Potentially interesting folder
|   /dat/: Potentially interesting folder
|   /data/: Potentially interesting folder
|   /dato/: Potentially interesting folder
|   /datos/: Potentially interesting folder
|   /db/: Potentially interesting folder
|   /dbase/: Potentially interesting folder
|   /dcforum/: Potentially interesting folder
|   /ddreport/: Potentially interesting folder
|   /ddrint/: Potentially interesting folder
|   /debug/: Potentially interesting folder
|   /debugs/: Potentially interesting folder
|   /default/: Potentially interesting folder
|   /deleted/: Potentially interesting folder
|   /delete/: Potentially interesting folder
|   /demoauct/: Potentially interesting folder
|   /demomall/: Potentially interesting folder
|   /demo/: Potentially interesting folder
|   /demos/: Potentially interesting folder
|   /demouser/: Potentially interesting folder
|   /deny/: Potentially interesting folder
|   /derived/: Potentially interesting folder
|   /design/: Potentially interesting folder
|   /dev/: Potentially interesting folder
|   /devel/: Potentially interesting folder
|   /development/: Potentially interesting folder
|   /directories/: Potentially interesting folder
|   /directory/: Potentially interesting folder
|   /directorymanager/: Potentially interesting folder
|   /dir/: Potentially interesting folder
|   /dl/: Potentially interesting folder
|   /dm/: Potentially interesting folder
|   /DMR/: Potentially interesting folder
|   /dms0/: Potentially interesting folder
|   /dmsdump/: Potentially interesting folder
|   /dms/: Potentially interesting folder
|   /dnn/: Potentially interesting folder
|   /doc1/: Potentially interesting folder
|   /doc/: Potentially interesting folder
|   /doc-html/: Potentially interesting folder
|   /docs1/: Potentially interesting folder
|   /docs/: Potentially interesting folder
|   /DocuColor/: Potentially interesting folder
|   /documentation/: Potentially interesting folder
|   /document/: Potentially interesting folder
|   /documents/: Potentially interesting folder
|   /dotnetnuke/: Potentially interesting folder
|   /down/: Potentially interesting folder
|   /download/: Potentially interesting folder
|   /downloads/: Potentially interesting folder
|   /dump/: Potentially interesting folder
|   /durep/: Potentially interesting folder
|   /easylog/: Potentially interesting folder
|   /eforum/: Potentially interesting folder
|   /ejemplo/: Potentially interesting folder
|   /ejemplos/: Potentially interesting folder
|   /emailclass/: Potentially interesting folder
|   /email/: Potentially interesting folder
|   /employees/: Potentially interesting folder
|   /empoyees/: Potentially interesting folder
|   /empris/: Potentially interesting folder
|   /enter/: Potentially interesting folder
|   /envia/: Potentially interesting folder
|   /enviamail/: Potentially interesting folder
|   /error/: Potentially interesting folder
|   /errors/: Potentially interesting folder
|   /es/: Potentially interesting folder
|   /estmt/: Potentially interesting folder
|   /etc/: Potentially interesting folder
|   /etcpasswd/: Potentially interesting folder
|   /excel/: Potentially interesting folder
|   /exc/: Potentially interesting folder
|   /exchange/: Potentially interesting folder
|   /exchweb/: Potentially interesting folder
|   /exec/: Potentially interesting folder
|   /exe/: Potentially interesting folder
|   /exit/: Potentially interesting folder
|   /export/: Potentially interesting folder
|   /external/: Potentially interesting folder
|   /extranet/: Potentially interesting folder
|   /failure/: Potentially interesting folder
|   /fbsd/: Potentially interesting folder
|   /fcgi-bin/: Potentially interesting folder
|   /fcgi/: Potentially interesting folder
|   /features/: Potentially interesting folder
|   /fileadmin/: Potentially interesting folder
|   /file/: Potentially interesting folder
|   /filemanager/: Potentially interesting folder
|   /files/: Potentially interesting folder
|   /find/: Potentially interesting folder
|   /flash/: Potentially interesting folder
|   /foldoc/: Potentially interesting folder
|   /foobar/: Potentially interesting folder
|   /foo/: Potentially interesting folder
|   /form/: Potentially interesting folder
|   /forms/: Potentially interesting folder
|   /formsmgr/: Potentially interesting folder
|   /form-totaller/: Potentially interesting folder
|   /foto/: Potentially interesting folder
|   /fotos/: Potentially interesting folder
|   /fpadmin/: Potentially interesting folder
|   /fpclass/: Potentially interesting folder
|   /fpdb/: Potentially interesting folder
|   /fpe/: Potentially interesting folder
|   /framesets/: Potentially interesting folder
|   /frames/: Potentially interesting folder
|   /frontpage/: Potentially interesting folder
|   /ftp/: Potentially interesting folder
|   /ftproot/: Potentially interesting folder
|   /func/: Potentially interesting folder
|   /function/: Potentially interesting folder
|   /functions/: Potentially interesting folder
|   /fun/: Potentially interesting folder
|   /general/: Potentially interesting folder
|   /gfx/: Potentially interesting folder
|   /gif/: Potentially interesting folder
|   /gifs/: Potentially interesting folder
|   /global/: Potentially interesting folder
|   /globals/: Potentially interesting folder
|   /good/: Potentially interesting folder
|   /graphics/: Potentially interesting folder
|   /grocery/: Potentially interesting folder
|   /guestbook/: Potentially interesting folder
|   /guest/: Potentially interesting folder
|   /guests/: Potentially interesting folder
|   /GXApp/: Potentially interesting folder
|   /HB/: Potentially interesting folder
|   /HBTemplates/: Potentially interesting folder
|   /helpdesk/: Potentially interesting folder
|   /help/: Potentially interesting folder
|   /hidden/: Potentially interesting folder
|   /hide/: Potentially interesting folder
|   /hitmatic/: Potentially interesting folder
|   /hit_tracker/: Potentially interesting folder
|   /hlstats/: Potentially interesting folder
|   /home/: Potentially interesting folder
|   /hosted/: Potentially interesting folder
|   /host/: Potentially interesting folder
|   /hostingcontroller/: Potentially interesting folder
|   /hosting/: Potentially interesting folder
|   /hp/: Potentially interesting folder
|   /htbin/: Potentially interesting folder
|   /htdocs/: Potentially interesting folder
|   /ht/: Potentially interesting folder
|   /htm/: Potentially interesting folder
|   /html/: Potentially interesting folder
|   /http/: Potentially interesting folder
|   /https/: Potentially interesting folder
|   /hyperstat/: Potentially interesting folder
|   /i18n/: Potentially interesting folder
|   /ibank/: Potentially interesting folder
|   /ibill/: Potentially interesting folder
|   /IBMWebAS/: Potentially interesting folder
|   /icons/: Potentially interesting folder
|   /idea/: Potentially interesting folder
|   /ideas/: Potentially interesting folder
|   /I/: Potentially interesting folder
|   /iisadmin/: Potentially interesting folder
|   /image/: Potentially interesting folder
|   /images/: Potentially interesting folder
|   /imagenes/: Potentially interesting folder
|   /imagery/: Potentially interesting folder
|   /img/: Potentially interesting folder
|   /imp/: Potentially interesting folder
|   /import/: Potentially interesting folder
|   /impreso/: Potentially interesting folder
|   /inc/: Potentially interesting folder
|   /include/: Potentially interesting folder
|   /includes/: Potentially interesting folder
|   /incoming/: Potentially interesting folder
|   /index/: Potentially interesting folder
|   /inet/: Potentially interesting folder
|   /inf/: Potentially interesting folder
|   /info/: Potentially interesting folder
|   /information/: Potentially interesting folder
|   /in/: Potentially interesting folder
|   /ingresa/: Potentially interesting folder
|   /ingreso/: Potentially interesting folder
|   /install/: Potentially interesting folder
|   /internal/: Potentially interesting folder
|   /internet/: Potentially interesting folder
|   /intranet/: Potentially interesting folder
|   /inventory/: Potentially interesting folder
|   /invitado/: Potentially interesting folder
|   /isapi/: Potentially interesting folder
|   /j2ee/: Potentially interesting folder
|   /japidoc/: Potentially interesting folder
|   /java/: Potentially interesting folder
|   /javascript/: Potentially interesting folder
|   /javasdk/: Potentially interesting folder
|   /javatest/: Potentially interesting folder
|   /jave/: Potentially interesting folder
|   /JBookIt/: Potentially interesting folder
|   /jdbc/: Potentially interesting folder
|   /job/: Potentially interesting folder
|   /jrun/: Potentially interesting folder
|   /jsa/: Potentially interesting folder
|   /jscript/: Potentially interesting folder
|   /jserv/: Potentially interesting folder
|   /js/: Potentially interesting folder
|   /jslib/: Potentially interesting folder
|   /jsp/: Potentially interesting folder
|   /junk/: Potentially interesting folder
|   /kiva/: Potentially interesting folder
|   /known/: Potentially interesting folder
|   /labs/: Potentially interesting folder
|   /lcgi/: Potentially interesting folder
|   /lib/: Potentially interesting folder
|   /libraries/: Potentially interesting folder
|   /library/: Potentially interesting folder
|   /libro/: Potentially interesting folder
|   /license/: Potentially interesting folder
|   /licenses/: Potentially interesting folder
|   /links/: Potentially interesting folder
|   /linux/: Potentially interesting folder
|   /loader/: Potentially interesting folder
|   /local/: Potentially interesting folder
|   /location/: Potentially interesting folder
|   /locations/: Potentially interesting folder
|   /logfile/: Potentially interesting folder
|   /logfiles/: Potentially interesting folder
|   /logger/: Potentially interesting folder
|   /logg/: Potentially interesting folder
|   /logging/: Potentially interesting folder
|   /logon/: Potentially interesting folder
|   /logout/: Potentially interesting folder
|   /lost+found/: Potentially interesting folder
|   /mailman/: Potentially interesting folder
|   /mailroot/: Potentially interesting folder
|   /makefile/: Potentially interesting folder
|   /manage/: Potentially interesting folder
|   /management/: Potentially interesting folder
|   /man/: Potentially interesting folder
|   /manual/: Potentially interesting folder
|   /map/: Potentially interesting folder
|   /maps/: Potentially interesting folder
|   /marketing/: Potentially interesting folder
|   /member/: Potentially interesting folder
|   /members/: Potentially interesting folder
|   /mem_bin/: Potentially interesting folder
|   /mem/: Potentially interesting folder
|   /message/: Potentially interesting folder
|   /messaging/: Potentially interesting folder
|   /metacart/: Potentially interesting folder
|   /microsoft/: Potentially interesting folder
|   /misc/: Potentially interesting folder
|   /mkstats/: Potentially interesting folder
|   /mod/: Potentially interesting folder
|   /module/: Potentially interesting folder
|   /modules/: Potentially interesting folder
|   /movimientos/: Potentially interesting folder
|   /mpcgi/: Potentially interesting folder
|   /mqseries/: Potentially interesting folder
|   /msfpe/: Potentially interesting folder
|   /ms/: Potentially interesting folder
|   /msql/: Potentially interesting folder
|   /Msword/: Potentially interesting folder
|   /mxhtml/: Potentially interesting folder
|   /mxportal/: Potentially interesting folder
|   /my/: Potentially interesting folder
|   /My%20Shared%20Folder/: Potentially interesting folder
|   /mysql_admin/: Potentially interesting folder
|   /mysql/: Potentially interesting folder
|   /name/: Potentially interesting folder
|   /names/: Potentially interesting folder
|   /ncadmin/: Potentially interesting folder
|   /nchelp/: Potentially interesting folder
|   /netbasic/: Potentially interesting folder
|   /netcat/: Potentially interesting folder
|   /NetDynamic/: Potentially interesting folder
|   /NetDynamics/: Potentially interesting folder
|   /net/: Potentially interesting folder
|   /netmagstats/: Potentially interesting folder
|   /netscape/: Potentially interesting folder
|   /netshare/: Potentially interesting folder
|   /nettracker/: Potentially interesting folder
|   /network/: Potentially interesting folder
|   /new/: Potentially interesting folder
|   /news/: Potentially interesting folder
|   /News/: Potentially interesting folder
|   /nextgeneration/: Potentially interesting folder
|   /nl/: Potentially interesting folder
|   /notes/: Potentially interesting folder
|   /noticias/: Potentially interesting folder
|   /NSearch/: Potentially interesting folder
|   /objects/: Potentially interesting folder
|   /odbc/: Potentially interesting folder
|   /officescan/: Potentially interesting folder
|   /ojspdemos/: Potentially interesting folder
|   /old_files/: Potentially interesting folder
|   /oldfiles/: Potentially interesting folder
|   /old/: Potentially interesting folder
|   /oprocmgr-service/: Potentially interesting folder
|   /oprocmgr-status/: Potentially interesting folder
|   /oracle/: Potentially interesting folder
|   /oradata/: Potentially interesting folder
|   /order/: Potentially interesting folder
|   /orders/: Potentially interesting folder
|   /os/: Potentially interesting folder
|   /out/: Potentially interesting folder
|   /outgoing/: Potentially interesting folder
|   /owners/: Potentially interesting folder
|   /ows-bin/: Potentially interesting folder
|   /page/: Potentially interesting folder
|   /_pages/: Potentially interesting folder
|   /pages/: Potentially interesting folder
|   /partner/: Potentially interesting folder
|   /partners/: Potentially interesting folder
|   /passport/: Potentially interesting folder
|   /password/: Potentially interesting folder
|   /passwords/: Potentially interesting folder
|   /path/: Potentially interesting folder
|   /payment/: Potentially interesting folder
|   /payments/: Potentially interesting folder
|   /pccsmysqladm/: Potentially interesting folder
|   /PDG_Cart/: Potentially interesting folder
|   /perl5/: Potentially interesting folder
|   /perl/: Potentially interesting folder
|   /personal/: Potentially interesting folder
|   /pforum/: Potentially interesting folder
|   /phorum/: Potentially interesting folder
|   /phpBB/: Potentially interesting folder
|   /php_classes/: Potentially interesting folder
|   /phpclassifieds/: Potentially interesting folder
|   /php/: Potentially interesting folder
|   /phpimageview/: Potentially interesting folder
|   /phpnuke/: Potentially interesting folder
|   /phpPhotoAlbum/: Potentially interesting folder
|   /phpprojekt/: Potentially interesting folder
|   /phpSecurePages/: Potentially interesting folder
|   /pics/: Potentially interesting folder
|   /pictures/: Potentially interesting folder
|   /pike/: Potentially interesting folder
|   /piranha/: Potentially interesting folder
|   /pls/: Potentially interesting folder
|   /plsql/: Potentially interesting folder
|   /plssampleadmin_/: Potentially interesting folder
|   /plssampleadmin/: Potentially interesting folder
|   /plssampleadmin_help/: Potentially interesting folder
|   /plssample/: Potentially interesting folder
|   /poll/: Potentially interesting folder
|   /polls/: Potentially interesting folder
|   /porn/: Potentially interesting folder
|   /portal/: Potentially interesting folder
|   /portals/: Potentially interesting folder
|   /postgres/: Potentially interesting folder
|   /postnuke/: Potentially interesting folder
|   /ppwb/: Potentially interesting folder
|   /printer/: Potentially interesting folder
|   /printers/: Potentially interesting folder
|   /privacy/: Potentially interesting folder
|   /privado/: Potentially interesting folder
|   /_private/: Potentially interesting folder
|   /private/: Potentially interesting folder
|   /priv/: Potentially interesting folder
|   /prod/: Potentially interesting folder
|   /projectserver/: Potentially interesting folder
|   /protected/: Potentially interesting folder
|   /proxy/: Potentially interesting folder
|   /prueba/: Potentially interesting folder
|   /pruebas/: Potentially interesting folder
|   /prv/: Potentially interesting folder
|   /pub/: Potentially interesting folder
|   /_public/: Potentially interesting folder
|   /public/: Potentially interesting folder
|   /publica/: Potentially interesting folder
|   /publicar/: Potentially interesting folder
|   /publico/: Potentially interesting folder
|   /publish/: Potentially interesting folder
|   /purchase/: Potentially interesting folder
|   /purchases/: Potentially interesting folder
|   /pw/: Potentially interesting folder
|   /python/: Potentially interesting folder
|   /random_banner/: Potentially interesting folder
|   /rdp/: Potentially interesting folder
|   /Readme/: Potentially interesting folder
|   /recycler/: Potentially interesting folder
|   /registered/: Potentially interesting folder
|   /register/: Potentially interesting folder
|   /registry/: Potentially interesting folder
|   /remote/: Potentially interesting folder
|   /remove/: Potentially interesting folder
|   /report/: Potentially interesting folder
|   /reports/: Potentially interesting folder
|   /reseller/: Potentially interesting folder
|   /restricted/: Potentially interesting folder
|   /retail/: Potentially interesting folder
|   /reveal/: Potentially interesting folder
|   /reviews/: Potentially interesting folder
|   /ROADS/: Potentially interesting folder
|   /robot/: Potentially interesting folder
|   /robots/: Potentially interesting folder
|   /root/: Potentially interesting folder
|   /rsrc/: Potentially interesting folder
|   /ruby/: Potentially interesting folder
|   /sales/: Potentially interesting folder
|   /save/: Potentially interesting folder
|   /script/: Potentially interesting folder
|   /ScriptLibrary/: Potentially interesting folder
|   /scripts/: Potentially interesting folder
|   /search/: Potentially interesting folder
|   /search-ui/: Potentially interesting folder
|   /sec/: Potentially interesting folder
|   /secret/: Potentially interesting folder
|   /secured/: Potentially interesting folder
|   /secure/: Potentially interesting folder
|   /security/: Potentially interesting folder
|   /sell/: Potentially interesting folder
|   /server/: Potentially interesting folder
|   /server-info/: Potentially interesting folder
|   /servers/: Potentially interesting folder
|   /server_stats/: Potentially interesting folder
|   /serverstats/: Potentially interesting folder
|   /server-status/: Potentially interesting folder
|   /service/: Potentially interesting folder
|   /services/: Potentially interesting folder
|   /servicio/: Potentially interesting folder
|   /servicios/: Potentially interesting folder
|   /servlet/: Potentially interesting folder
|   /servlets/: Potentially interesting folder
|   /session/: Potentially interesting folder
|   /setup/: Potentially interesting folder
|   /shared/: Potentially interesting folder
|   /sharedtemplates/: Potentially interesting folder
|   /share/: Potentially interesting folder
|   /shell-cgi/: Potentially interesting folder
|   /shipping/: Potentially interesting folder
|   /shop/: Potentially interesting folder
|   /shopper/: Potentially interesting folder
|   /show/: Potentially interesting folder
|   /SilverStream/: Potentially interesting folder
|   /siteadmin/: Potentially interesting folder
|   /site/: Potentially interesting folder
|   /sitemgr/: Potentially interesting folder
|   /siteminderagent/: Potentially interesting folder
|   /siteminder/: Potentially interesting folder
|   /siteserver/: Potentially interesting folder
|   /sites/: Potentially interesting folder
|   /sitestats/: Potentially interesting folder
|   /siteupdate/: Potentially interesting folder
|   /smreports/: Potentially interesting folder
|   /smreportsviewer/: Potentially interesting folder
|   /soapdocs/: Potentially interesting folder
|   /soap/: Potentially interesting folder
|   /software/: Potentially interesting folder
|   /solaris/: Potentially interesting folder
|   /source/: Potentially interesting folder
|   /sql/: Potentially interesting folder
|   /squid/: Potentially interesting folder
|   /src/: Potentially interesting folder
|   /srchadm/: Potentially interesting folder
|   /ssi/: Potentially interesting folder
|   /ssl/: Potentially interesting folder
|   /sslkeys/: Potentially interesting folder
|   /staff/: Potentially interesting folder
|   /state/: Potentially interesting folder
|   /stat/: Potentially interesting folder
|   /statistic/: Potentially interesting folder
|   /statistics/: Potentially interesting folder
|   /stats-bin-p/: Potentially interesting folder
|   /stats/: Potentially interesting folder
|   /stats_old/: Potentially interesting folder
|   /status/: Potentially interesting folder
|   /storage/: Potentially interesting folder
|   /StoreDB/: Potentially interesting folder
|   /store/: Potentially interesting folder
|   /storemgr/: Potentially interesting folder
|   /stronghold-info/: Potentially interesting folder
|   /stronghold-status/: Potentially interesting folder
|   /stuff/: Potentially interesting folder
|   /style/: Potentially interesting folder
|   /styles/: Potentially interesting folder
|   /stylesheet/: Potentially interesting folder
|   /stylesheets/: Potentially interesting folder
|   /subir/: Potentially interesting folder
|   /sun/: Potentially interesting folder
|   /super_stats/: Potentially interesting folder
|   /supplier/: Potentially interesting folder
|   /suppliers/: Potentially interesting folder
|   /supply/: Potentially interesting folder
|   /supporter/: Potentially interesting folder
|   /support/: Potentially interesting folder
|   /sysadmin/: Potentially interesting folder
|   /sysbackup/: Potentially interesting folder
|   /sys/: Potentially interesting folder
|   /system/: Potentially interesting folder
|   /systems/: Potentially interesting folder
|   /tar/: Potentially interesting folder
|   /target/: Potentially interesting folder
|   /tarjetas/: Potentially interesting folder
|   /tech/: Potentially interesting folder
|   /technote/: Potentially interesting folder
|   /te_html/: Potentially interesting folder
|   /temp/: Potentially interesting folder
|   /template/: Potentially interesting folder
|   /templates/: Potentially interesting folder
|   /temporal/: Potentially interesting folder
|   /test-cgi/: Potentially interesting folder
|   /testing/: Potentially interesting folder
|   /tests/: Potentially interesting folder
|   /testweb/: Potentially interesting folder
|   /themes/: Potentially interesting folder
|   /ticket/: Potentially interesting folder
|   /tickets/: Potentially interesting folder
|   /tip/: Potentially interesting folder
|   /tips/: Potentially interesting folder
|   /tmp/: Potentially interesting folder
|   /ToDo/: Potentially interesting folder
|   /tool/: Potentially interesting folder
|   /tools/: Potentially interesting folder
|   /TopAccess/: Potentially interesting folder
|   /top/: Potentially interesting folder
|   /tpv/: Potentially interesting folder
|   /trabajo/: Potentially interesting folder
|   /track/: Potentially interesting folder
|   /tracking/: Potentially interesting folder
|   /transfer/: Potentially interesting folder
|   /transito/: Potentially interesting folder
|   /transpolar/: Potentially interesting folder
|   /tree/: Potentially interesting folder
|   /trees/: Potentially interesting folder
|   /trick/: Potentially interesting folder
|   /tricks/: Potentially interesting folder
|   /u02/: Potentially interesting folder
|   /unix/: Potentially interesting folder
|   /unknown/: Potentially interesting folder
|   /updates/: Potentially interesting folder
|   /upload/: Potentially interesting folder
|   /uploads/: Potentially interesting folder
|   /usage/: Potentially interesting folder
|   /userdb/: Potentially interesting folder
|   /user/: Potentially interesting folder
|   /users/: Potentially interesting folder
|   /us/: Potentially interesting folder
|   /usr/: Potentially interesting folder
|   /ustats/: Potentially interesting folder
|   /usuario/: Potentially interesting folder
|   /usuarios/: Potentially interesting folder
|   /util/: Potentially interesting folder
|   /utils/: Potentially interesting folder
|   /vendor/: Potentially interesting folder
|   /vfs/: Potentially interesting folder
|   /view/: Potentially interesting folder
|   /vpn/: Potentially interesting folder
|   /vti_txt/: Potentially interesting folder
|   /w2000/: Potentially interesting folder
|   /w2k/: Potentially interesting folder
|   /w3perl/: Potentially interesting folder
|   /w-agora/: Potentially interesting folder
|   /way-board/: Potentially interesting folder
|   /web800fo/: Potentially interesting folder
|   /webaccess/: Potentially interesting folder
|   /webadmin/: Potentially interesting folder
|   /webAdmin/: Potentially interesting folder
|   /webalizer/: Potentially interesting folder
|   /webapps/: Potentially interesting folder
|   /WebBank/: Potentially interesting folder
|   /webboard/: Potentially interesting folder
|   /WebCalendar/: Potentially interesting folder
|   /webcart/: Potentially interesting folder
|   /webcart-lite/: Potentially interesting folder
|   /webcgi/: Potentially interesting folder
|   /webdata/: Potentially interesting folder
|   /webdav/: Potentially interesting folder
|   /webdb/: Potentially interesting folder
|   /webDB/: Potentially interesting folder
|   /web/: Potentially interesting folder
|   /webimages2/: Potentially interesting folder
|   /webimages/: Potentially interesting folder
|   /web-inf/: Potentially interesting folder
|   /webmaster/: Potentially interesting folder
|   /webmaster_logs/: Potentially interesting folder
|   /webMathematica/: Potentially interesting folder
|   /webpub/: Potentially interesting folder
|   /webpub-ui/: Potentially interesting folder
|   /webreports/: Potentially interesting folder
|   /webreps/: Potentially interesting folder
|   /webshare/: Potentially interesting folder
|   /WebShop/: Potentially interesting folder
|   /website/: Potentially interesting folder
|   /webstat/: Potentially interesting folder
|   /webstats/: Potentially interesting folder
|   /Web_store/: Potentially interesting folder
|   /webtrace/: Potentially interesting folder
|   /WebTrend/: Potentially interesting folder
|   /webtrends/: Potentially interesting folder
|   /web_usage/: Potentially interesting folder
|   /win2k/: Potentially interesting folder
|   /window/: Potentially interesting folder
|   /windows/: Potentially interesting folder
|   /win/: Potentially interesting folder
|   /winnt/: Potentially interesting folder
|   /word/: Potentially interesting folder
|   /work/: Potentially interesting folder
|   /world/: Potentially interesting folder
|   /wsdocs/: Potentially interesting folder
|   /WS_FTP/: Potentially interesting folder
|   /wstats/: Potentially interesting folder
|   /wusage/: Potentially interesting folder
|   /www0/: Potentially interesting folder
|   /www2/: Potentially interesting folder
|   /www3/: Potentially interesting folder
|   /www4/: Potentially interesting folder
|   /www/: Potentially interesting folder
|   /wwwjoin/: Potentially interesting folder
|   /wwwrooot/: Potentially interesting folder
|   /www-sql/: Potentially interesting folder
|   /wwwstat/: Potentially interesting folder
|   /wwwstats/: Potentially interesting folder
|   /xGB/: Potentially interesting folder
|   /xml/: Potentially interesting folder
|   /XSL/: Potentially interesting folder
|   /xtemp/: Potentially interesting folder
|   /xymon/: Potentially interesting folder
|   /zb41/: Potentially interesting folder
|   /zipfiles/: Potentially interesting folder
|   /zip/: Potentially interesting folder
|   /_docs/: Potentially interesting folder
|   /sitecore/shell/sitecore.version.xml: Sitecore.NET login page
|   /sitecore/login/default.aspx: Sitecore.NET login page
|   /sitecore/admin/stats.aspx: Sitecore.NET (CMS)
|   /sitecore/admin/unlock_admin.aspx: Sitecore.NET (CMS)
|   /sitecore/shell/Applications/shell.xml: Sitecore.NET (CMS)
|   /sitecore/admin/ShowConfig.aspx: Sitecore.NET (CMS)
|   /App_Config/Security/Domains.config.xml: Sitecore.NET (CMS)
|_  /App_Config/Security/GlobalRoles.config.xml: Sitecore.NET (CMS)
| http-vuln-cve2010-0738:
|_  /jmx-console/: Authentication was not required
|_http-vuln-cve2014-3704: ERROR: Script execution failed (use -d to debug)
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_sslv2-drown:

Nmap done: 1 IP address (1 host up) scanned in 315.09 seconds
True
🎃 krink@Karls-MBP bin % sentinel list-vulns
29 192.168.0.1 2020-10-30 02:31:03 -
28 192.168.0.2 2020-10-25 17:40:29 -
27 192.168.0.220 2020-10-25 17:39:38 80/tcp
26 192.168.0.221 2020-10-25 17:39:31 80/tcp
25 192.168.0.159 2020-10-25 17:39:07 80/tcp,443/tcp,8873/tcp
24 192.168.0.1 2020-10-25 17:38:42 -
23 192.168.0.8 2020-10-25 17:38:12 -
22 192.168.0.4 2020-10-25 17:38:00 -
21 192.168.0.155 2020-10-25 17:37:47 -
20 192.168.0.81 2020-10-25 17:37:37 -
19 192.168.0.253 2020-10-25 17:37:37 -
18 192.168.0.16 2020-10-25 17:37:37 -
17 192.168.0.156 2020-10-25 17:37:37 -
16 192.168.0.1 2020-10-14 01:54:55 -
15 192.168.0.1 2020-10-13 03:10:06 -
14 192.168.0.2 2020-10-13 03:09:57 -
13 192.168.2.1 2020-10-13 03:09:55 -
12 192.168.0.4 2020-10-13 03:09:01 -
11 192.168.0.220 2020-10-13 03:07:50 80/tcp
10 192.168.0.221 2020-10-13 03:07:43 80/tcp
9 192.168.2.22 2020-10-13 03:07:35 -
8 192.168.2.24 2020-10-13 03:07:27 -
7 192.168.2.21 2020-10-13 03:07:26 -
6 192.168.0.159 2020-10-13 03:07:03 443/tcp,8873/tcp
5 192.168.0.8 2020-10-13 03:06:54 8080/tcp
4 192.168.0.16 2020-10-13 03:05:43 -
3 192.168.0.81 2020-10-13 03:05:43 -
2 192.168.0.253 2020-10-13 03:05:42 -
1 192.168.0.156 2020-10-13 03:05:41 -
🎃 krink@Karls-MBP bin % sentinel list-vulns 25
25 192.168.0.159 2020-10-25 17:39:07 80/tcp,443/tcp,8873/tcp
Starting Nmap 7.80 ( https://nmap.org ) at 2020-10-25 10:37 PDT
Pre-scan script results:
| broadcast-avahi-dos:
|   Discovered hosts:
|     224.0.0.251
|   After NULL UDP avahi packet DoS (CVE-2011-1002).
|_  Hosts are all up (not vulnerable).
Nmap scan report for LS220DD98.local.lan (192.168.0.159)
Host is up (0.0038s latency).
Not shown: 995 closed ports
PORT     STATE SERVICE
80/tcp   open  http
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum:
|_  /proxy/: Potentially interesting folder
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-passwd: ERROR: Script execution failed (use -d to debug)
| http-slowloris-check:
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-vuln-cve2010-0738:
|_  /jmx-console/: Authentication was not required
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
443/tcp  open  https
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum:
|_  /proxy/: Potentially interesting folder
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-passwd: ERROR: Script execution failed (use -d to debug)
| http-slowloris-check:
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-vuln-cve2010-0738:
|_  /jmx-console/: Authentication was not required
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_ssl-ccs-injection: No reply from server (TIMEOUT)
| ssl-dh-params:
|   VULNERABLE:
|   Diffie-Hellman Key Exchange Insufficient Group Strength
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use Diffie-Hellman groups
|       of insufficient strength, especially those using one of a few commonly
|       shared groups, may be susceptible to passive eavesdropping attacks.
|     Check results:
|       WEAK DH GROUP 1
|             Cipher Suite: TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA
|             Modulus Type: Non-safe prime
|             Modulus Source: RFC5114/1024-bit DSA group with 160-bit prime order subgroup
|             Modulus Length: 1024
|             Generator Length: 1024
|             Public Key Length: 1024
|     References:
|_      https://weakdh.org
|_sslv2-drown:
548/tcp  open  afp
873/tcp  open  rsync
8873/tcp open  dxspider
| ssl-dh-params:
|   VULNERABLE:
|   Anonymous Diffie-Hellman Key Exchange MitM Vulnerability
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use anonymous
|       Diffie-Hellman key exchange only provide protection against passive
|       eavesdropping, and are vulnerable to active man-in-the-middle attacks
|       which could completely compromise the confidentiality and integrity
|       of any data exchanged over the resulting session.
|     Check results:
|       ANONYMOUS DH GROUP 1
|             Cipher Suite: TLS_DH_anon_WITH_AES_256_CBC_SHA
|             Modulus Type: Safe prime
|             Modulus Source: Unknown/Custom-generated
|             Modulus Length: 512
|             Generator Length: 8
|             Public Key Length: 512
|     References:
|_      https://www.ietf.org/rfc/rfc2246.txt
|_sslv2-drown:
MAC Address: DC:FB:02:EB:7D:98 (Buffalo.inc)

Nmap done: 1 IP address (1 host up) scanned in 125.06 seconds

🎃 krink@Karls-MBP bin %




