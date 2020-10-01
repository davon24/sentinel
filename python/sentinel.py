#!/usr/bin/env python3

__version__ = '0.0.0.v1.4.w9'

import sys
#sys.path.insert(0,'db')

import json

import tools
import store

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

        detect-scan-net [ip/net]
        detect-scan ip
        list-detects [id]
        del-detect id
        clear-detects

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
        established-rules
        established-rules-filter
        established-rule ALLOW|DENY proto laddr lport faddr fport
        established-alerts

        list-ips
        update-ip ip data
        del-ip ip
        clear-ips

        list-jobs
        list-jobs-running
        run-job name
        update-job name data
        delete-job name
        clear-jobs

        list-configs
        update-config name data
        delete-config id

        list-reports
        delete-report id

        list-alerts
        delete-alert id
        run-alert name
        update-alert name data
        run-alert name

        list-fims
        list-fims-changed
        check-fim [name]
        b2sum-fim [name]
        b2sum /dir/file
        update-fim name data
        delete-fim id
        add-fim name /dir/file
        del-fim name /dir/file

        sentry

        ---

        run-create-db

    ''')


def printArps():
    arpTbl = tools.getArps()
    for k,v in arpTbl.items():
        if (v == '(incomplete)') or (v == '<incomplete>'):
            continue
        print(v,k)
    return True

def printListening():
    cntDct = cntLsOf()
    for k,v in sorted(cntDct.items()):
        print(k,v)
    return True

def run():
        arpTbl = tools.getArps()
        update = store.update_arp_data(db_store, arpTbl)
        print(update)
        return True

if __name__ == '__main__':

    gLst = []

    db_store = 'db/sentinel.db'
    db_manuf = 'db/manuf'

    if sys.argv[1:]:
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
            #p = tools.printListenPortsDetails(port)
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
        if sys.argv[1] == 'established-rules':
            established_rules = store.printEstablishedRules(db_store)
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
            print_alerts = store.printEstablishedRulesMatch(db_store)
            sys.exit(0)
        if sys.argv[1] == 'established-alerts':
            print_alerts = store.printEstablishedAlerts(db_store)
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
            run = store.printIPs(db_store)
            sys.exit(0)
        if sys.argv[1] == 'add-ip':
            ip = sys.argv[2]
            insert = store.insertIPs(ip, db_store)
            print(insert)
            sys.exit(0)
        if sys.argv[1] == 'del-ip':
            ip = sys.argv[2]
            insert = store.deleteIPs(ip, db_store)
            print(insert)
            sys.exit(0
            )
        if sys.argv[1] == 'update-ip':
            ip = sys.argv[2]
            data = sys.argv[3]
            #update = store.updateIPs(ip, data, db_store)
            replace = store.replaceINTO('ips', ip, data, db_store)
            print(replace)
            sys.exit(0)

        if sys.argv[1] == 'clear-ips':
            clear = store.clearAllIPs(db_store)
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
                
                #print('i ' + str(i) + ' ' + str(len(i)))

                if len(i) == 1:
                    #level = ''.join(i)
                    level = sys.argv[2]
                    ipnet = tools.getIfconfigIPv4()
                #if len(_i)  

            if level is None:
                level = 1

            #print(ipnet, level, db_store)
            #run_discovery = tools.runDiscoverNet(ipnet, level, db_store)
            #run_discovery = tools.runDiscoverNetMultiProcess(ipnet, level, db_store)
            run_discovery = tools.runDiscoverNetAll(ipnet, level, db_store)
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
            #scans = store.getNmapVulns(db_store)
            #for row in scans:
            #    print(row)
            try: vid = sys.argv[2]
            except IndexError: vid = None
            #print('vid: ' + str(vid))
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

            #print(ip, port)
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
                #print('i ' + str(i) + ' ' + str(len(i)))

                if len(i) == 1:
                    #level = ''.join(i)
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

            #print(str(ipnet))
            #print(str(level))
            scan = tools.runNmapScanMultiProcess(ipnet, level, db_store)
            print(scan)
            sys.exit(0)

        #if sys.argv[1] == 'vuln-scan':
        #    ip = sys.argv[2]
        #    scan = tools.nmapVulnScanStore(ip, db_store)
        #    print(scan)
        #    sys.exit(0)

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

            #print(str(ipnet))
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

        if sys.argv[1] == 'list-jobs':
            #run = tools.printJobs(db_store)
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
            #run = store.deleteFrom('jobs', rowid, db_store)
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
            run = tools.sentryMode(db_store)
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
                fims = store.getAll('fims', db_store)
                for i in fims:
                    name = i[1]
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
                fims = store.getAll('fims', db_store)
                for i in fims:
                    name = i[1]
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
            reports = store.getAll('reports', db_store)
            for row in reports:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'delete-report':
            rowid = sys.argv[2]
            delete = store.deleteFrom('reports', rowid, db_store)
            print(delete)
            sys.exit(0)

        if sys.argv[1] == 'list-alerts':
            alerts = store.getAll('alerts', db_store)
            for row in alerts:
                print(row)
            sys.exit(0)

        if sys.argv[1] == 'delete-alert':
            rowid = sys.argv[2]
            delete = store.deleteFrom('alerts', rowid, db_store)
            print(delete)
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

        else:
            usage()
            sys.exit(0)
    else:
        sys.exit(run())

            
