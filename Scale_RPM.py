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



def CreateRPM(conf_file,Variables):
    #print(Variables)
    common_config = """\n"""
    
    RPMProbeCount = Variables['SCALE']['RPM_PROBE_COUNT']
    RPMSource = Variables['SCALE']['RPM_SOURCE_ADDR']
    RPMDest = Variables['SCALE']['RPM_DEST_ADDR']
    RPMVRF = Variables['SCALE']['RPM_START_VRF']
    ProbeCounter = 1

    while ProbeCounter <= RPMProbeCount:
        local_config = """
set services rpm probe TEST_PROBE_{0} test Target_{0} target address {1}
set services rpm probe TEST_PROBE_{0} test Target_{0} source-address {2}
""".format(str(ProbeCounter),RPMDest,RPMSource)
        common_config = local_config + common_config
        if  'RPM_DEST_INT' in Variables['SCALE'] and Variables['SCALE']['RPM_DEST_INT'] is not None:
            local_config = """
set services rpm probe TEST_PROBE_{0} test Target_{0} destination-interface {1}
""".format(str(ProbeCounter),Variables['SCALE']['RPM_DEST_INT'])
            common_config = local_config + common_config

        elif RPMVRF is not None:
        # calculate prepend 
            num_zeros = 7 - len(str(RPMVRF))
            PrePend = '0'*num_zeros    
            local_config = """
set services rpm probe TEST_PROBE_{0} test Target_{0} routing-instance N{1}{2}R
""".format(str(ProbeCounter),PrePend,RPMVRF)
            common_config = local_config + common_config
            

        else:
            pass
        RPMVRF = RPMVRF + 1
        ProbeCounter = ProbeCounter +1
    
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
        CreateRPM(conf_file,Variables)
    

if __name__ == "__main__":
    ConfigGeneration()




