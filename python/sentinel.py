#!/usr/bin/env python3

import sys
import os
import json

import tools
import store

__version__ = tools.__version__

def usage():
    print(sys.argv[0] + ''' [option]

    options:

        nmap-net net
        ping-net ip/net

        port-scan [ip/net] [level]
        list-nmaps
        nmap ip [level]
        del-nmap ip
        clear-nmaps

        vuln-scan [ip/net]
        list-vulns [id]
        del-vuln id
        clear-vulns
        check-vuln id
        email-vuln id

        arps
        manuf mac
        lsof port
        rdns ip [srv]
        myip

        udp ip port
        udpscan ip port
        tcp ip port

        list-macs
        update-manuf mac
        update-dns mac ip

        listening
        listening-detailed
        listening-details port
        listening-allowed
        listening-alerts
        listening-allow port
        listening-remove port

        established
        established-lsof
        established-rules
        established-rules-filter
        established-rule ALLOW|DENY proto laddr lport faddr fport
        established-alerts
        delete-established-rule rowid
        clear-established-rules

        list-ips
        update-ip ip data
        update-ip-item ip item value
        delete-ip-item ip item value
        del-ip ip
        clear-ips

        list-jobs
        list-jobs-running
        list-jobs-available
        run-job name
        update-job name data
        delete-job name
        clear-jobs

        list-configs
        update-config name data
        delete-config name
        clear-configs

        list-rules
        update-rule name data
        delete-rule name
        clear-rules

        list-reports
        update-report name data
        delete-report name
        clear-reports

        list-alerts
        delete-alert id
        run-alert name
        update-alert name data
        run-alert name
        clear-alerts

        list-fims
        list-fims-changed
        check-fim [name]
        b2sum-fim [name]
        b2sum /dir/file
        update-fim name data
        delete-fim id
        add-fim name /dir/file
        del-fim name /dir/file

        list-files
        add-file /dir/file
        del-file /dir/file
        fim-restore /dir/file [/dir/file]
        fim-diff
        clear-files

        file-type /dir/file

        av-scan dir|file
        list-avs

        list-proms

        list-proms-db
        update-prom-db name data
        clear-proms-db

        list-b2sums
        clear-b2sums

        list-sshwatch
        clear-sshwatch

        list-counts
        clear-counts

        list-training [id|tags tag]
        update-training tag json
        update-training-tag id tag
        delete-training id
        clear-training

        list-occurrence [name|-eq,-gt,-lt,-ne,-le,-ge num]
        delete-occurrence name
        copy-occurrence name
        clear-occurrence

        sample-logstream count
        mark-training tag
        mark-training-on name

        list-system-profile
        list-system-profile-full
        gen-system-profile
        get-system-profile-name name
        get-system-profile-rowid rowid
        del-system-profile-name name
        del-system-profile-rowid rowid
        clear-system-profile
        diff-system-profile-rowid rowid rowid

        tail file
        logstream
        logstream-json
        logstream-keys
        run-create-db
        run-ps

        sentry

        ---

        config

                watch-syslog:
                    rules
                    sklearn naive_bayes.MultinomialNB
                            naive_bayes.BernoulliNB

                watch-resin-log
                watch-mariadb-audit-log
                watch-ssh

Version: {} '''.format(__version__))





def printArps():
    arpTbl = tools.getArps()
    for k,v in arpTbl.items():
        if (v == '(incomplete)') or (v == '<incomplete>'):
            continue
        print(v,k)
    return True

def printListening():
    cntDct = tools.cntLsOf()
    for k,v in sorted(cntDct.items()):
        print(k,v)
    return True

def run():
        arpTbl = tools.getArps()
        update = store.update_arp_data(db_store, arpTbl, db_manuf)
        print(update)
        return True

