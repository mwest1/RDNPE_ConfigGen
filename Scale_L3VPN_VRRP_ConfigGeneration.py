#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import Scale_VRRP_ServiceInterface_ConfigGeneration
import Scale_QoS_ConfigGeneration



def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)


def CreateVRF(conf_file,Variables):

    try:
        VRF_BASE = Variables['VRF_BASE']
        VRF_INDEX = Variables['VRF_START']
        VRF_END = Variables['VRF_END']
        VRF_DESCRIPTION = Variables['description']

        while VRF_INDEX <= VRF_END:
            VRF_ID = VRF_BASE + VRF_INDEX
            
        # calculate prepend 
            num_zeros = 7 - len(str(VRF_ID))
            PrePend = '0'*num_zeros    

            


            common_config = """
del routing-instances N{1}{0}R
set routing-instances N{1}{0}R instance-type vrf
set routing-instances N{1}{0}R routing-options maximum-prefixes 10000
set routing-instances N{1}{0}R routing-options maximum-prefixes threshold 80
set routing-instances N{1}{0}R routing-options auto-export
set routing-instances N{1}{0}R description "{2} VRF,N{1}{0}R"
set routing-instances N{1}{0}R route-distinguisher 65530:{0}
set routing-instances N{1}{0}R vrf-target target:65530:{0}
set routing-instances N{1}{0}R vrf-table-label
set routing-instances N{1}{0}R no-vrf-propagate-ttl
            """.format(VRF_ID,PrePend,VRF_DESCRIPTION)

            conf_file.write(common_config)

            VRF_INDEX = VRF_INDEX + 1
    except:
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
        Variables = ReadYamlVars(RouterVars)['SCALE']['L3VPN_VRRP']
    
        CreateVRF(conf_file,Variables)
        Scale_VRRP_ServiceInterface_ConfigGeneration.CreateInterfaces(conf_file,Variables)
        Scale_QoS_ConfigGeneration.ConfigGeneration(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




