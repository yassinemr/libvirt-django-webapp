from vrtManager.util import get_xml_path,cpu_version,get_cap_xml
import time


"""host"""

def get_node_info(conn):
    info = []
    info.append(conn.getHostname())
    info.append(conn.getInfo()[0])
    info.append(conn.getInfo()[1] * 1048576)
    info.append(conn.getInfo()[2])
    info.append(get_xml_path(conn.getSysinfo(0), func=cpu_version))
    info.append(conn.getURI())
    return info

def hypervisor_type(conn):
    """Return hypervisor type"""
    return get_xml_path(get_cap_xml(conn), "/capabilities/guest/arch/domain/@type")

def get_memory_usage(conn):
        """
        Function return memory usage on node.
        """
        get_all_mem = conn.getInfo()[1] * 1048576
        get_freemem = conn.getMemoryStats(-1, 0)
        if type(get_freemem) == dict:
            free = (list(get_freemem.values())[0] +
                    list(get_freemem.values())[2] +
                    list(get_freemem.values())[3]) * 1024
            percent = (100 - ((free * 100) / get_all_mem))
            usage = (get_all_mem - free)
            mem_usage = {'usage': usage, 'percent': percent}
        else:
            mem_usage = {'usage': None, 'percent': None}
        return mem_usage

def get_cpu_usage(conn):
        """
        Function return cpu usage on node.
        """
        prev_idle = 0
        prev_total = 0
        cpu = conn.getCPUStats(-1, 0)
        if type(cpu) == dict:
            for num in range(2):
                idle = list(conn.getCPUStats(-1, 0).values())[1]
                total = sum(list(conn.getCPUStats(-1, 0).values()))
                diff_idle = idle - prev_idle
                diff_total = total - prev_total
                diff_usage = (1000 * (diff_total - diff_idle) / diff_total + 5) / 10
                prev_total = total
                prev_idle = idle
                if num == 0:
                    time.sleep(1)
                else:
                    if diff_usage < 0:
                        diff_usage = 0
        else:
            return {'usage': None}
        return {'usage': diff_usage}

"""instance"""

def get_instance_status(conn, name):
    inst = conn.lookupByName(name)
    return inst.info()[0]

def get_instance_memory(conn, name):
        inst = conn.lookupByName(name)
        mem = get_xml_path(inst.XMLDesc(0), "/domain/currentMemory")
        return int(mem) / 1024

def get_instance_vcpu(conn, name):
        inst = conn.lookupByName(name)
        cur_vcpu = get_xml_path(inst.XMLDesc(0), "/domain/vcpu/@current")
        if cur_vcpu:
            vcpu = cur_vcpu
        else:
            vcpu = get_xml_path(inst.XMLDesc(0), "/domain/vcpu")
        return vcpu

def get_instance_managed_save_image(conn, name):
        inst = conn.lookupByName(name)
        return inst.hasManagedSaveImage(0)

def start(conn, name):
    dom = conn.lookupByName(name)
    dom.create()

def shutdown(conn, name):
    dom = conn.lookupByName(name)
    dom.shutdown()

def force_shutdown(conn, name):
    dom = conn.lookupByName(name)
    dom.destroy()



def managedsave(conn, name):
    dom = conn.lookupByName(name)
    dom.managedSave(0)

def managed_save_remove(conn, name):
    dom = conn.lookupByName(name)
    dom.managedSaveRemove(0)

def suspend(conn, name):
    dom = conn.lookupByName(name)
    dom.suspend()

def resume(conn, name):
    dom = conn.lookupByName(name)
    dom.resume()

"""network"""
def get_networks(conn):
    virtnet = []
    for net in conn.listNetworks():
        virtnet.append(net)
    for net in conn.listDefinedNetworks():
        virtnet.append(net)
    return virtnet

def get_networks_info(conn):
    virtnet = []
    for net in conn.listNetworks():
        virtnet.append(net)
    for net in conn.listDefinedNetworks():
        virtnet.append(net)
    networks = []
    for network in virtnet:
        net = conn.networkLookupByName(network)
        net_status = net.isActive()
        net_bridge = net.bridgeName()
        net_forwd = get_xml_path(net.XMLDesc(0), "/network/forward/@mode")
        networks.append({'name': network, 'status': net_status,
                            'device': net_bridge, 'forward': net_forwd})
        
    return networks