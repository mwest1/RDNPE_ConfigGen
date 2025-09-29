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



def CreateCFMInterfaces(conf_file,Variables):
    
    Interfaces = Variables['interfaces']

    for port,parameters in Interfaces.items():
        description= parameters['description']
    # check if its not a bundle and configure interface 
        if "bundle" not in parameters:

        # create unit interfaces

            VRF_BASE = Variables['VRF_BASE']
            VRF_INDEX = Variables['VRF_START']
            VRF_END = Variables['VRF_END']

            while VRF_INDEX <= VRF_END:
                VRF_ID = VRF_BASE + VRF_INDEX
            # calculate prepend 
                num_zeros = 7 - len(str(VRF_ID))
                PrePend = '0'*num_zeros    
                
                unit = VRF_INDEX
                routing_instance = "N"+str(PrePend)+str(VRF_ID) 
               
            # calculate IP address - initially set to fixed value
    # create common unit parameters
                common_config = """
del protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0}
set protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0} apply-groups SET_CFM_CCM_1_SEC
set protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0} mep 1 interface {1}.{2}
set protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0} mep 1 priority 0
set protocols oam ethernet connectivity-fault-management maintenance-domain NBN_EVC_MD maintenance-association {0} mep 1 remote-mep 2 action-profile INTF_DOWN
            """.format(routing_instance, port,unit)                           
                conf_file.write(common_config)
                VRF_INDEX = VRF_INDEX + 1 

        else:                
            pass
    

def ConfigGeneration(Inventory):
    for hostname in Inventory:
        RouterVars = "{}.yml".format(hostname)
        ConfFile = "Configs/{}.set".format(hostname)    
        try:
            conf_file = open(ConfFile,"a+")
        except:
            print("unable to create new configuration file!")
            sys.exit(0)
    
# Read in the Variables 
        Variables = ReadYamlVars(RouterVars)['SCALE']['OAM_CFM']
        CreateCFMInterfaces(conf_file,Variables)
    

if __name__ == "__main__":
    ConfigGeneration()




