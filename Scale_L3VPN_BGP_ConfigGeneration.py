#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import Scale_ServiceInterface_ConfigGeneration
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

    VRF_BASE = Variables['VRF_BASE']
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    BGP_GROUPS = Variables['BGP']
    VRF_DESCRIPTION = Variables['description']

    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_BASE + VRF_INDEX
        
    # calculate prepend 
        num_zeros = 7 - len(str(VRF_ID))
        PrePend = '0'*num_zeros    

        


        common_config = """
del routing-instances N{1}{0}R
set routing-instances N{1}{0}R instance-type vrf
set routing-instances N{1}{0}R routing-options maximum-prefixes 1000000
set routing-instances N{1}{0}R routing-options maximum-prefixes threshold 80
set routing-instances N{1}{0}R routing-options auto-export
set routing-instances N{1}{0}R description "{2}, VRF N{1}{0}R"
set routing-instances N{1}{0}R route-distinguisher 65530:{0}
set routing-instances N{1}{0}R vrf-target target:65530:{0}
set routing-instances N{1}{0}R vrf-table-label
set routing-instances N{1}{0}R no-vrf-propagate-ttl
        """.format(VRF_ID,PrePend,VRF_DESCRIPTION)

        conf_file.write(common_config)

        for group,parameters in BGP_GROUPS.items():

            BGP_PEER_AS = parameters['peer_as']
            BGP_PEERS = parameters['peer_list']

            common_config = """
set routing-instances N{1}{0}R protocols bgp group {2} apply-groups DROP_IN_BGP_COMMUNITIES
set routing-instances N{1}{0}R protocols bgp group {2} export DROP_INTERNALS
set routing-instances N{1}{0}R protocols bgp group {2} export REDIST_ALL
set routing-instances N{1}{0}R protocols bgp group {2} tcp-mss 2048
            """.format(VRF_ID,PrePend,group)

            conf_file.write(common_config)
    # create BGP peer list 
            for peer in BGP_PEERS:
                common_config = """
set routing-instances N{1}{0}R protocols bgp group {2} peer-as {3}
set routing-instances N{1}{0}R protocols bgp group {2} neighbor {4}
set routing-instances N{1}{0}R protocols bgp group {2} neighbor {4} apply-groups SET_BFD_TIMERS_PE_CE_300

            """.format(VRF_ID,PrePend,group,BGP_PEER_AS,peer)
                conf_file.write(common_config)

        VRF_INDEX = VRF_INDEX + 1




def ConfigGeneration(Inventory):
    
    for hostname in Inventory:
        RouterVars = "{}.yml".format(hostname)
        ConfFile = "Configs/{}.set".format(hostname)    
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
                CreateVRF(conf_file,Variables)
                Scale_ServiceInterface_ConfigGeneration.CreateInterfaces(conf_file,Variables)
                Scale_QoS_ConfigGeneration.ConfigGeneration(conf_file,Variables)
            except:
               pass

        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




