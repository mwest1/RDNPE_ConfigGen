#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re
import ServiceInterface_ConfigGeneration



def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)

def CalculateBurst(burstseconds,rate):
    
    exponent = (re.split('[0-9]',rate)[-1]).lower()
    rate = int(re.split('[a-zA-Z]',rate)[0])

    if exponent == "k":
        multiplier = 1000
    elif exponent == "m": 
        multiplier = 1000000
    elif exponent == "g":
        multiplier = 1000000000
    burstsize = int((rate*multiplier*burstseconds)/8)

    return burstsize

def CreateInterfaces(conf_file,Variables):
    

    Interfaces = Variables['interfaces']

    for port,parameters in Interfaces.items():
        description= parameters['description']
        mtu = parameters['mtu']
        common_config = """
delete interfaces {0}
set interfaces {0} description "{1}"
set interfaces {0} mtu {2}
set interfaces {0} hierarchical-scheduler
set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
        """.format(port,description,mtu)
        conf_file.write(common_config)
# create interface units
        units = parameters['unit']
        for unit,parameters in units.items():
            description = parameters['description']
            vlan_id = parameters['vlan_id']
            ipv4_addr = parameters['ipv4_addr']
            routing_instance = parameters['routing_instance']
# create common unit parameters
            common_config = """
set interfaces {0} unit {1} description "{2}"
set interfaces {0} unit {1} vlan-id {3}
set interfaces {0} unit {1} family inet address {4}
set routing-instances {5} interface {0}.{1}
        """.format(port,unit,description,vlan_id,ipv4_addr,routing_instance)
            
            conf_file.write(common_config)
            

def CreateHCOS(conf_file,Variables):
    


    common_config = """
delete class-of-service schedulers HCOS_FC0_6Q_SCHED
delete class-of-service schedulers HCOS_FC1_6Q_SCHED
delete class-of-service schedulers HCOS_FC2_6Q_SCHED
delete class-of-service schedulers HCOS_FC3_6Q_SCHED
delete class-of-service schedulers HCOS_FC4_6Q_SCHED
delete class-of-service schedulers HCOS_FC5_6Q_SCHED

set class-of-service schedulers HCOS_FC0_6Q_SCHED transmit-rate percent 5
set class-of-service schedulers HCOS_FC0_6Q_SCHED buffer-size percent 30
set class-of-service schedulers HCOS_FC0_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC1_6Q_SCHED transmit-rate percent 10
set class-of-service schedulers HCOS_FC1_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC1_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC2_6Q_SCHED transmit-rate percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC2_6Q_SCHED priority low

set class-of-service schedulers HCOS_FC3_6Q_SCHED transmit-rate percent 20
set class-of-service schedulers HCOS_FC3_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC3_6Q_SCHED priority low
set class-of-service schedulers HCOS_FC4_6Q_SCHED transmit-rate percent 30
set class-of-service schedulers HCOS_FC4_6Q_SCHED buffer-size percent 15
set class-of-service schedulers HCOS_FC4_6Q_SCHED priority medium-low
 

set class-of-service schedulers HCOS_FC5_6Q_SCHED transmit-rate percent 20
set class-of-service schedulers HCOS_FC5_6Q_SCHED buffer-size percent 5
set class-of-service schedulers HCOS_FC5_6Q_SCHED priority high
 
del class-of-service scheduler-maps HCOS_6Q_SCHEDULER

set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC0 scheduler HCOS_FC0_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC1 scheduler HCOS_FC1_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC2 scheduler HCOS_FC2_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC3 scheduler HCOS_FC3_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC4 scheduler HCOS_FC4_6Q_SCHED
set class-of-service scheduler-maps HCOS_6Q_SCHEDULER forwarding-class FC5 scheduler HCOS_FC5_6Q_SCHED

set class-of-service schedulers PE_CE_FC0_6Q_SCHED transmit-rate percent 5
set class-of-service schedulers PE_CE_FC0_6Q_SCHED buffer-size percent 25
set class-of-service schedulers PE_CE_FC0_6Q_SCHED priority low
set class-of-service schedulers PE_CE_FC1_6Q_SCHED transmit-rate percent 10
set class-of-service schedulers PE_CE_FC1_6Q_SCHED buffer-size percent 15
set class-of-service schedulers PE_CE_FC1_6Q_SCHED priority low
set class-of-service schedulers PE_CE_FC2_6Q_SCHED transmit-rate percent 15
set class-of-service schedulers PE_CE_FC2_6Q_SCHED buffer-size percent 15
set class-of-service schedulers PE_CE_FC2_6Q_SCHED priority low
set class-of-service schedulers PE_CE_FC3_6Q_SCHED transmit-rate percent 30
set class-of-service schedulers PE_CE_FC3_6Q_SCHED buffer-size percent 15
set class-of-service schedulers PE_CE_FC3_6Q_SCHED priority low
set class-of-service schedulers PE_CE_FC4_6Q_SCHED transmit-rate percent 40
set class-of-service schedulers PE_CE_FC4_6Q_SCHED buffer-size percent 15
set class-of-service schedulers PE_CE_FC4_6Q_SCHED priority medium-low
set class-of-service schedulers PE_CE_FC5_6Q_SCHED buffer-size percent 15
set class-of-service schedulers PE_CE_FC5_6Q_SCHED priority strict-high
set class-of-service schedulers PE_CE_FC5_6Q_SCHED drop-profile-map loss-priority high protocol any drop-profile PE_CE_FC5_HIGH_PROFILE

        """
            
    conf_file.write(common_config)

