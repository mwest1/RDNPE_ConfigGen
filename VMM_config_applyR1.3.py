#!/usr/bin/env python3

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
from lxml import etree
from pathlib import Path
import yaml
import sys
import time

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

def LoadConfigConfirmed(BackupDir,Inventory):
        for host, parameters in Inventory.items():
            host_ip = parameters["ip"]
            port = parameters["port"]
            username = parameters["username"]
            password = parameters ["password"]
            CnfFile= str(host) + ".set"
            filename = BackupDir/CnfFile
            print(filename)
            dev = Device(host=host_ip,user=username,passwd=password,port=port)
            try:
                dev.open()
                dev.timeout = 300
                #Config (dev, mode='ephemeral', ephemeral_instance='LAWFUL_INTERCEPT') as cu:
                with Config(dev) as cu:
                    cu.load(path=filename, format="set", merge=True, ignore_warning=True)
                    #cu.pdiff()
                    cu.commit(ignore_warning=True,confirm=15,timeout=180)
                dev.close()
            except ConnectError as err:
                print("Cannot connect to device: {0} due to {1}".format(host,err))
                pass
            except Exception as err:
                print("failed to backup host due to {}".format(err))
                pass

def ConfigConfirm(Inventory):
        for host, parameters in Inventory.items():
            host_ip = parameters["ip"]
            port = parameters["port"]
            username = parameters["username"]
            password = parameters ["password"]
            dev = Device(host=host_ip,user=username,passwd=password,port=port)
            try:
                dev.open()
                dev.timeout = 180
                with Config(dev,mode='private') as cu:
                    cu.commit(ignore_warning=True)
                dev.close()
                print("Configuration Confirmed for host {}".format(host))
            except ConnectError as err:
                print("Cannot connect to device: {0} due to {1}".format(host,err))
                pass
            except Exception as err:
                print("failed to backup host due to {}".format(err))
                pass  


def main():
    yaml_file = (input("Enter host file location (default PE_hosts.yml):") or "PE_hosts.yml")
    print(yaml_file)
    Inventory = GetInventory(yaml_file)
    
    BackupDir = Path(input("Enter folder for configuration repository:") or "Configs")
# peform a commit confirmed on all nodes
    LoadConfigConfirmed(BackupDir,Inventory)
    time.sleep(10)
# Commit the configuration if the node is still reachable, otherwise automatic rollback will occur. 
    ConfigConfirm(Inventory)


    


main()

