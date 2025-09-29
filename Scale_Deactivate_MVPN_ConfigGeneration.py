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


def DeactivateVRF(conf_file,Variables):

    VLAN = Variables['VLAN']
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']


    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_INDEX
        
    # calculate prepend 
        num_zeros = 7 - len(str(VRF_ID))
        PrePend = '0'*num_zeros    

        
        common_config = """
delete routing-instances N{1}{0}R protocols mvpn
delete routing-instances N{1}{0}R protocols pim
delete routing-instances N{1}{0}R provider-tunnel
        """.format(VRF_ID,PrePend,VRF_INDEX)
        conf_file.write(common_config)
        VRF_INDEX = VRF_INDEX + 1
    

def ConfigGeneration(Inventory):
    print("The deactivated Inventory is: {}".format(Inventory))
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
    
        DeactivateVRF(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




