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

    if bool(re.match('[k|K]',exponent)):
        multiplier = 1000
    elif bool(re.match('[m|M]',exponent)):
        multiplier = 1000000
    elif bool(re.match('[g|G]',exponent)):
        multiplier = 1000000000
    else:
        multiplier = 1
    burstsize = int((rate*multiplier*burstseconds)/8)
    return burstsize

def CalculateGrate(UnitCount,port_speed):
    
    exponent = (re.split('[0-9]',port_speed)[-1]).lower()
    rate = int(re.split('[a-zA-Z]',port_speed)[0])
    
    if bool(re.match('[k|K]',exponent)):
        multiplier = 1000
    elif bool(re.match('[m|M]',exponent)):
        multiplier = 1000000
    elif bool(re.match('[g|G]',exponent)):
        multiplier = 1000000000
    UnitPIR = int(rate*multiplier)/(UnitCount)
    
    num_length = len(str(UnitPIR))

    if num_length <=6:
        exponent = "k"

    return UnitPIR




def CreateHCOS(conf_file,Variables):
    
    common_config = """
delete class-of-service schedulers HCOS_FC0_6Q_SCHED
delete class-of-service schedulers HCOS_FC1_6Q_SCHED
delete class-of-service schedulers HCOS_FC2_6Q_SCHED
delete class-of-service schedulers HCOS_FC3_6Q_SCHED
delete class-of-service schedulers HCOS_FC4_6Q_SCHED
delete class-of-service schedulers HCOS_FC5_6Q_SCHED

set class-of-service schedulers HCOS_FC0_6Q_SCHED transmit-rate percent 5
set class-of-service schedulers HCOS_FC0_6Q_SCHED buffer-size percent 25
set class-of-service schedulers HCOS_FC0_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC1_6Q_SCHED transmit-rate percent 10
set class-of-service schedulers HCOS_FC1_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC1_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC2_6Q_SCHED transmit-rate percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED priority low

set class-of-service schedulers HCOS_FC3_6Q_SCHED transmit-rate percent 25
set class-of-service schedulers HCOS_FC3_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC3_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC4_6Q_SCHED transmit-rate percent 35
set class-of-service schedulers HCOS_FC4_6Q_SCHED buffer-size percent 15
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



def CreateCosUnits(conf_file,port,UnitPIR,Variables):      

# now create the unit specific configuration and traffic control profiles
    Interfaces = Variables['class_of_service']['interfaces']
# calculate the CIR as all these interfaces are part of interface sets
# only CIR is required.
    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']
    UnitCount = VRF_END - VRF_INDEX + 1
    UnitCIR = Interfaces[port]['cir']

    # calculate the CIR for a unit based on the number of interfaces  
# calculate the CIR for a unit based on the number of interfaces

    while VRF_INDEX <= VRF_END:
        
        unit = VRF_INDEX
    
# calculate shaper burst rate based on seconds of traffic. 
        burstseconds = 0.01 
        tcp_name = "HCOS_SHAPER_BURST10_{}_6Q".format(UnitCIR)
        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))
        conf_file.write("set class-of-service traffic-control-profiles {0} scheduler-map HCOS_6Q_SCHEDULER".format(tcp_name))
        burstsize = CalculateBurst(burstseconds,UnitCIR)
        common_config = """
set class-of-service traffic-control-profiles {2} guaranteed-rate {0}
set class-of-service traffic-control-profiles {2} guaranteed-rate burst-size {1}
""".format(UnitCIR,burstsize,tcp_name)
        conf_file.write(common_config)
# If interface set is not applied then configure a PIR
        if UnitPIR is not None:
            burstsize = CalculateBurst(burstseconds,UnitPIR)
            common_config = """
set class-of-service traffic-control-profiles {2} shaping-rate {0}
set class-of-service traffic-control-profiles {2} shaping-rate burst-size {1}
        """.format(UnitPIR,burstsize,tcp_name)
            conf_file.write(common_config)


    # apply TCP to interface, along with inbound classifier and 802.1P rewrite rule. 
        common_config = """
