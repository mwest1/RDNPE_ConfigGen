#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import HQoS_ConfigGeneration
import EVPN_ConfigGeneration
import ServiceInterface_ConfigGeneration
import L3VPN_ConfigGeneration
import Scale_L3VPN_BGP_ConfigGeneration
import Scale_L3VPN_VRRP_ConfigGeneration
import Scale_ServiceInterface_ConfigGeneration
import Scale_QoS_ConfigGeneration_Standalone
import Scale_CFM_ConfigGeneration
import Scale_NG_MVPN_ConfigGeneration
import Scale_ROSEN_MVPN_ConfigGeneration
import Scale_VPLS_ConfigGeneration

import Scale_Deactivate_MVPN_ConfigGeneration
import Scale_RPM

## Cleanup modules
import CLEANUP_L3VPN_BGP_ConfigGeneration
import CLEANUP_L3VPN_VRRP_ConfigGeneration
import CLEANUP_CFM_ConfigGeneration
import CLEANUP_NG_MVPN_ConfigGeneration
import CLEANUP_ROSEN_MVPN_ConfigGeneration
import CLEANUP_VPLS_ConfigGeneration


def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)


def main():
   
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H%M%S")
    # Read in Inventory  
    Config_hosts = input("Enter Inventory file (default ConfigurationHosts.yml):") or 'ConfigurationHosts.yml'
    Inventory = ReadYamlVars(Config_hosts)
    # create a new configuration file for every host. if one exists it will be trucated.  
    for ConfigSchema,hosts in Inventory.items():
        if hosts: 
            for host in hosts:
                ConfFile = "Configs/{}.set".format(host)    
                try:
                    conf_file = open(ConfFile,"w+")
                    conf_file.close()
                except:
                    print("unable to create new configuration file!")
                    sys.exit(0)
        else: 
            pass

 

    # configure QoS configuration.
    #QoSConfigGeneration(Inventory)
    #QoS_ConfigGeneration.ConfigGeneration(Inventory['QoSTesting'])
    # add other configuration, ensure that this an append....
    
    L3VPN_ConfigGeneration.ConfigGeneration(Inventory['L3VPN'])
    #EVPN_ConfigGeneration.ConfigGeneration(Inventory['EVPNTesting'])
    #ServiceInterface_ConfigGeneration.ConfigGeneration(Inventory['INTERFACES'])
    
    try:
        Scale_RPM.ConfigGeneration(Inventory['RPM'])
    except Exception as e:
        print(f"unable to create RPM configuration for host {host}, due to {e}")
   
   # $$$$$$$$$$ For Scale testing 
    try: 
        Scale_L3VPN_BGP_ConfigGeneration.ConfigGeneration(Inventory['L3VPN'])
    except:
        print("unable to create L3VPN configuration for host {} ".format(host))
       

    try: 
        Scale_L3VPN_VRRP_ConfigGeneration.ConfigGeneration(Inventory['L3VPN'])
    except:
        print("unable to create VRRP configuration for host {} ".format(host))
        

    try: 
        Scale_NG_MVPN_ConfigGeneration.ConfigGeneration(Inventory['NG_MVPN'])
        print("Calling NG MVPN configuration for host {}".format(host))
    except:
        print("unable to create NG MVPN configuration for host {} ".format(host))
        
    
    try: 
        Scale_ROSEN_MVPN_ConfigGeneration.ConfigGeneration(Inventory['ROSEN_MVPN'])
    except:
        print("unable to create Rosen MVPN configuration for host {} ".format(host))
        

    try: 
        Scale_CFM_ConfigGeneration.ConfigGeneration(Inventory['CFM'])
    except:
        print("unable to create Ethernet OAM - CFM  configuration for host {} ".format(host))
           
    
    try: 
       Scale_VPLS_ConfigGeneration.ConfigGeneration(Inventory['VPLS'])
    except:
        print("unable to create VPLS configuration for host {} ".format(host))
           
    

    #HQoS_ConfigGeneration.ConfigGeneration(Inventory['HQoS'])
    
    try: 
        HQoS_ConfigGeneration.ConfigGeneration(Inventory['HQoS'])
    except Exception as e :
        print("unable to create HQOS configuration for host {} ".format(host))
        print(e)
        



   
   
    # Create cleanup files


     # create a new cleanup file for every host. if one exists it will be trucated.  
    for ConfigSchema,hosts in Inventory.items():
        if hosts: 
            for host in hosts:
                ConfFile = "Config_cleanup/{}.set".format(host)    
                try:
                    conf_file = open(ConfFile,"w+")
                    conf_file.close()
                except:
                    print("unable to create new configuration file!")
                    sys.exit(0)
        else: 
            pass
                

    CLEANUP_L3VPN_BGP_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['L3VPN'])
    CLEANUP_L3VPN_VRRP_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['L3VPN'])
    CLEANUP_CFM_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['L3VPN'])
    CLEANUP_NG_MVPN_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['NG_MVPN'])
    CLEANUP_ROSEN_MVPN_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['ROSEN_MVPN'])
    CLEANUP_VPLS_ConfigGeneration.CLEANUP_ConfigGeneration(Inventory['VPLS'])



    
    
    #Scale_ServiceInterface_ConfigGeneration.ConfigGeneration(Inventory['L3VPN'])
   
    
    
    # Scale_QoS_ConfigGeneration.ConfigGeneration(Inventory['MX304'])
    # Scale_Deactivate_L3VPN_QoS_ConfigGeneration.ConfigGeneration(Inventory['Deactivate'])
    # Scale_Deactivate_MVPN_ConfigGeneration.ConfigGeneration(Inventory['Deactivate']) 
    


    

if __name__ == "__main__":
    main()




