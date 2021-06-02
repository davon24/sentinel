#!/usr/bin/env python3

__version__ = '20210405'

import libvirt
import sys
import json

class ListDomainsClass(object):
    def __init__(self, uri, host):
        self.uri = uri
        self.host = host

    def get(self):
        returnDict = {}
        uri_handle = str(self.uri) + str(self.host) + '/system'
        try:
            self.conn = libvirt.openReadOnly(uri_handle)
        except libvirt.libvirtError as e:
            return {"Error":str(e)}

        domains = self.conn.listAllDomains(0)
        if len(domains) != 0:
            for domain in domains:
                state = self.domstate(domain.name())
                returnDict[domain.name()] = str(state).lower()

        return returnDict

    def domstate(self,domName=None):
        dom = self.conn.lookupByName(domName)
        if dom == None:
            return str('NOTFOUND').lower()

        state, reason = dom.state()
        if state == libvirt.VIR_DOMAIN_NOSTATE:
            state='NOSTATE'
        elif state == libvirt.VIR_DOMAIN_RUNNING:
            state='RUNNING'
        elif state == libvirt.VIR_DOMAIN_BLOCKED:
            state='BLOCKED'
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            state='PAUSED'
        elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
            state='SHUTDOWN'
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            state='SHUTOFF'
        elif state == libvirt.VIR_DOMAIN_CRASHED:
            state='CRASHED'
        elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            state='PMSUSPENDED'
        else:
            state='UNKNOWN'

        return str(state).lower()