del class-of-service interfaces {0} unit {1}
set class-of-service interfaces {0} unit {1} output-traffic-control-profile {2}
set class-of-service interfaces {0} unit {1} classifiers dscp CLASSIFY_CE_PE_DSCP
set class-of-service interfaces {0} unit {1} rewrite-rules ieee-802.1 PE_CE_DOT1P_REWRITE
    """.format(port,unit,tcp_name)

        conf_file.write(common_config)         
        VRF_INDEX = VRF_INDEX + 1 
        
def CreateInterfaceSets(conf_file,port,InterfaceSet,Variables):
    

    interface_set = Variables['class_of_service']['interfaces'][port]['interface_set'][InterfaceSet]
# read in interface set member count and shaping rates. 
    interface_set_members = interface_set['member_count']
    interfaces_set_pir = interface_set['pir']
    interfaces_set_cir = interface_set['cir']
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

    # Create the interface sets. 
    interface_set_index = 1

    while VRF_INDEX <= VRF_END:
        
    # initialise member count, interface_set name 
        member_count = 1;
        interface_set_id = InterfaceSet+"_"+str(interface_set_index)
        common_config = """
del class-of-service interfaces interface-set {0}
set class-of-service interfaces interface-set {0} output-traffic-control-profile {1}
""".format(interface_set_id,tcp_name)           
        conf_file.write(common_config)
  
# apply TCP to interface set 
        while member_count <= interface_set_members:
            

            unit = VRF_INDEX

# create the interface set 
            common_config = """
set interfaces interface-set {0} interface {1} unit {2}
""".format(interface_set_id,port,unit)    
            conf_file.write(common_config)
            member_count = member_count + 1
            VRF_INDEX = VRF_INDEX + 1      
        interface_set_index = interface_set_index + 1
    
    return interfaces_set_pir

           


def CreateIngressPolicers(conf_file,port,PolicerPIR,Variables):

    VRF_INDEX = Variables['VRF_START']
    VRF_END = Variables['VRF_END']


    while VRF_INDEX <= VRF_END:
        
        unit = VRF_INDEX
# calculate shaper burst rate based on seconds of traffic. 
        burstseconds = 0.01
        burstsize = CalculateBurst(burstseconds,PolicerPIR)
        if "ae" in(port):
            policer_name = "HCOS_IFL_AE_POLICER_{}".format(PolicerPIR.upper())
            conf_file.write("set firewall policer {0} shared-bandwidth-policer".format(policer_name))
        else:
            policer_name = "HCOS_IFL_POLICER_{}".format(PolicerPIR.upper())
        common_config = """
set firewall policer {0} logical-interface-policer 
set firewall policer {0} if-exceeding bandwidth-limit {1}
set firewall policer {0} if-exceeding burst-size-limit {2}
set firewall policer {0} then discard
set interfaces {3} unit {4} layer2-policer input-policer {0}                  
            """.format(policer_name,PolicerPIR,burstsize,port,unit)

        conf_file.write(common_config)

        VRF_INDEX = VRF_INDEX + 1

            



def ConfigGeneration(conf_file,Variables):
    try:
# create generic configuration.         
        CreateHCOS(conf_file,Variables)
    
# Read in the Variables

        CosEnableInterfaces = Variables['class_of_service']['interfaces']
# cycle through each port 
        for port in CosEnableInterfaces:

# check if this has an interface set applied: 
            if CosEnableInterfaces[port]['interface_set'] is not None:
                for InterfaceSet, value in CosEnableInterfaces[port]['interface_set'].items():
                    PolicerPIR = CreateInterfaceSets(conf_file,port,InterfaceSet,Variables)
                    UnitPIR = None
                    CreateIngressPolicers(conf_file,port,PolicerPIR,Variables)
                    CreateCosUnits(conf_file,port,UnitPIR,Variables)
            else:
                PolicerPIR = CosEnableInterfaces[port]['pir']
                UnitPIR = CosEnableInterfaces[port]['pir']
                CreateCosUnits(conf_file,port,UnitPIR,Variables)
                CreateIngressPolicers(conf_file,port,PolicerPIR,Variables)
    except:
        pass








    

if __name__ == "__main__":
    ConfigGeneration()




