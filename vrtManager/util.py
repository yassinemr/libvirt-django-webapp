import random
import libxml2
import libvirt



def cpu_version(ctx):
    for info in ctx.xpathEval('/sysinfo/processor/entry'):
        elem = info.xpathEval('@name')[0].content
        if elem == 'version':
            return info.content
    return 'Unknown'


def get_xml_path(xml, path=None, func=None):
    """
    Return the content from the passed xml xpath, or return the result
    of a passed function (receives xpathContext as its only arg)
    """
    doc = None
    ctx = None
    result = None

    try:
        doc = libxml2.parseDoc(xml)
        ctx = doc.xpathNewContext()

        if path:
            ret = ctx.xpathEval(path)
            if ret is not None:
                if type(ret) == list:
                    if len(ret) >= 1:
                        result = ret[0].content
                else:
                    result = ret

        elif func:
            result = func(ctx)

        else:
            raise ValueError("'path' or 'func' is required.")
    finally:
        if doc:
            doc.freeDoc()
        if ctx:
            ctx.xpathFreeContext()
    return result


def pretty_mem(val):
    val = int(val)
    if val > (10 * 1024 * 1024):
        return "%2.2f GB" % (val / (1024.0 * 1024.0))
    else:
        return "%2.0f MB" % (val / 1024.0)


def pretty_bytes(val):
    val = int(val)
    if val > (1024 * 1024 * 1024):
        return "%2.2f GB" % (val / (1024.0 * 1024.0 * 1024.0))
    else:
        return "%2.2f MB" % (val / (1024.0 * 1024.0))


def hypervisor_type(self):
        """Return hypervisor type"""
        return get_xml_path(self.get_cap_xml(), "/capabilities/guest/arch/domain/@type")

def get_cap_xml(conn):
        """Return xml capabilities"""
        return conn.getCapabilities()