from django.shortcuts import render
import sys
import libvirt
from hurry.filesize import size
from xml.dom import minidom
from django.template import RequestContext, context
from vrtManager.hostdetails import force_shutdown, get_cpu_usage, get_instance_managed_save_image, get_instance_memory, get_instance_status, get_instance_vcpu, get_memory_usage, get_networks_info, get_node_info,hypervisor_type, managed_save_remove, managedsave, resume, shutdown, start, suspend
from libvirt import libvirtError
from django.http import HttpResponse, HttpResponseRedirect
import json
import time
from rest_framework.views import APIView 
import numpy 

class hostusage(APIView):
    """
    Return Memory and CPU Usage
    """
    authentication_classes=[]
    permission_classes=[]

    def get(self,request,format=None):
        points = 5
        datasets = {}
        cookies = {}
        curent_time = time.strftime("%H:%M:%S")

        try:

            conn = libvirt.open('qemu:///system')
            cpu_usage = get_cpu_usage(conn)

        except libvirtError:
            cpu_usage = 0
            mem_usage = 0

        try:
            cookies['cpu'] = request.COOKIES.get('cpu')
            cookies['mem'] = request.COOKIES.get('meme')
            cookies['timer'] = request.COOKIES.get('timer')
        except KeyError:
            cookies['cpu'] = None
            cookies['mem'] = None

        if not cookies['cpu'] and not cookies['mem']:
            datasets['cpu'] = [0]
            datasets['mem'] = [0]
            datasets['timer'] = [curent_time]
        else:
            datasets['cpu'] = eval(str(cookies['cpu']))
            datasets['mem'] = eval(str(cookies['mem']))
            datasets['timer'] = eval(str(cookies['timer']))

        datasets['timer'].append(curent_time)
        datasets['cpu'].append(int(cpu_usage['usage']))


        if len(datasets['timer']) > points:
            datasets['timer'].pop(0)
        if len(datasets['cpu']) > points:
            datasets['cpu'].pop(0)


       


        data = json.dumps({'labels': datasets['timer'],'data': datasets['cpu']})
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        response.cookies['cpu'] = datasets['cpu']
        response.cookies['timer'] = datasets['timer']
        response.write(data)
        return response

def home(request):
    test = ""
    try:
        conn = libvirt.open('qemu:///system')

        if conn == None:
            test = 'Failed to open connection to qemu:///system' + str(file=sys.stderr)
        else:
            test = 'good'+' Connection is Alive: '+str(conn.isAlive())
            
    except:
        test = "dont have permissions"
    

    hostname, host_arch, host_memory, logical_cpu, model_cpu, uri_conn = get_node_info(conn)
    hypervisor = hypervisor_type(conn)
    mem_usage = get_memory_usage(conn)
    cpu_usage = get_cpu_usage(conn)
    network = get_networks_info(conn)
    print(network)
    
    
    context={
        'test':test,
        'hostname':hostname,
        'host_arch':host_arch,
        'host_memory':size(host_memory),
        'logical_cpu':logical_cpu,
        'model_cpu':model_cpu,
        'uri_conn':uri_conn,
        'hypervisor':hypervisor,
        }
        
    return render(request,"home.html",context)


def instances(request):
    """
    Instances block
    """

    errors = []
    instances = []
    time_refresh = 8000
    get_instances = []
    conn = None

    test = ""
    try:
        conn = libvirt.open('qemu:///system')

        if conn == None:
            test = 'Failed to open connection to qemu:///system' + str(file=sys.stderr)
        else:
            test = 'good'+' Connection is Alive: '+str(conn.isAlive())
            
    except:
        test = "dont have permissions"

    get_instances = conn.listAllDomains(0)

    for instance in get_instances:
        name = instance.name()
        uuid=instance.UUIDString()
        instances.append({'name': name,
                          'status': get_instance_status(conn,name),
                          'uuid': uuid,
                          'memory': get_instance_memory(conn,name),
                          'vcpu': get_instance_vcpu(conn,name),
                          'has_managed_save_image': get_instance_managed_save_image(conn,name)})
    if conn:
        try:
            if request.method == 'POST':
                name = request.POST.get('name', '')
                if 'start' in request.POST:
                    start(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'shutdown' in request.POST:
                    shutdown(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'destroy' in request.POST:
                    force_shutdown(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'managedsave' in request.POST:
                    managedsave(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'deletesaveimage' in request.POST:
                    managed_save_remove(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'suspend' in request.POST:
                    suspend(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
                if 'resume' in request.POST:
                    resume(conn,name)
                    return HttpResponseRedirect(request.get_full_path())
            conn.close()
        except libvirtError as err:
            errors.append(err)
    context={
       'instances': instances
    }

    return render(request,"vmachines.html",context)

"""network"""

def networks(request):
    errors = []

    try:
        conn = libvirt.open('qemu:///system')
    
        networks = get_networks_info(conn)
        conn.close()
    except libvirtError as err:
        errors.append(err)

    context={
        'errors':errors,
        'networks':networks
    }
    return render(request,"networks.html",context)
