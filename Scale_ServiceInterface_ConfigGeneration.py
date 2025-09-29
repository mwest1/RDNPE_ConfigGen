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

    # If this is a loopback just configure ipv4 address for each unit
        if "lo0" in port:
            VLAN = Variables['VLAN']
            VRF_INDEX = Variables['VRF_START']
            VRF_END = Variables['VRF_END']
            lo0_Addr = parameters['ipv4_addr']

            while VRF_INDEX <= VRF_END:
                VRF_ID = VRF_INDEX
            # calculate prepend 
                num_zeros = 7 - len(str(VRF_ID))
                PrePend = '0'*num_zeros    
                
                unit = VLAN
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                description = "Loopback for MVPN {}".format(routing_instance)
            
                common_config = """
set interfaces {0} unit {1} description "{2}"
set interfaces {0} unit {1} family inet address {3}
set routing-instances {4} interface {0}.{1}
            """.format(port,unit,description,lo0_Addr,routing_instance)
                conf_file.write(common_config)
                VRF_INDEX = VRF_INDEX + 1
                VLAN = VLAN + 1  

    # check if its not a bundle and configure interface 
        elif "bundle" not in parameters:
            description= parameters['description']
            mtu = parameters['mtu']
            common_config = """
set interfaces {0} description "{1}"
set interfaces {0} mtu {2}
set interfaces {0} per-unit-scheduler
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

            VLAN = Variables['VLAN']
            VRF_INDEX = Variables['VRF_START']
            VRF_END = Variables['VRF_END']

            while VRF_INDEX <= VRF_END:
                VRF_ID = VRF_INDEX
            # calculate prepend 
                num_zeros = 7 - len(str(VRF_ID))
                PrePend = '0'*num_zeros    
                
                unit = VLAN
                vlan_id = VLAN
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                description = "Service interface for {}".format(routing_instance)
            
                common_config = """
delete interfaces {0} unit {1}
set interfaces {0} unit {1} description "{2}"
set interfaces {0} unit {1} vlan-id {3}
set routing-instances {4} interface {0}.{1}
            """.format(port,unit,description,vlan_id,routing_instance)
                conf_file.write(common_config)
                if 'ipv4_addr_start' in parameters.keys():
                    # calculate IP address - initially set to fixed value
                    ipv4_addr_start = parameters['ipv4_addr_start']
                    if ipv4_addr_start is not None:
                        ipv4_mask = parameters['ipv4_mask']
                        ipv4_addr = str(ipv4_addr_start)+"/"+str(ipv4_mask)
                #  Configure ipv4 address
                        common_config = """
set interfaces {0} unit {1} family inet address {2}
                        """.format(port,unit,ipv4_addr)
                        conf_file.write(common_config)
                if 'ipv6_addr_start' in parameters.keys():
                    # calculate IP address - initially set to fixed value
                    ipv6_addr_start = parameters['ipv6_addr_start']
                    if ipv6_addr_start is not None:
                        ipv6_mask = parameters['ipv6_mask']
                        ipv6_addr = str(ipv6_addr_start)+"/"+str(ipv6_mask)
            #  Configure ipv4 address
                        common_config = """
set interfaces {0} unit {1} family inet6 address {2}
                        """.format(port,unit,ipv6_addr)
                        conf_file.write(common_config)
                VRF_INDEX = VRF_INDEX + 1
                VLAN = VLAN + 1 


        else:                
            bundle = parameters['bundle']
            description= parameters['description']
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
set interfaces {0} per-unit-scheduler
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




