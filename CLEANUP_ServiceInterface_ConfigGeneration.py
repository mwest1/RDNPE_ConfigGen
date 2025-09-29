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



def CLEANUP_Interfaces(conf_file,Variables):
    
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
                vlan_id = VRF_INDEX
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                description = "Service interface for {}".format(routing_instance)
            
                common_config = """
del interfaces {0} unit {1} 
            """.format(port,unit,description,vlan_id,routing_instance)
                conf_file.write(common_config)
                
                VRF_INDEX = VRF_INDEX + 1 



def CLEANUP_ConfigGeneration(Inventory):
    for hostname in Inventory:
        RouterVars = "{}.yml".format(hostname)
        ConfFile = "Configs/{}.set".format(hostname)    
        try:
            conf_file = open(ConfFile,"a+")
        except:
            print("unable to create new configuration file!")
            sys.exit(0)
    
# Read in the Variables 
        Variables = ReadYamlVars(RouterVars)

        try:
            CLEANUP_Interfaces(conf_file,Variables)
        except:
            pass

if __name__ == "__main__":
    CLEANUP_ConfigGeneration()




