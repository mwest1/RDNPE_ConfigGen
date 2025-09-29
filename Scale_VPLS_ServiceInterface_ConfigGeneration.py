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



def CreateInterfaces(conf_file,Variables):
    
    Interfaces = Variables['interfaces']

    for port,parameters in Interfaces.items():
        description= parameters['description']
    # check if its not a bundle and configure interface 
        if "bundle" not in parameters:
            mtu = parameters['mtu']
            common_config = """
set interfaces {0} description "{1}"
set interfaces {0} mtu {2}
set interfaces {0} hierarchical-scheduler
set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
                """.format(port,description,mtu)
            conf_file.write(common_config)
            if "ae" in port:
                common_config = """
set interfaces {0} aggregated-ether-options lacp active periodic fast
                """.format(port)
                conf_file.write(common_config)

            else:              
                pass

        # create unit interfaces

            VRF_BASE = Variables['VRF_BASE']
            VRF_INDEX = Variables['VRF_START']
            VRF_END = Variables['VRF_END']
            SITES = Variables['site']

            while VRF_INDEX <= VRF_END:
                VRF_ID = VRF_BASE + VRF_INDEX
            # calculate prepend 
                num_zeros = 7 - len(str(VRF_ID))
                PrePend = '0'*num_zeros    
                
                unit = VRF_INDEX
                vlan_id = VRF_INDEX
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                description = "VPLS Service interface for {}".format(routing_instance)

                common_config = """
                """
                for site,parameters in SITES.items():
                    port = parameters['interface']
                    interface_config = """
set interfaces {0} unit {1} apply-groups-except SET_LOGICAL_MTU
set interfaces {0} unit {1} description "{2}"
set interfaces {0} unit {1} encapsulation vlan-vpls
set interfaces {0} unit {1} bandwidth 10m
set interfaces {0} unit {1} vlan-id {1}
set interfaces {0} unit {1} family vpls
set routing-instances {3} interface {0}.{1}
                    """.format(port,vlan_id,description,routing_instance)
                    
                    common_config = common_config + interface_config

                conf_file.write(common_config)

                VRF_INDEX = VRF_INDEX +1


        else:                
            bundle = parameters['bundle']
    # check to see if interface is part of a bundle 
            if bundle is not None:
                common_config = """
set interfaces {0} description "{1}"
set interfaces {0} gigether-options 802.3ad {2}
                """.format(port,description,bundle)
                conf_file.write(common_config)
            else: 
                mtu = parameters['mtu']
                common_config = """
set interfaces {0} description "{1}"
set interfaces {0} mtu {2}
set interfaces {0} hierarchical-scheduler
set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
                """.format(port,description,mtu)
                conf_file.write(common_config)






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
        Variables = ReadYamlVars(RouterVars)
        CreateInterfaces(conf_file,Variables)
    

if __name__ == "__main__":
    ConfigGeneration()




