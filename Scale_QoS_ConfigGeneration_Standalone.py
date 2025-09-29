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

def CalculateBurst(burstseconds,rate):
    

    exponent = (re.split('[0-9]',rate)[-1])
    rate = int(re.split('[a-zA-Z]',rate)[0])

    if exponent == "k":
        multiplier = 1000
    elif exponent == "m": 
        multiplier = 1000000
    elif exponent == "g":
        multiplier = 1000000000
    else:
        multiplier = 1
    burstsize = int((rate*multiplier*burstseconds)/8)

    return burstsize

def CalculateGrate(UnitCount,port_speed):
    
    exponent = (re.split('[0-9]',port_speed)[-1]).lower()
    rate = int(re.split('[a-zA-Z]',port_speed)[0])

    if exponent == "k":
        multiplier = 1000
    elif exponent == "m": 
        multiplier = 1000000
    elif exponent == "g":
        multiplier = 1000000000
    unit_cir = int(rate*multiplier)/(UnitCount)
    
    num_length = len(str(unit_cir))

    if num_length <=6:
        exponent = "k"

    return unit_cir




def CreateHCOS(conf_file,Variables):
    
    common_config = """
delete class-of-service schedulers HCOS_FC0_6Q_SCHED
delete class-of-service schedulers HCOS_FC1_6Q_SCHED
delete class-of-service schedulers HCOS_FC2_6Q_SCHED
delete class-of-service schedulers HCOS_FC3_6Q_SCHED
delete class-of-service schedulers HCOS_FC4_6Q_SCHED
delete class-of-service schedulers HCOS_FC5_6Q_SCHED

set class-of-service schedulers HCOS_FC0_6Q_SCHED transmit-rate percent 5
set class-of-service schedulers HCOS_FC0_6Q_SCHED buffer-size percent 5
set class-of-service schedulers HCOS_FC0_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC1_6Q_SCHED transmit-rate percent 10
set class-of-service schedulers HCOS_FC1_6Q_SCHED buffer-size percent 5
set class-of-service schedulers HCOS_FC1_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC2_6Q_SCHED transmit-rate percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED priority low

set class-of-service schedulers HCOS_FC3_6Q_SCHED transmit-rate percent 25
set class-of-service schedulers HCOS_FC3_6Q_SCHED buffer-size percent 25
set class-of-service schedulers HCOS_FC3_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC4_6Q_SCHED transmit-rate percent 35
set class-of-service schedulers HCOS_FC4_6Q_SCHED buffer-size percent 30
set class-of-service schedulers HCOS_FC4_6Q_SCHED priority medium-low
 

set class-of-service schedulers HCOS_FC5_6Q_SCHED transmit-rate percent 10
set class-of-service schedulers HCOS_FC5_6Q_SCHED buffer-size temporal 10k
set class-of-service schedulers HCOS_FC5_6Q_SCHED priority high
 
del class-of-service scheduler-maps HCOS_6Q_SCHEDULER

set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC0 scheduler HCOS_FC0_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC1 scheduler HCOS_FC1_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC2 scheduler HCOS_FC2_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC3 scheduler HCOS_FC3_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC4 scheduler HCOS_FC4_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC5 scheduler HCOS_FC5_6Q_SCHED
        """
            
    conf_file.write(common_config)



def CreateCosUnits(conf_file,Variables):      

# now create the unit specific configuration and traffic control profiles
    Interfaces = Variables['interfaces']
# calculate the CIR as all these interfaces are part of interface sets
# only CIR is required.
# 

    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    UnitCount = VRF_END - VRF_INDEX + 1
    port = Variables['class_of_service']['interface']
    port_speed = Interfaces[port]['pir']
    unit_cir = Interfaces[port]['cir']

    # calculate the CIR for a unit based on the number of interfaces



    while VRF_INDEX <= VRF_END:
        
        unit = VLAN
        

# calculate shaper burst rate based on seconds of traffic. 
        burstseconds = 0.01 
        tcp_name = "HCOS_SHAPER_BURST10_{}_6Q".format(unit_cir)
        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))
        conf_file.write("set class-of-service traffic-control-profiles {0} scheduler-map HCOS_6Q_SCHEDULER".format(tcp_name))

        burstsize = CalculateBurst(burstseconds,unit_cir)
        common_config = """
set class-of-service traffic-control-profiles {2} guaranteed-rate {0}
set class-of-service traffic-control-profiles {2} guaranteed-rate burst-size {1}
""".format(unit_cir,burstsize,tcp_name)

        conf_file.write(common_config)

    # apply TCP to interface, along with inbound classifier and 802.1P rewrite rule. 
        common_config = """
del class-of-service interfaces {0} unit {1}
set class-of-service interfaces {0} unit {1} output-traffic-control-profile {2}
set class-of-service interfaces {0} unit {1} classifiers dscp CLASSIFY_CE_PE_DSCP
set class-of-service interfaces {0} unit {1} rewrite-rules ieee-802.1 PE_CE_DOT1P_REWRITE
    """.format(port,unit,tcp_name)

        conf_file.write(common_config)         
    # apply interface into interface set
    #         if interface_set is not None:
    #             common_config = """
    # del interfaces interface-set {0} interface {1} unit {2}   
    # set interfaces interface-set {0} interface {1} unit {2}      
    #     """.format(interface_set,port,unit)

    #             conf_file.write(common_config)
        VRF_INDEX = VRF_INDEX + 1 
    
