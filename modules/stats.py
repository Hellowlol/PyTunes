# coding=utf-8

import time
import json
from datetime import datetime, timedelta
from subprocess import PIPE
import sys
import os
import socket
import ConfigParser
import urllib2
import platform
import cherrypy
import pytunes
#from pytunes import connector
from pytunes.staticvars import get_var as html
import logging
import pwd, grp


try:
    import psutil
    importPsutil = True

except ImportError:
    logger.error("Could't import psutil. See http://psutil.googlecode.com/hg/INSTALL")
    importPsutil = False

 
class Stats:
    def __init__(self):
        self.logger = logging.getLogger('modules.stats')
        pytunes.MODULES.append({
            'name': 'System',
            'id': 'stats',
            'test': pytunes.WEBDIR + 'stats/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'stats_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'stats_name'},
                {'type': 'bool', 'label': 'Bar', 'name': 'stats_use_bars'}
        ]})

    @cherrypy.expose()
    def index(self):
        #Since many linux repos still have psutil version 0.5
        if psutil.version_info >= (0, 7):
            pass
        else:
            self.logger.error("Psutil is outdated, needs atleast version 0,7")

        return pytunes.LOOKUP.get_template('stats.html').render(scriptname='stats')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ping(self):
        """ Tests For Installation of psutil """
        self.logger.debug("Testing Stats connectivity")
        try:
            import psutil
            #psutil.version_info >= (0, 7)
            return 'happy'
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("psutil not installed or version too low ")
            return

    def trunc(self, f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        slen = len('%.*f' % (n, f))
        return str(f)[:slen]

    @cherrypy.expose()
    def uptime2(self):
        try:
            if psutil.version_info >= (2, 0, 0):
                b = psutil.boot_time()
            else:
                b = psutil.get_boot_time()
            
            d = {}
            boot = datetime.now() - datetime.fromtimestamp(b)
            boot = str(boot)
            uptime = boot[:-7]
            d['uptime'] = uptime
            return json.dumps(d)
        except Exception as e:
            self.logger.error("Could not get uptime %s" % e)
            

    @cherrypy.expose()
    def disk_usage(self):
        disks = []        
        try:
            if os.name == 'nt':
                # Need to be true, or else not network disks will show.
                for disk in psutil.disk_partitions(all=True):
                    
                    if 'cdrom' in disk.opts or disk.fstype == '':
                        #To stop windows errors if cdrom is empty
                        continue
                        
                    usage = psutil.disk_usage(disk.mountpoint)
                    dusage = usage._asdict()
                    dusage['mountpoint'] = disk.mountpoint
                    dusage['device'] = disk.device
                    dusage['fstype'] = disk.fstype
                    disks.append(dusage)
                    #rr = json.dumps(l)
                    
            if os.name == 'posix':
                
                for disk in psutil.disk_partitions(all=True):
                    usage = psutil.disk_usage(disk.mountpoint)
                    dusage = usage._asdict()
                    dusage['mountpoint'] = disk.mountpoint
                    dusage['device'] = disk.device
                    dusage['fstype'] = disk.fstype
                    disks.append(dusage)
                    #rr = json.dumps(l)
                    
        except Exception as e:
            self.logger.error("Could not get disk info %s" % e)
        
        return json.dumps(disks)

    @cherrypy.expose()
    def disk_usage2(self):
        disks = []
        fstypes = ['ext', 'ext2', 'ext3', 'ext4', 'nfs', 'nfs4', 'fuseblk', 'cifs', 'msdos', 'ntfs', 'fat', 'fat32']
        try:
            for disk in psutil.disk_partitions(all=True):
            	if 'cdrom' in disk.opts or disk.fstype == '' or disk.fstype not in fstypes:
                    pass
            	else:
                    usage = psutil.disk_usage(disk.mountpoint)
                    dusage = usage._asdict()
                    dusage['mountpoint'] = disk.mountpoint
                    dusage['device'] = disk.device
                    if disk.fstype == 'fuseblk' :
                        dusage['fstype'] = 'ntfs'
                    else:
                        dusage['fstype'] = disk.fstype
                    disks.append(dusage)
                        
        except Exception as e:
            self.logger.error("Could not get disk info %s" % e)
        
        return json.dumps(disks)



    @cherrypy.expose()
    def processes(self):
        out = ''
        procs = []
        procs_status = {}
        for p in psutil.process_iter():
            
            try:
                p.dict = p.as_dict(['username', 'get_memory_percent', 
                                    'get_cpu_percent', 'name', 'status', 'pid', 'get_memory_info', 'create_time', 'cmdline'])
                #Create a readable time
                r_time = datetime.now() - datetime.fromtimestamp(p.dict['create_time'])
                r_time = str(r_time)[:-7]
                p.dict['r_time'] = r_time
                try:
                    procs_status[p.dict['status']] += 1
                except KeyError:
                    procs_status[p.dict['status']] = 1
            except psutil.NoSuchProcess:
                self.logger.error("No Such Process")
                pass
            else:
                procs.append(p.dict)

        # processes sorted by CPU percent usage
        processes = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)
        for proc in processes:
            if len(proc['cmdline']):
                cmdline = proc['cmdline'][0]
            else:
                cmdline = 'N/A'
                
            out += html('proc_row') % (proc['pid'], proc['pid'], proc['name'], proc['username'], str(proc['cpu_percent']) + '%', cmdline, proc['status'], self.trunc(proc['memory_percent'], 2) + '%', proc['r_time'], proc['pid']) 
        return out
 


    @cherrypy.expose()
    def cpu_percent(self):
        jcpu = None
        try:
            cpu = psutil.cpu_times_percent(interval=0.4, percpu=False)
            cpu = cpu._asdict()
            jcpu = json.dumps(cpu)

            return jcpu
        except Exception as e:
            self.logger.error("Error trying to pull cpu percent: %s" % e)

    # Not in use atm.
    @cherrypy.expose()
    def cpu_times(self):
        rr = None
        try:
            cpu = psutil.cpu_times(percpu=False)
            dcpu = cpu._asdict()
            rr = json.dumps(dcpu)
            
            return rr
        except Exception as e:
            pass
    
    #Not in use as it returns threads aswell on windows
    @cherrypy.expose()
    def num_cpu(self):
        try:
            
            cpu = psutil.NUM_CPUS
            dcpu = cpu._asdict()
            jcpu  = json.dumps(dcpu)
            
            return jcpu
            
        except Exception as e:
            self.logger.error("Error trying to pull cpu cores %s" % e)

    @cherrypy.expose()
    def sizeof(self, num):
        for x in ['bytes','KB','MB','GB', 'TB']:
            if num < 1024.0:
                return "%3.2f%s" % (num, x)
            num /= 1024.0
        return "%3.2f%s" % (num, 'TB')

    @cherrypy.expose()
    def Dash(self):
        dash = {
        'total':0.0,
        'free':0.0,
        'used':0.0,
        'percent':0.0,
        'bar':''}
        free = 0.0
        used = 0.0
        total = 0.0
        percent = 0.0
        fstypes = ['ext', 'ext2', 'ext3', 'ext4', 'nfs', 'nfs4', 'fuseblk', 'cifs', 'msdos', 'ntfs', 'fat', 'fat32']
        try:
            for disk in psutil.disk_partitions(all=True):
            	if 'cdrom' in disk.opts or disk.fstype == '' or disk.fstype not in fstypes:
                    pass
            	else:
                    usage = psutil.disk_usage(disk.mountpoint)
                    total += float(usage.total)
                    free += float(usage.free)
                    used += float(usage.used)
                    #print dash
            print 'total', total, 'used', used, 'free', free
            if total:
                percent = (used/total)*100
            #print 'percent', percent, dash['percent']
            dash['bar'] = html('dash_stats') % (self.sizeof(total), self.sizeof(used), str(percent) + '%', str(100 - percent) + '%')
        except Exception as e:
            self.logger.error("Could not get dash disk info %s" % e)
        print dash
        return json.dumps(dash)

    @cherrypy.expose()
    def ShowProcess(self, pid):
        cpu = psutil.NUM_CPUS
        p = psutil.Process(int(pid))
        runtime = str(timedelta(seconds=int(time.time() - p.create_time)))
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(p.create_time)))
        proc = {}
        proc['head'] = 'Process Information'
        proc['body'] = html('stats_modal') % (' '.join(p.cmdline), pid, p.get_cpu_percent(interval=1.0), p.username, p.status, p.uids[0], p.gids[0], p.nice, self.trunc(p.get_memory_percent(), 2), starttime, runtime)
        proc['foot'] = html('kill_button') % pid + html('terminate_button') % pid + html('suspend_button') % pid + html('resume_button') % pid + html('close_button')
        return json.dumps(proc)

    @cherrypy.expose()
    def get_users(self):
        table = ''
        row6 = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        for p in pwd.getpwall():
            table += row6 % (p[0], p[2], grp.getgrgid(p[3])[0], p[3], p[5], p[6])
        return table

    @cherrypy.expose()
    def get_user(self):
        l =[]
        d = {}
        rr = None
        try:
            for user in psutil.get_users():
                duser = user._asdict()
                td = datetime.now() - datetime.fromtimestamp(duser['started'])
                td = str(td)
                td = td[:-7]
                duser['started'] = td
                rr = json.dumps(duser)
                
            return rr
            
        except Exception as e:
            self.logger.error("Pulling logged in info %s" % e)
    
    
        return rr

    @cherrypy.expose()
    def get_local_ip(self):
        # added a small delay since getting local is faster then network usage (Does not render in the html)
        time.sleep(0.1)
        d = {}
        try:
            
            ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); 
            ip.connect(('8.8.8.8', 80)) 
            local_ip =(ip.getsockname()[0])
            d['localip'] = local_ip
            return json.dumps(d)
            
        except Exception as e:
            self.logger.error("Pulling  local ip %s" % e)

    
    @cherrypy.expose()
    def get_external_ip(self):
        d = {}
        rr = None
        
        try:
            s = urllib2.urlopen('http://myexternalip.com/raw').read()
            d['externalip'] = s
            return json.dumps(d)
            
        except Exception as e:
            self.logger.error("Pulling external ip %s" % e)

    @cherrypy.expose()
    def sys_info(self):
        d = {}
        
        try:
            computer = platform.uname()
            d['system'] = computer[0]
            d['user'] = computer[1]
            d['release'] = computer[2]
            d['version'] = computer[3]
            d['machine'] = computer[4]
            d['processor'] = computer[5]
            return json.dumps(d)
            
        except Exception as e:
            self.logger.error("Pulling system info %s" % e )


    #get network usage
    @cherrypy.expose()
    def network_usage(self):
        
        try:
            nw_psutil = psutil.net_io_counters()
            nw_psutil = nw_psutil._asdict()
            
            return json.dumps(nw_psutil)
            
        except Exception as e:
            self.logger.error("Pulling network info %s" % e)
            
    @cherrypy.expose()
    def virtual_memory(self):
        d = {}
        
        try:
            mem = psutil.virtual_memory()
            mem = mem._asdict()
            return json.dumps(mem)
            
        except Exception as e:
            self.logger.error("Pulling physical memory %s" % e)

    @cherrypy.expose()
    def swap_memory(self):
        d = {}
        
        try:
            
            mem = psutil.swap_memory()
            mem = mem._asdict()
            return json.dumps(mem)
            
        except Exception as e:
            self.logger.error("Pulling swap memory %s" % e)
    
    @cherrypy.expose()
    def return_settings(self):
        d = {}
        try:
            
            d['real'] = pytunes.settings.get('stats_use_bars')
            if str(pytunes.settings.get('stats_use_bars')) == str('False'):
                d['stats_use_bars'] = 'false'
            else:
                d['stats_use_bars'] = 'true'
            
        except Exception as e:
            self.logger.error("Getting stats settings %s" % e)
            
        return json.dumps(d)
    

    @cherrypy.expose()
    def command(self, cmd=None, pid=None, signal=None):
        #pid = int(json.loads(pid))
        print 'in command', cmd, pid
        dmsg = {}
        try:
            if pid:
                p = psutil.Process(int(pid))
                name = p.name
                print 'name: ', name
            else:
                pass

            if cmd == 'kill':
                try:
                    p.terminate()
                    dmsg['status'] = 'success'
                    msg = 'Terminated process %s %s' % (name, pid)
                    p.wait()

                except psutil.NoSuchProcess:
                    msg = 'Process %s does not exist' % name
                    dmsg['status'] = 'error'

                except psutil.AccessDenied:
                    msg = 'Dont have permission to terminate/kill %s %s' % (name,pid)
                    dmsg['status'] = 'error'

                except psutil.TimeoutExpired:
                    p.kill()
                    dmsg['status'] = 'success'
                    msg = 'Killed process %s %s' % (name, pid)

                dmsg['msg'] = msg
                self.logger.info(msg)
                return json.dumps(dmsg)

            elif cmd == 'signal':
                p.send_signal(signal)
                msg = '%ed pid %s successfully with %s'% (cmd, pid, signal)
                dmsg['msg'] = msg
                self.logger.info(msg)
                return json.dumps(dmsg)

        except Exception as e:
            #print msg
            self.logger.error("Error trying to %s %s" % (cmd, e))



    @cherrypy.expose()
    def cmdpopen(self, cmd=None, popen=None):
        d = {}
        msg = None
        if not pytunes.NOSHELL:
            #print cmd,popen
            if cmd == 'popen':
                print 'in popen'
                r = psutil.Popen(popen,stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
                msg = r.communicate()
            else:
                pass
            return msg
        else:
            msg = 'Shell commands disabled. PyTunes is started with --noshell\n'
            self.logger.error(msg)
            return msg
            
  

