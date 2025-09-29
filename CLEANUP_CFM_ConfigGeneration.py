#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re



def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)



def CLEANUP_CFMInterfaces(conf_file,Variables):
    
    Interfaces = Variables['interfaces']
    for port,parameters in Interfaces.items():
        description= parameters['description']
    # check if its not a bundle and configure interface 
        if "bundle" not in parameters:

        # CLEANUP_ unit interfaces

            VLAN = Variables['VLAN']
            VRF_INDEX = Variables['VRF_START']
            VRF_END = Variables['VRF_END']

            while VRF_INDEX <= VRF_END:
                VRF_ID = VRF_INDEX
            # calculate prepend 
                num_zeros = 7 - len(str(VRF_ID))
                PrePend = '0'*num_zeros    
                
                unit = VLAN
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
               
            # calculate IP address - initially set to fixed value
    # CLEANUP_ common unit parameters
                common_config = """
del protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0}
            """.format(routing_instance, port,unit)                           
                conf_file.write(common_config)
                VRF_INDEX = VRF_INDEX + 1 

        else:                
            pass
    

def CLEANUP_ConfigGeneration(Inventory):
    for hostname in Inventory:
        RouterVars = "{}.yml".format(hostname)
        ConfFile = "Config_cleanup/{}.set".format(hostname)    
        try:
            conf_file = open(ConfFile,"a+")
        except:
            print("unable to CLEANUP_ new configuration file!")
            sys.exit(0)
    
# Read in the Variables 
        Variables = ReadYamlVars(RouterVars)['SCALE']['OAM_CFM']
        try:
            CLEANUP_CFMInterfaces(conf_file,Variables)
        except:
            pass
    

if __name__ == "__main__":
    CLEANUP_ConfigGeneration()




