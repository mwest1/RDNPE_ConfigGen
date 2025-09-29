#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import CLEANUP_ServiceInterface_ConfigGeneration
import CLEANUP_QoS_ConfigGeneration



def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)


def CLEANUP_VRF(conf_file,Variables):

    VRF_BASE = Variables['VRF_BASE']
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']

    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_BASE + VRF_INDEX

    # calculate prepend 
        num_zeros = 7 - len(str(VRF_ID))
        PrePend = '0'*num_zeros    

        


        common_config = """
del routing-instances N{1}{0}R
        """.format(VRF_ID,PrePend)

        conf_file.write(common_config)

        VRF_INDEX = VRF_INDEX + 1




def CLEANUP_ConfigGeneration(Inventory):
    
    for hostname in Inventory:
        RouterVars = "{}.yml".format(hostname)
        ConfFile = "Config_cleanup/{}.set".format(hostname)    
        try:
            conf_file = open(ConfFile,"a+")
        except:
            print("unable to create new configuration file!")
            sys.exit(0)
    
# Create a list of BGP service types i.e IPv4, IPv6 and Dual stack
        BGPServices = ['L3VPN_BGP_V4','L3VPN_BGP_V6','L3VPN_BGP_DS']    
# Read in the Variables for each BGP service type

        for service in BGPServices: 
            try: 
                Variables = ReadYamlVars(RouterVars)['SCALE'][service]
                CLEANUP_VRF(conf_file,Variables)
                CLEANUP_ServiceInterface_ConfigGeneration.CLEANUP_Interfaces(conf_file,Variables)
                CLEANUP_QoS_ConfigGeneration.CLEANUP_ConfigGeneration(conf_file,Variables)
            except:
                pass
        conf_file.close()


    

if __name__ == "__main__":
    CLEANUP_ConfigGeneration()