class ListDomainsDetailedClass(ListDomainsClass):
    def get(self):
        runningDict = {}
        uri_handle = str(self.uri) + str(self.host) + '/system'
        try:
            self.conn = libvirt.openReadOnly(uri_handle)
        except libvirt.libvirtError as e:
            return {"Error":str(e)}

        hvm_type = str(self.conn.getType())
        hypervisor_type = hvm_type.lower()

        nodeinfo = self.conn.getInfo()
        hvm_model = str(nodeinfo[0])
        hvm_mem = str(nodeinfo[1])
        hvm_cpu = str(nodeinfo[2])
        stats = self.conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)

        hypervisor_cpu = {
          'count': str(hvm_cpu),
          'type': str(hvm_model),
          'kernel': str(stats['kernel']),
          'idle': str(stats['idle']),
          'user': str(stats['user']),
          'iowait': str(stats['iowait'])
        }

        memfree = self.conn.getFreeMemory()
        memfreeMB = memfree / 1024 / 1024
        memusedMB = int(hvm_mem) - int(memfreeMB)

        hypervisor_mem = {
          'total': str(hvm_mem),
          'used': str(memusedMB),
          'free': str(memfreeMB)
        }

        hypervisor = {
          'type': hypervisor_type,
          'cpu': hypervisor_cpu,
          'mem': hypervisor_mem
        }

        runningDict['hypervisor'] = hypervisor

        def domStatus(domName=None):
            runningStatus = {}

            dom = self.conn.lookupByName(domName)
            if dom == None:
                print(json.dumps({"Error":"Failed to find domain " + str(domName)}, indent=2))
                sys.exit(1)

            state = self.domstate(domName)

            state_lower_case = str(state).lower()
            runningStatus['state'] = state_lower_case

            active = dom.isActive()
            if active == True:
                ok=1
            else:
                return {'state': state}

            cpus = dom.maxVcpus() #dom cpu count
            if cpus != -1:
                pass
            else:
                print(json.dumps({"Error":"major error getting dom.Vcpus()"}, indent=2))
                sys.exit(1)

            cpu_stats = dom.getCPUStats(True)
            cpu_time = str(cpu_stats[0]['cpu_time'])
            system_time = str(cpu_stats[0]['system_time'])
            user_time = str(cpu_stats[0]['user_time'])

            dom_cpu = {
              'count': str(cpus),
              'cpu_time': cpu_time,
              'system_time': system_time,
              'user_time': user_time
            }

            runningStatus['cpu'] = dom_cpu

            mem = dom.maxMemory()
            if mem > 0:
                pass
            else:
                print(json.dumps({"Error":"major error getting dom.maxMemory()"}, indent=2))
                sys.exit(1)

            dom_mem = {}
            mem_stats  = dom.memoryStats()

            for name in mem_stats:
                if name:
                    dom_mem[name] = str(mem_stats[name])

            runningStatus['mem'] = dom_mem

            from xml.dom import minidom
            raw_xml = dom.XMLDesc(0)
            xml = minidom.parseString(raw_xml)

            diskTypes = xml.getElementsByTagName('disk')
            diskDict = {}
            source = None
            for diskType in diskTypes:
                diskNodes = diskType.childNodes
                for diskNode in diskNodes:
                    if diskNode.nodeName[0:1] != '#':
                        if diskNode.nodeName == 'source':
                            for attr in diskNode.attributes.keys():
                                if diskNode.attributes[attr].name == 'dev':
                                    source = str(diskNode.attributes[attr].value)
                                elif diskNode.attributes[attr].name == 'file':
                                    source = str(diskNode.attributes[attr].value)
                        if diskNode.nodeName == 'target':
                            for attr in diskNode.attributes.keys():
                                if diskNode.attributes[attr].name == 'dev':
                                    target = str(diskNode.attributes[attr].value)
                                    if source is not None:
                                        rd_req, rd_bytes, wr_req, wr_bytes, err = dom.blockStats(source)
                                    else:
                                        rd_req, rd_bytes, wr_req, wr_bytes, err = None

                                    diskDict[target] = {
                                      'device': str(source),
                                      'read_requests_issued': str(rd_req),
                                      'bytes_read': str(rd_bytes),
                                      'write_requests_issued': str(wr_req),
                                      'bytes_written': str(wr_bytes),
                                      'number_of_errors': str(err)
                                    }
            runningStatus['disk'] = diskDict


            netDict = {}
            interfaceTypes = xml.getElementsByTagName('interface')
            count = 0
            for interfaceType in interfaceTypes:
                netname = 'eth' + str(count)
                count = count + 1
                ifaceDict = {}
                interfaceNodes = interfaceType.childNodes
                for interfaceNode in interfaceNodes:
                    if interfaceNode.nodeName[0:1] != '#':
                        for attr in interfaceNode.attributes.keys():
                            if interfaceNode.attributes[attr].name == 'address':
                                mac = str(interfaceNode.attributes[attr].value)
                                ifaceDict['mac'] = mac

                            if interfaceNode.attributes[attr].name == 'bridge':
                                bridge = str(interfaceNode.attributes[attr].value)
                                ifaceDict['bridge'] = bridge

                            if interfaceNode.attributes[attr].name == 'dev':
                                iface = str(interfaceNode.attributes[attr].value)

                                stats = dom.interfaceStats(iface)

                                ifaceDict['read_bytes'] = str(stats[0])
                                ifaceDict['read_packets'] = str(stats[1])
                                ifaceDict['read_errors'] = str(stats[2])
                                ifaceDict['read_drops'] = str(stats[3])
                                ifaceDict['write_bytes'] = str(stats[4])
                                ifaceDict['write_packets'] = str(stats[5])
                                ifaceDict['write_errors'] = str(stats[6])
                                ifaceDict['write_drops'] = str(stats[7])
                    netDict[netname] = ifaceDict
            runningStatus['net'] = netDict

            return runningStatus

        domDict = {}
        domains = self.conn.listAllDomains(0)
        if len(domains) != 0:
            for domain in domains:
                status = domStatus(domain.name())
                domDict[domain.name()] = status

        runningDict['domains'] = domDict

        self.conn.close()
        return runningDict

if __name__ == "__main__":

    #uri = 'qemu+tcp://'
    uri = 'qemu://'
    host = ''
    runningDict = ListDomainsDetailedClass(uri, host).get()
    print(json.dumps(runningDict, indent=2, sort_keys=True))



