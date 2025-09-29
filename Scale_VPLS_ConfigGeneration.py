#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import Scale_VPLS_ServiceInterface_ConfigGeneration
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
    SITES = Variables['site']
    LO0 = Variables['Lo0_addr']

    while VRF_INDEX <= VRF_END:
        VRF_ID = VRF_BASE + VRF_INDEX
        
    # calculate prepend 
        num_zeros = 7 - len(str(VRF_ID))
        PrePend = '0'*num_zeros    

        


        common_config = """
del routing-instances N{1}{0}R
set routing-instances N{1}{0}R instance-type vpls
set routing-instances N{1}{0}R apply-groups-except SET_GR_ENABLE
set routing-instances N{1}{0}R apply-groups-except SET_BGP_PIC
set routing-instances N{1}{0}R description "VPLS scale testing instance,N{1}{0}R"
set routing-instances N{1}{0}R route-distinguisher {2}:{0}
set routing-instances N{1}{0}R vrf-target target:65530:{0}
set routing-instances N{1}{0}R protocols vpls mac-table-size 500
set routing-instances N{1}{0}R protocols vpls interface-mac-limit 200
set routing-instances N{1}{0}R protocols vpls no-tunnel-services
set routing-instances N{1}{0}R protocols vpls mac-flush
set routing-instances N{1}{0}R instance-type vpls
set routing-instances N{1}{0}R provider-tunnel rsvp-te label-switched-path-template P2MP_LSP
        """.format(VRF_ID,PrePend,LO0)
    # Create per site configuration 

        for site,parameters in SITES.items():
            vpls_id = parameters['id']
            site_id = "N{1}{0}R_{2}".format(VRF_ID,PrePend,site)
            preference = parameters['preference']
            port = parameters['interface']
            if preference is None:
                site_config = """
set routing-instances N{1}{0}R protocols vpls site {2} site-identifier {3}
set routing-instances N{1}{0}R protocols vpls site {2} interface {5}.{6}
                """.format(VRF_ID,PrePend,site_id,vpls_id,preference,port,VRF_INDEX)
            else: 
                site_config = """
set routing-instances N{1}{0}R protocols vpls site {2} site-identifier {3}
set routing-instances N{1}{0}R protocols vpls site {2} multi-homing
set routing-instances N{1}{0}R protocols vpls site {2} site-preference {4}
set routing-instances N{1}{0}R protocols vpls site {2} interface {5}.{6}
                """.format(VRF_ID,PrePend,site_id,vpls_id,preference,port,VRF_INDEX)
            
            common_config = common_config + site_config
    

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

# Read in the Variables for each BGP service type
        Variables = ReadYamlVars(RouterVars)['SCALE']['VPLS']
        CreateVRF(conf_file,Variables)
        Scale_VPLS_ServiceInterface_ConfigGeneration.CreateInterfaces(conf_file,Variables)
        Scale_QoS_ConfigGeneration.ConfigGeneration(conf_file,Variables)            

        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




