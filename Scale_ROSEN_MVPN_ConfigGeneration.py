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
set routing-instances N{1}{0}R description "{3}, VRF N{1}{0}R"
set routing-instances N{1}{0}R route-distinguisher 65530:{0}
set routing-instances N{1}{0}R vrf-target target:65530:{0}
set routing-instances N{1}{0}R vrf-table-label
set routing-instances N{1}{0}R no-vrf-propagate-ttl
set routing-instances N{1}{0}R protocols pim vpn-group-address 239.252.0.{2}
 """.format(VRF_ID,PrePend,VRF_INDEX,VRF_DESCRIPTION)

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
                routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                common_config = """
set routing-instances {2} protocols pim interface {0}.{1}
            """.format(port,unit,routing_instance)
                conf_file.write(common_config)
                VRF_INDEX = VRF_INDEX + 1
        else:
            pass


def Scale_RP(conf_file,Variables,service):
    
    VLAN = Variables['VLAN']
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    Interfaces = Variables['interfaces']


    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_INDEX
    # calculate prepend 
        num_zeros = 7 - len(str(VRF_ID))
        PrePend = '0'*num_zeros

        if  "STATIC" in service:
            if Variables['RP_addr']:
                RP = Variables['RP_addr']
                common_config = """
set routing-instances N{1}{0}R protocols pim rp static address {2}
             """.format(VRF_ID,PrePend,RP)
            else:
                RP = Variables['RP_local']
                common_config = """
set routing-instances N{1}{0}R protocols pim rp local address {2}
             """.format(VRF_ID,PrePend,RP)

            conf_file.write(common_config)
        
        if "AUTO" in service:
            
            common_config = """
set routing-instances N{1}{0}R protocols pim rp auto-rp discovery
set routing-instances N{1}{0}R protocols pim dense-groups 224.0.1.39/32
set routing-instances N{1}{0}R protocols pim dense-groups 224.0.1.40/32
            """.format(VRF_ID,PrePend)
            conf_file.write(common_config)
        # create PIM enabled interfaces with sparse-dense
            for port,parameters in Interfaces.items():
                if "lo0" in port:
                    pass
    
                if "bundle" not in parameters:
                    # calculate prepend 
                        num_zeros = 7 - len(str(VRF_ID))
                        PrePend = '0'*num_zeros    
                        unit = VLAN
                        routing_instance = "N"+str(PrePend)+str(VRF_ID)+"R"
                        common_config = """
set routing-instances {2} protocols pim interface {0}.{1} mode sparse-dense
                    """.format(port,unit,routing_instance)
                        conf_file.write(common_config)
                else:
                    pass
                        
            else:
                pass
        
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

# create ROSEN MVPN service type

        MVPNType = ['ROSEN_MVPN_STATIC','ROSEN_MVPN_BSR','ROSEN_MVPN_AUTO']


# Read in the Variables for each BGP service type
        for service in MVPNType:
            try:   
                Variables = ReadYamlVars(RouterVars)['SCALE'][service]
                    
                CreateVRF(conf_file,Variables)
                Scale_RP(conf_file,Variables,service)
                Scale_ServiceInterface_ConfigGeneration.CreateInterfaces(conf_file,Variables)
                Scale_QoS_ConfigGeneration.ConfigGeneration(conf_file,Variables)
            except:
                pass
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