# create interface_sets and associated TCP
    interface_sets = Variables['class_of_service']['interface_set']
    for interface_set,parameters in interface_sets.items():
        cir = parameters['cir']
        pir = parameters['pir']
        tcp_name = "HCOS_GRP_SHAPER_BURST10_{}".format(cir)
        common_config = """
del class-of-service traffic-control-profiles {0}
""".format(tcp_name)
        conf_file.write(common_config)
# calculate shaper burst rate based on seconds of traffic. 
        burstseconds = 0.01
        if pir is not None:
            burstsize = CalculateBurst(burstseconds,pir)
            common_config = """
set class-of-service traffic-control-profiles {2} shaping-rate {0}
set class-of-service traffic-control-profiles {2} shaping-rate burst-size {1}
""".format(pir,burstsize,tcp_name)
            
            conf_file.write(common_config)            
# define CIR and burst size
        if cir is not None:
            burstsize = CalculateBurst(burstseconds,cir)
            common_config = """
set class-of-service traffic-control-profiles {2} guaranteed-rate {0}
set class-of-service traffic-control-profiles {2} guaranteed-rate burst-size {1}
""".format(cir,burstsize,tcp_name)

            conf_file.write(common_config)

# apply TCP to interface set 
        common_config = """
del class-of-service interfaces interface-set {0}
set class-of-service interfaces interface-set {0} output-traffic-control-profile {1}
""".format(interface_set,tcp_name)    
        
        conf_file.write(common_config)       

# temporary for PWHT testing only !!!!!!!!!!!!!!!! 
        common_config = """
delete interfaces interface-set PS0_AE21
delete class-of-service interfaces interface-set PS0_AE21
""".format(interface_set,tcp_name)    
        
        conf_file.write(common_config)       


def CreateCosUnits(conf_file,Variables):      

