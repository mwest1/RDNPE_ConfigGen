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

    VLAN = Variables['VLAN']
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    Interfaces = Variables['interfaces']
    VRF_DESCRIPTION = Variables['description']


    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_INDEX
        
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
set routing-instances N{1}{0}R protocols mvpn family any
set routing-instances N{1}{0}R protocols mvpn mvpn-mode spt-only
set routing-instances N{1}{0}R provider-tunnel rsvp-te label-switched-path-template P2MP_LSP
set routing-instances N{1}{0}R provider-tunnel selective tunnel-limit 16
set routing-instances N{1}{0}R provider-tunnel selective group ff00::/8 source ::/0 rsvp-te label-switched-path-template P2MP_LSP
set routing-instances N{1}{0}R provider-tunnel selective group ff00::/8 source ::/0 threshold-rate 1
set routing-instances N{1}{0}R provider-tunnel selective group 224.0.0.0/4 source 0/0 rsvp-te label-switched-path-template P2MP_LSP
set routing-instances N{1}{0}R provider-tunnel selective group 224.0.0.0/4 source 0/0 threshold-rate 1
        """.format(VRF_ID,PrePend,VRF_DESCRIPTION)

        conf_file.write(common_config)
        VRF_INDEX = VRF_INDEX + 1 


        # create PIM enabled interfaces 
    for port,parameters in Interfaces.items():
        
        if "bundle" not in parameters:
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
set routing-instances {4} protocols pim interface {0}.{1} mode sparse
set routing-instances {4} protocols pim interface {0}.{1} priority 0
            """.format(port,unit,description,vlan_id,routing_instance)
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

# Read in the Variables for each BGP service type
           
        Variables = ReadYamlVars(RouterVars)['SCALE']['NG_MVPN']
         
            
        CreateVRF(conf_file,Variables)
        Scale_ServiceInterface_ConfigGeneration.CreateInterfaces(conf_file,Variables)
        Scale_QoS_ConfigGeneration.ConfigGeneration(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




