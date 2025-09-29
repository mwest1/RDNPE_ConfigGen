#!/usr/bin/env python3

import pexpect
import sys
import time
import os
import yaml



def GetInventory(yaml_file):
    try: 
        with open(yaml_file,"r") as yaml_file:
            try:
                Inventory = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
            #print(parsed_yaml)
            return Inventory
            
    except:
        print("Unable to open file {0}. Please check yaml file for host exists.".format(yaml_file))
        sys.exit(0)

def SSHTunnel(hostname,parameters):
    # read in the paramaters

    local_port = parameters['local_port']
    tunnel_ip = parameters['tunnel_ip']
    tunnel_port = parameters['tunnel_port']
    username = parameters['username']
    password = parameters['password']
    tunnel_host = parameters['tunnel_host']
    host_port = parameters['host_port']
    host_expect_string = parameters['host_expect_string'] 


    try: 
        print("Setting SSH tunnel for host {}".format(hostname))
        #command = "nohup ssh -L {}:{}:22 mwest1@127.0.0.1 -p 2201 -fN &".format(port,hostip)
        command = "nohup ssh -L {}:{}:{} {}@{} -p {} -fN &".format(local_port,tunnel_ip,tunnel_port,username,tunnel_host,host_port)
        #command = "nohup ssh -L {}:{}:{}  {}@{} -p {} -fN &".format(local_port,tunnel_ip,tunnel_port,username,tunnel_host,host_port)
        if password is None:
            SSHProcesses = os.system(command)
            time.sleep(1)
        elif host_expect_string is None:
            #used if username/password prompt is required. 
            sshtunnel = pexpect.spawn(command, encoding='utf-8')
            print(command)
            #sshtunnel.logfile = sys.stdout
            #print(command)
            expect_string = "mwest@{}'s password:".format(tunnel_host)
            sshtunnel.expect(expect_string)
            #sshtunnel.expect("mwest@qnc-css-lnx02's password:")
            sshtunnel.sendline("{}\r\n".format(password))

            time.sleep(1)

        else:
            #used if username/password prompt is required. 
            sshtunnel = pexpect.spawn(command, encoding='utf-8')
            print(command)
            #sshtunnel.logfile = sys.stdout
            #print(command)
            sshtunnel.expect(host_expect_string)
            #sshtunnel.expect("mwest@qnc-css-lnx02's password:")
            sshtunnel.sendline("{}\r\n".format(password))

            time.sleep(1)
      
            
    except Exception as e:
        print("SSH Tunnel for host {} failed.".format(hostname))
        print(e)

def main():
    
    # get the inventory file
    yaml_file = (input("Enter Base inventory (default Tunnel.yml):") or "Tunnel.yml")
    
    Inventory = GetInventory(yaml_file)

    # Create the SSH tunnel for each host in the inventory 
    for hostname,paramaters in Inventory.items():
        SSHTunnel(hostname,paramaters)
    
    print("Script complete. The list of SSH processes is shown below")
    SSHProcesses = os.system('ps -ef | grep ssh')
    print(SSHProcesses)
    
main()