if __name__ == '__main__':

    #sys.path.insert(0,'db')
    #print(os.path.dirname(__file__))
    #sys.path.insert(0, os.path.dirname(__file__))

    db_store = str(os.path.dirname(__file__)) + '/db/sentinel.db'
    db_manuf = str(os.path.dirname(__file__)) + '/db/manuf'

    if sys.argv[1:]:

        if sys.argv[1] == '--version':
            print(__version__)
            sys.exit(0)

        if sys.argv[1] == 'manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            print(mfname)
            sys.exit(0)

        if sys.argv[1] == 'arps':
            printArps()
            sys.exit(0)

        if sys.argv[1] == 'list-macs':
            store.print_all(db_store)
            sys.exit(0)

        if sys.argv[1] == 'update-manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            update = store.update_data_manuf(mac, mfname, db_store)
            print(update)
            sys.exit(0)

        if sys.argv[1] == 'rdns':
            ip = sys.argv[2]
            try: srv = sys.argv[3]
            except IndexError: srv = None
            dnsname = tools.getNSlookup(ip, srv)
            print(dnsname)
            sys.exit(0)

        if sys.argv[1] == 'update-dns':
            mac = sys.argv[2]
            ip = sys.argv[3]
            #dnsname = tools.getDNSName(ip)
            #update = store.update_data_dns(mac, dnsname, db_store)
            import threading
            dns = store.DNSUpDateTask()
            t = threading.Thread(target=dns.run, args=(mac,ip,db_store,))
            t.start()
            #print(t)
            sys.exit(0)

        if sys.argv[1] == 'ping-net':
            ip = sys.argv[2]
            pn = tools.pingNet(ip)
            print(pn)
            sys.exit(0)

        if sys.argv[1] == 'nmap-net':
            ip = sys.argv[2]
            pn = tools.nmapNet(ip)
            print(pn)
            sys.exit(0)

        if sys.argv[1] == 'listening':
            p = tools.printListenPorts()
            sys.exit(0)

        if sys.argv[1] == 'listening-detailed':
            p = tools.printListenPortsDetailed()
            sys.exit(0)

        if sys.argv[1] == 'listening-details':
            port = sys.argv[2]
            p = tools.printLsOfPort(port)
            sys.exit(0)

        if sys.argv[1] == 'listening-allowed':
            p = store.printListeningAllowed(db_store)
            sys.exit(0)

        if sys.argv[1] == 'listening-allow':
            port = sys.argv[2]
            insert = store.insertAllowedPort(port, db_store)
            print(insert)
            sys.exit(0)

        if sys.argv[1] == 'listening-remove':
            port = sys.argv[2]
            remove = store.deleteAllowedPort(port, db_store)
            print(remove)
            sys.exit(0)

        if sys.argv[1] == 'listening-alerts':
            alerts = store.printListeningAlerts(db_store)
            sys.exit(0)

        if sys.argv[1] == 'established':
            established = tools.printEstablished()
            sys.exit(0)

        if sys.argv[1] == 'established-lsof':
            established = tools.printEstablishedLsOf()
            sys.exit(0)

        if sys.argv[1] == 'established-rules':
            established_rules = tools.printEstablishedRules(db_store)
            sys.exit(0)

        if sys.argv[1] == 'established-rule':
            #established-rule proto laddr lport faddr fport
            rule  = sys.argv[2]
            proto = sys.argv[3]
            laddr = sys.argv[4]
            lport = sys.argv[5]
            faddr = sys.argv[6]
            fport = sys.argv[7]
            insert_rule = store.insertEstablishedRules(rule, proto, laddr, lport, faddr, fport, db_store)
            sys.exit(0)

        if sys.argv[1] == 'established-rules-filter':
            print_alerts = tools.printEstablishedRulesMatch(db_store)
            sys.exit(0)

        if sys.argv[1] == 'established-alerts':
            print_alerts = tools.printEstablishedAlerts(db_store)
            sys.exit(0)

        if sys.argv[1] == 'delete-established-rule':
            rowid = sys.argv[2]
            delete = store.deleteFromRowid('established', rowid, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'clear-established-rules':
            clear = store.clearAll('established', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'clear-configs':
            clear = store.clearAll('configs', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'lsof':
            port = sys.argv[2]
            lsof = tools.printLsOfPort(port)
            sys.exit(0)

        if sys.argv[1] == 'nmap':
            ip = sys.argv[2]
            try: level = sys.argv[3]
            except IndexError: level = 1
            scan = tools.nmapScan(ip, level)
            update = store.replaceNmaps(ip, scan, db_store)
            print(str(update) + ' ' + str(scan))
            sys.exit(0)

        if sys.argv[1] == 'list-ips':
            rows = store.selectAll('ips', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'add-ip':
            ip = sys.argv[2]
            insert = store.insertIPs(ip, db_store)
            print(insert)
            sys.exit(0)

        if sys.argv[1] == 'del-ip':
            ip = sys.argv[2]
            _del = store.deleteIPs(ip, db_store)
            print(_del)
            sys.exit(0)

        if sys.argv[1] == 'update-ip':
            ip = sys.argv[2]
            data = sys.argv[3]

            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            replace = store.replaceINTO('ips', ip, data, db_store)
            print(replace)
            sys.exit(0)

        if sys.argv[1] == 'update-ip-item':
            name = sys.argv[2]
            item = sys.argv[3]
            val  = sys.argv[4]
            update = store.updateDataItem(item, val, 'ips', name, db_store)
            print(update)
            sys.exit(0)

        if sys.argv[1] == 'delete-ip-item':
            name = sys.argv[2]
            item = sys.argv[3]
            delete = store.deleteDataItem(item, 'ips', name, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'clear-ips':
            clear = store.clearAll('ips', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'discover-net':
            ipnet = None
            level = None
            try:
                ipnet = sys.argv[2]
                level = sys.argv[3]
            except IndexError: pass

            if ipnet is None:
                ipnet = tools.getIfconfigIPv4()
            else:
                i = ipnet.split('.')
                if len(i) == 1:
                    level = sys.argv[2]
                    ipnet = tools.getIfconfigIPv4()
            if level is None:
                level = 1

            run_discovery = tools.runDiscoverNet(ipnet, level, db_store)
            print(run_discovery)
            sys.exit(0)

        if sys.argv[1] == 'list-nmaps':
            scans = store.getNmaps(db_store)
            for row in scans:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'del-nmap':
            ip = sys.argv[2]
            del_ = store.deleteNmaps(ip, db_store)
            print(del_)
            sys.exit(0)

        if sys.argv[1] == 'clear-nmaps':
            clear = store.clearAllNmaps(db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'list-vulns':
            try: vid = sys.argv[2]
            except IndexError: vid = None
            run = tools.printVulnScan(db_store, vid)
            sys.exit(0)

        if sys.argv[1] == 'del-vuln':
            ip = sys.argv[2]
            del_ = store.deleteVulns(ip, db_store)
            print(del_)
            sys.exit(0)

        if sys.argv[1] == 'clear-vulns':
            clear = store.clearAllVulns(db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'check-vuln':
            vid = sys.argv[2]
            data = store.getVulnData(vid, db_store)
            run = tools.processVulnData(data)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'email-vuln':
            vid = sys.argv[2]
            data = store.getVulnData(vid, db_store)
            subject = 'sentinel vuln-scan'
            email = tools.sendEmail(subject, data, db_store)
            print(email)
            sys.exit(0)

        if sys.argv[1] == 'myip':
            myip = tools.getIfconfigIPv4()
            print(myip)
            sys.exit(0)

        if sys.argv[1] == 'udp':
            ip = sys.argv[2]
            port = sys.argv[3]
            run = tools.nmapUDP(ip, port)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'udpscan':
            ip = port = None
            try:
                ip = sys.argv[2]
                port = sys.argv[3]
            except IndexError: pass
            run = tools.nmapUDPscan(ip, port)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'tcp':
            ip = sys.argv[2]
            port = sys.argv[3]
            run = tools.nmapTCP(ip, port)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-detects':
            try: id_ = sys.argv[2]
            except IndexError: id_ = None
            run = tools.printDetectScan(db_store, id_)
            sys.exit(0)

        if sys.argv[1] == 'detect-scan':
            ip = sys.argv[2]
            scan = tools.nmapDetectScanStore(ip, db_store)
            print(str(scan))
            sys.exit(0)

        if sys.argv[1] == 'del-detect':
            id_ = sys.argv[2]
            del_ = store.deleteDetect(id_, db_store)
            print(del_)
            sys.exit(0)

        if sys.argv[1] == 'clear-detects':
            clear = store.clearAllDetects(db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'port-scan':
            ipnet = None
            level = 1
            try:
                ipnet = sys.argv[2]
                level = sys.argv[3]
            except IndexError: pass

            if ipnet is None:
                myip = tools.getIfconfigIPv4()
                ipn = tools.getIpNet(myip)
                print('discover net: ' + str(ipn))
                ipnet = tools.nmapNet(ipn)
            else:
                i = ipnet.split('.')

                if len(i) == 1:
                    level = sys.argv[2]
                    myip = tools.getIfconfigIPv4()
                    ipn = tools.getIpNet(myip)
                    print('discover net: ' + str(ipn))
                    ipnet = tools.nmapNet(ipn)
                else:
                    if tools.isNet(ipnet):
                        print('discover net: ' + str(ipnet))
                        ipnet = tools.nmapNet(ipnet)
            
            if type(ipnet) == str:
                ipnet = ipnet.split()
            scan = tools.runNmapScanMultiProcess(ipnet, level, db_store)
            print(scan)
            sys.exit(0)

        if sys.argv[1] == 'vuln-scan':
            try: ipnet = sys.argv[2]
            except IndexError: ipnet = None

            if ipnet is None:
                myip = tools.getIfconfigIPv4()
                ipn = tools.getIpNet(myip)
                print('discover net: ' + str(ipn))
                ipnet = tools.nmapNet(ipn)
            else:
                if tools.isNet(ipnet):
                    print('discover net: ' + str(ipnet))
                    ipnet = tools.nmapNet(ipnet)

            if type(ipnet) == str:
                ipnet = ipnet.split()

            scan = tools.runNmapVulnMultiProcess(ipnet, db_store)
            print(scan)
            sys.exit(0)

        if sys.argv[1] == 'detect-scan-net':
            ipnet = None
            try: ipnet = sys.argv[2]
            except IndexError: pass
            if ipnet is None:
                ipnet = tools.getIfconfigIPv4()
            ipn = tools.getIpNet(ipnet)
            print('ipnet: ' + ipn)
            hostLst = tools.nmapNet(ipn)
            scan = tools.runNmapDetectMultiProcess(hostLst, db_store)
            print(scan)
            sys.exit(0)

        if sys.argv[1] == 'list-configs':
            run = tools.printConfigs(db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'update-config':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError: 
                print('invalid json') 
                sys.exit(1)
            run = store.replaceINTO('configs', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'delete-config':
            rowid = sys.argv[2]
            run = store.deleteFrom('configs', rowid, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-rules':
            rows = store.selectAll('rules', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'update-rule':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            run = store.replaceINTO('rules', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'delete-rule':
            name = sys.argv[2]
            run = store.deleteFrom('rules', name, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'clear-rules':
            clear = store.clearAll('rules', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'list-jobs':
            rows = store.selectAll('jobs', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'update-job':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError: 
                print('invalid json') 
                sys.exit(1)
            run = store.replaceINTO('jobs', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'delete-job':
            name = sys.argv[2]
            run = store.deleteJob(name, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'clear-jobs':
            clear = store.clearAllJobs(db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'run-job':
            name = sys.argv[2]
            run = tools.runJob(name, db_store)
            print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'sentry':
            try: v = sys.argv[2]
            except IndexError: v = False
            run = tools.sentryMode(db_store, verbose=v)
            print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'list-jobs-running':
            run = tools.listRunning(db_store)
            sys.exit(0)

        if sys.argv[1] == 'b2sum':
            _file = sys.argv[2]
            b2sum = tools.b2sum(_file)
            print(_file + ' ' + b2sum)
            sys.exit(0)

        if sys.argv[1] == 'b2sum-fim':
            try: name = sys.argv[2]
            except IndexError: name = None
            if name is None:
                fims = store.selectAll('fims', db_store)
                for i in fims:
                    name = i[0]
                    run = tools.b2sumFim(name, db_store)
                    print(str(name) + ' ' + str(run))
            else:
                run = tools.b2sumFim(name, db_store)
                print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'check-fim':
            try: name = sys.argv[2]
            except IndexError: name = None
            if name is None:
                fims = store.selectAll('fims', db_store)
                for i in fims:
                    name = i[0]
                    run = tools.printFim(name, db_store)
                    print(str(name) + ' ' + str(run))
            else:
                run = tools.printFim(name, db_store)
                print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'list-fims':
            run = tools.printAllFims(db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-fims-changed':
            run = tools.printAllFimsChanged(db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'add-fim':
            name = sys.argv[2]
            _file = sys.argv[3]
            add = tools.addFimFile(name, _file, db_store)
            print(str(add))
            sys.exit(0)

        if sys.argv[1] == 'del-fim':
            name = sys.argv[2]
            _file = sys.argv[3]
            add = tools.delFimFile(name, _file, db_store)
            print(str(add))
            sys.exit(0)

        if sys.argv[1] == 'update-fim':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            run = store.replaceINTO('fims', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-reports':
            reports = store.selectAll('reports', db_store)
            for row in reports:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'delete-report':
            name = sys.argv[2]
            delete = store.deleteFrom('reports', name, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'clear-reports':
            clear = store.clearAll('reports', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'update-report':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            run = store.replaceINTO('reports', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-alerts':
            alerts = store.selectAll('alerts', db_store)
            for row in alerts:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'delete-alert':
            name = sys.argv[2]
            delete = store.deleteFrom('alerts', name, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'clear-alerts':
            clear = store.clearAll('alerts', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'update-alert':
            name = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            run = store.replaceINTO('alerts', name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'run-alert':
            name = sys.argv[2]
            run = tools.runAlert(name, db_store)
            print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'run-create-db':
            run = store.createDB(db_store)
            print(str(run))
            sys.exit(0)

        if sys.argv[1] == 'run-ps':
            import modules.ps.ps
            run = modules.ps.ps.get_ps()
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'list-jobs-available':
            for k,v in tools.options.items():
                print(k)
            sys.exit(0)

        if sys.argv[1] == 'list-counts':
            reports = store.selectAll('counts', db_store)
            for row in reports:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'clear-counts':
            clear = store.clearAll('counts', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'list-proms':
            _prom = str(db_store) + '.prom'
            with open(_prom, 'r') as _file:
                lines = _file.readlines()
                for line in lines:
                    print(line.strip('\n'))
            sys.exit(0)

        if sys.argv[1] == 'list-proms-db':
            proms = store.selectAll('proms', db_store)
            for row in proms:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'clear-proms-db':
            clear = store.clearAll('proms', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'update-prom-db':
            name = sys.argv[2]
            data = sys.argv[3]
            run = store.replaceINTOproms(name, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'file-type':
            import modules.gitegridy.gitegridy as git
            _file = sys.argv[2]
            file_type = git.fileType(_file)
            print(file_type)
            sys.exit(0)

        if sys.argv[1] == 'add-file':
            _file = sys.argv[2]
            store_file = store.storeFile(_file, db_store)
            print(store_file)
            sys.exit(0)

        if sys.argv[1] == 'del-file':
            _file = sys.argv[2]
            unstore_file = store.unstoreFile(_file, db_store)
            print(unstore_file)
            sys.exit(0)

        if sys.argv[1] == 'list-files':
            list_files = store.selectAll('files', db_store)
            for row in list_files:
                print(row[0], row[1])
            sys.exit(0)

        if sys.argv[1] == 'clear-files':
            clear = store.clearAll('files', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'fim-diff':
            _file = sys.argv[2]
            fim_diff = tools.fimDiff(_file, db_store)
            print(fim_diff)
            sys.exit(0)

        if sys.argv[1] == 'fim-restore':
            _file = sys.argv[2]
            try: _dest = sys.argv[3]
            except IndexError: _dest = None

            store_file_ = store.getData('files', _file, db_store)
            store_file_blob = store_file_[0]
            
            if _dest:
                dest = _dest
            else:
                dest = _file

            with open(dest, 'wb+') as outfile:
                outfile.write(store_file_blob)

            print('fim-restore ' + dest)
            sys.exit(0)

        if sys.argv[1] == 'av-scan':
            filedir = sys.argv[2]
            av_scan = tools.avScan(filedir, db_store)
            print(av_scan)
            sys.exit(0)

        if sys.argv[1] == 'tail':
            _file = sys.argv[2]
            for line in tools.tail(_file):
                print(line)
            sys.exit(0)

        if sys.argv[1] == 'logstream':
            for line in tools.logstream():
                print(line)
            sys.exit(0)

        if sys.argv[1] == 'logstream-json':
            for line in tools.logstream():
                print(line.decode('utf-8'))
            sys.exit(0)

        if sys.argv[1] == 'logstream-keys':
            for line in tools.logstream():
                jline = json.loads(line.decode('utf-8'))
                n = len(jline.keys())
                print(n, ' ' , jline.keys())
            sys.exit(0)

        if sys.argv[1] == 'list-b2sums':
            rows = store.selectAll('b2sum', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'clear-b2sums':
            clear = store.clearAll('b2sum', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'list-sshwatch':
            rows = store.selectAll('sshwatch', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'clear-sshwatch':
            clear = store.clearAll('sshwatch', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'clear-training':
            clear = store.clearAll('training', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'list-training':
            try: _id = sys.argv[2]
            except IndexError: _id = None

            if _id:

                if _id  == 'tags':
                    _tag = sys.argv[3]
                    rows = store.getAllTrainingTags(_tag, db_store)
                    for row in rows:
                        print(row)
                else:
                    row = store.getByID('training', _id, db_store)
                    print(row)

            else:
                rows = store.getAll('training', db_store)
                for row in rows:
                    print(row)
            sys.exit(0)

        if sys.argv[1] == 'update-training':
            tag = sys.argv[2]
            data = sys.argv[3]
            try: valid_json = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('invalid json')
                sys.exit(1)
            run = store.updateTraining(tag, data, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'update-training-tag':
            _id = sys.argv[2]
            tag = sys.argv[3]
            run = store.updateTrainingTag(_id, tag, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'delete-training':
            rowid = sys.argv[2]
            delete = store.deleteFromRowid('training', rowid, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'sample-logstream':
            count = sys.argv[2]
            run = tools.sampleLogStream(count, db_store)
            sys.exit(0)

        if sys.argv[1] == 'mark-training':
            tag = sys.argv[2]
            run = store.markAllTraining(tag, db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'mark-training-on':
            name = sys.argv[2]
            run = tools.markTrainingRe(name, db_store)
            sys.exit(0)

        #list-occurrence [name|-gt,-lt,-eq num]
        if sys.argv[1] == 'list-occurrence':

            try: opn = sys.argv[2]
            except IndexError: opn=None
            try: val = sys.argv[3]
            except IndexError: val=None

            if val:
                rows = store.getByOp('occurrence', opn, val, db_store)
                for row in rows:
                    print(row)
            elif opn:
                row = store.getByName('occurrence', opn, db_store)
                print(row)
            else:
                rows = store.selectAll('occurrence', db_store)
                for row in rows:
                    print(row)
            sys.exit(0)

        if sys.argv[1] == 'clear-occurrence':
            clear = store.clearAll('occurrence', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'delete-occurrence':
            name = sys.argv[2]
            delete = store.deleteFrom('occurrence', name, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'copy-occurrence':
            name = sys.argv[2]
            _copy = store.copyOccurrenceToTraining(name, db_store)
            print(_copy)
            sys.exit(0)

        if sys.argv[1] == 'list-system-profile-full':
            rows = store.getAll('system_profile', db_store)
            for row in rows:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'list-system-profile':
            #name = sys.argv[2]
            #rows = store.selectAll('system_profile', db_store)
            rows = store.getAll('system_profile', db_store)
            for row in rows:
                print(row[0],row[1],row[2])
            sys.exit(0)

        if sys.argv[1] == 'gen-system-profile':
            run = tools.genSystemProfile(db_store)
            print(run)
            sys.exit(0)

        if sys.argv[1] == 'del-system-profile-name':
            name = sys.argv[2]
            delete = store.deleteFrom('system_profile', name, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'del-system-profile-rowid':
            rowid = sys.argv[2]
            delete = store.deleteFromRowid('system_profile', rowid, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'clear-system-profile':
            clear = store.clearAll('system_profile', db_store)
            print(clear)
            sys.exit(0)

        if sys.argv[1] == 'get-system-profile-name':
            name = sys.argv[2]
            get = store.getByName('system_profile', name, db_store)
            print(get)
            sys.exit(0)

        if sys.argv[1] == 'get-system-profile-rowid':
            rowid = sys.argv[2]
            get = store.getByID('system_profile', rowid, db_store)
            print(get)
            sys.exit(0)

        if sys.argv[1] == 'diff-system-profile-rowid':
            rowid1 = sys.argv[2]
            rowid2 = sys.argv[3]
            diff = tools.diffSystemProfileIDs(rowid1, rowid2, db_store)
            print(diff)
            sys.exit(0)


        else:
            usage()
            sys.exit(0)
    else:
        sys.exit(run())