# now create the unit specific configuration and traffic control profiles
    Interfaces = Variables['interfaces']
    for port,parameters in Interfaces.items():
        if parameters.get('unit'):
            units = parameters['unit']
            for unit,parameters in units.items():
                cir = parameters['cir']
                pir = parameters['pir']
                Queueing = parameters['qos']
                interface_set = parameters['interface_set']
    # calculate shaper burst rate based on seconds of traffic. 
                #burstseconds = 0.01
                burstseconds = 0.004 
                if interface_set is not None:
                    if Queueing == True:
                        tcp_name = "HCOS_SHAPER_BURST10_{}_6Q".format(cir)
                        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))
                        conf_file.write("set class-of-service traffic-control-profiles {0} scheduler-map HCOS_6Q_SCHEDULER".format(tcp_name))
                    else:
                        tcp_name = "HCOS_SHAPER_BURST10_{}".format(cir)
                        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))
                else:
                    if Queueing == True:
                        tcp_name = "ACCESS_SHAPER_{}_6Q".format(pir)
                        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))
                        conf_file.write("set class-of-service traffic-control-profiles {0} scheduler-map PE_CE_6Q_SCHEDULER".format(tcp_name))
                    else:
                        tcp_name = "ACCESS_SHAPER_{}".format(pir)
                        conf_file.write("del class-of-service traffic-control-profiles {0}\n".format(tcp_name))

    # calculate shaper burst rate based on seconds of traffic. 
                if pir is not None:
                    burstsize = CalculateBurst(burstseconds,pir)
                    common_config = """
set class-of-service traffic-control-profiles {2} shaping-rate {0}
set class-of-service traffic-control-profiles {2} shaping-rate burst-size {1}
        """.format(pir,burstsize,tcp_name)
                    
                    conf_file.write(common_config)            
        # define CIR and burst size
                if cir is not None:
                    burstsize = CalculateBurst(burstseconds,cir)
                    common_config = """
set class-of-service traffic-control-profiles {2} guaranteed-rate {0}
set class-of-service traffic-control-profiles {2} guaranteed-rate burst-size {1}
        """.format(cir,burstsize,tcp_name)

                    conf_file.write(common_config)

        # apply TCP to interface, along with inbound classifier and 802.1P rewrite rule. 
                common_config = """
del class-of-service interfaces {0} unit {1}
set class-of-service interfaces {0} unit {1} output-traffic-control-profile {2}
set class-of-service interfaces {0} unit {1} classifiers ieee-802.1 CLASSIFY_CE_PE_DOT1P 
set class-of-service interfaces {0} unit {1} rewrite-rules ieee-802.1 PE_CE_DOT1P_REWRITE
        """.format(port,unit,tcp_name,pir)

                conf_file.write(common_config)         
        # apply interface into interface set
                if interface_set is not None:
                    common_config = """
del interfaces interface-set {0} interface {1} unit {2}   
set interfaces interface-set {0} interface {1} unit {2}      
            """.format(interface_set,port,unit)

                    conf_file.write(common_config)

def CreateIngressPolicers(conf_file, Variables):
    Interfaces = Variables['interfaces']
    for port,parameters in Interfaces.items():
        if parameters.get('unit'):
            units = parameters['unit']
            # get the PIR of the interface set as this will be the policier limit/rate
            for unit,parameters in units.items():
                if parameters.get('interface_set'):
                    interface_set = parameters['interface_set']
                    if interface_set is None:
                        pir = parameters['pir']
                    else: 
                        pir = Variables['class_of_service']['interface_set'][interface_set]['pir']
        # calculate shaper burst rate based on seconds of traffic. 
                    burstseconds = 0.01
                    burstsize = CalculateBurst(burstseconds,pir)
                    if "ae" in(port):
                        policer_name = "HCOS_IFL_AE_POLICER_{}".format(pir.upper())
                        conf_file.write("set firewall policer {0} shared-bandwidth-policer".format(policer_name))
                    else:
                        policer_name = "HCOS_IFL_POLICER_{}".format(pir.upper())
                    common_config = """
set firewall policer {0} logical-interface-policer 
set firewall policer {0} if-exceeding bandwidth-limit {1}
set firewall policer {0} if-exceeding burst-size-limit {2}
set firewall policer {0} then discard
set interfaces {3} unit {4} layer2-policer input-policer {0}                  
                    """.format(policer_name,pir,burstsize,port,unit)

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
        Variables = ReadYamlVars(RouterVars)['SCALE']['HQoS']
# CreateInterfaces function not needed as ServiceInterface function handles this role. 
        ServiceInterface_ConfigGeneration.ConfigGeneration(conf_file,Variables)
        CreateHCOS(conf_file,Variables)
        CreateCosUnits(conf_file,Variables)
        CreateIngressPolicers(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