def CreateInterfaceSets(conf_file, Variables):

# create interface_sets and associated TCP
    for key in Variables['class_of_service']['interface_set']:
        interface_set_base = key 

# read in interface set member count 
    interface_set_members = Variables['class_of_service']['interface_set'][interface_set_base]['member_count']
    interfaces_set_pir = Variables['class_of_service']['interface_set'][interface_set_base]['pir']
    interfaces_set_cir = Variables['class_of_service']['interface_set'][interface_set_base]['cir']
    tcp_name = "HCOS_GRP_SHAPER_B10_RL_{}".format(interfaces_set_cir)
    common_config = """
del class-of-service traffic-control-profiles {0}
""".format(tcp_name)
    conf_file.write(common_config)
# calculate shaper burst rate based on seconds of traffic. 
    burstseconds = 0.01
    if interfaces_set_pir is not None:
        burstsize = CalculateBurst(burstseconds,interfaces_set_pir)
        common_config = """
set class-of-service traffic-control-profiles {2} shaping-rate {0}
set class-of-service traffic-control-profiles {2} shaping-rate burst-size {1}
""".format(interfaces_set_pir,burstsize,tcp_name)
            
        conf_file.write(common_config)            
# define CIR and burst size
        if interfaces_set_cir is not None:
            burstsize = CalculateBurst(burstseconds,interfaces_set_cir)
            common_config = """
set class-of-service traffic-control-profiles {2} guaranteed-rate {0}
set class-of-service traffic-control-profiles {2} guaranteed-rate burst-size {1}
""".format(interfaces_set_cir,burstsize,tcp_name)

        conf_file.write(common_config)



# create interface sets and bind interfaces into interface set 
    
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    port = Variables['class_of_service']['interface']
    # calculate the CIR for a unit based on the number of interfaces
    interface_set_index = 1

    while VRF_INDEX <= VRF_END:
        
    # initialise member count, interface_set name 
        member_count = 1;

# apply TCP to interface set 
        while member_count <= interface_set_members:
            interface_set_id = interface_set_base+"_"+str(interface_set_index)
            common_config = """
del class-of-service interfaces interface-set {0}
set class-of-service interfaces interface-set {0} output-traffic-control-profile {1}
""".format(interface_set_id,tcp_name)           
            conf_file.write(common_config)
            unit = VLAN

# create the interface set 
            common_config = """
set interfaces interface-set {0} interface {1} unit {2}
""".format(interface_set_id,port,unit)    
            conf_file.write(common_config)
            member_count = member_count + 1
            VRF_INDEX = VRF_INDEX + 1      
        interface_set_index = interface_set_index + 1

           


def CreateIngressPolicers(conf_file, Variables):
    Interfaces = Variables['interfaces']


    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    port = Variables['class_of_service']['interface']
    interface_set = Interfaces[port]['interface_set']
    policer_pir  = Variables['class_of_service']['interface_set'][interface_set]['pir']

    # calculate the CIR for a unit based on the number of interfaces
    

    while VRF_INDEX <= VRF_END:
        
        unit = VLAN
# calculate shaper burst rate based on seconds of traffic. 
        burstseconds = 0.01
        burstsize = CalculateBurst(burstseconds,policer_pir)
        if "ae" in(port):
            policer_name = "HCOS_IFL_AE_POLICER_{}".format(policer_pir.upper())
            conf_file.write("set firewall policer {0} shared-bandwidth-policer".format(policer_name))
        else:
            policer_name = "HCOS_IFL_POLICER_{}".format(policer_pir.upper())
        common_config = """
set firewall policer {0} logical-interface-policer 
set firewall policer {0} if-exceeding bandwidth-limit {1}
set firewall policer {0} if-exceeding burst-size-limit {2}
set firewall policer {0} then discard
set interfaces {3} unit {4} layer2-policer input-policer {0}                  
            """.format(policer_name,policer_pir,burstsize,port,unit)

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
    
# Read in the Variables 
        Variables = ReadYamlVars(RouterVars)
        CreateHCOS(conf_file,Variables)
        CreateCosUnits(conf_file,Variables)
        CreateInterfaceSets(conf_file, Variables)
        CreateIngressPolicers(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




