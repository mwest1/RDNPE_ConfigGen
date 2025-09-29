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





def CLEANUP_CosUnits(conf_file,Variables):      

# now CLEANUP the unit specific configuration and traffic control profiles
    Interfaces = Variables['interfaces']
# calculate the CIR as all these interfaces are part of interface sets
# only CIR is required.
# 

    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    UnitCount = VRF_END - VRF_INDEX + 1
    for port,attributes in Variables['class_of_service']['interfaces'].items():
        
        while VRF_INDEX <= VRF_END:
            
            unit = VLAN

        # apply TCP to interface, along with inbound classifier and 802.1P rewrite rule. 
            common_config = """
    del class-of-service interfaces {0} unit {1}
        """.format(port,unit)

            conf_file.write(common_config)         
        # apply interface into interface set
        #         if interface_set is not None:
        #             common_config = """
        # del interfaces interface-set {0} interface {1} unit {2}   
        # set interfaces interface-set {0} interface {1} unit {2}      
        #     """.format(interface_set,port,unit)

        #             conf_file.write(common_config)
            VRF_INDEX = VRF_INDEX + 1 
    
def CLEANUP_InterfaceSets(conf_file, Variables):
   CosEnableInterfaces = Variables['class_of_service']['interfaces']
   for port in Variables['class_of_service']['interfaces']:
        if CosEnableInterfaces[port]['interface_set'] is not None:
            IFLSet = Variables['class_of_service']['interfaces'][port]['interface_set']
        
    # CLEANUP interface_sets and associated TCP
            for key,values in IFLSet.items():
                interface_set_base = key

        # CLEANUP interface sets and bind interfaces into interface set 
            
                VRF_INDEX = Variables['VRF_START']
                VRF_END = Variables['VRF_END']
                interface_set_index = 1

                while VRF_INDEX <= VRF_END:
                
            # initialise member count, interface_set name 
                    member_count = values['member_count']

        # apply TCP to interface set 

                    interface_set_id = interface_set_base+"_"+str(interface_set_index)
                    common_config = """
del class-of-service interfaces interface-set {0}
del interfaces interface-set {0}
            """.format(interface_set_id)           
                    conf_file.write(common_config)
                    VRF_INDEX = VRF_INDEX + member_count  
                    interface_set_index = interface_set_index + 1    




def CLEANUP_ConfigGeneration(conf_file,Variables):
        try: 
            CLEANUP_CosUnits(conf_file,Variables)
            CLEANUP_InterfaceSets(conf_file, Variables)
        except:
             pass




    

if __name__ == "__main__":
    CLEANUP_ConfigGeneration()




