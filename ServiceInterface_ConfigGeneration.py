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


def esiGen(vlan_list,MAC):
    ESI_padding = "00:00"
    # find lowest value in vlan_list, first create an empty list
    vlans = []
    # create a numberical list when ranges are specified
    
    if type(vlan_list) == list:
        for vlan in vlan_list:
        # if type string split based on the '-' and use the first number
            if type(vlan) == str:
                vlan_id = int(vlan.split('-')[0])
            else:
                vlan_id = vlan
    else:
        vlan_id = vlan_list
    
    vlans.append(vlan_id)
   
    VLAN = min(vlans)
    # Pad vlan to 4 digits using zfill
    VLAN = str(VLAN).zfill(4)
    esi = ESI_padding+":"+VLAN[0:2]+":"+VLAN[2:]+":"+MAC
    return esi


# def CreateInterfaces(conf_file,Variables):
    

#     Interfaces = Variables['interfaces']

#     for port,parameters in Interfaces.items():
#         description= parameters['description']
#         mtu = parameters['mtu']
#         common_config = """
# delete interfaces {0}
# set interfaces {0} description "{1}"
# set interfaces {0} mtu {2}
# set interfaces {0} hierarchical-scheduler
# set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
#         """.format(port,description,mtu)
#         conf_file.write(common_config)
# # create interface units
#         units = parameters['unit']
#         for unit,parameters in units.items():
#             description = parameters['description']
#             vlan_id = parameters['vlan_id']
#             ipv4_addr = parameters['ipv4_addr']
#             routing_instance = parameters['routing_instance']
# # create common unit parameters
#             common_config = """
# set interfaces {0} unit {1} description "{2}"
# set interfaces {0} unit {1} vlan-id {3}
# set interfaces {0} unit {1} family inet address {4}
# set routing-instances {5} interface {0}.{1}
#         """.format(port,unit,description,vlan_id,ipv4_addr,routing_instance)
            
#             conf_file.write(common_config)


def CreatePhysicalInterface(conf_file,Variables):
    
    Interfaces = Variables['interfaces']

    for port,parameters in Interfaces.items():


        description = parameters['description']
        if parameters.get('bundle'):
            ae = parameters['bundle']
            common_config = """
delete interfaces {0}
set interfaces {0} description "{1}"
set interfaces {0} gigether-options 802.3ad {2}
        """.format(port,description,ae)
            conf_file.write(common_config)

# If IRB interface do not configure any IFD level settings
# configure bundle specific configuraiton
        elif "irb" in port:
            common_config = """
delete interfaces irb
        """
            conf_file.write(common_config)

        else:
            mtu = parameters['mtu']
            common_config = """
set interfaces {0} description "{1}"
set interfaces {0} mtu {2}
set interfaces {0} hierarchical-scheduler
set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
        """.format(port,description,mtu)
            conf_file.write(common_config)
# if single active then do NOT configure LACP
        if "ae" in port:
            if parameters.get('single_active'):
            # then do not configure LACP i.e do nothing
                pass
            elif parameters.get('system_id'): 
            # configure LACP with system id aligned to the MAC address
                id = parameters['system_id']
                common_config = """
set interfaces {0} aggregated-ether-options lacp active periodic fast
set interfaces {0} aggregated-ether-options lacp system-id {1}
            """.format(port,id)

            else:
                common_config = """
set interfaces {0} aggregated-ether-options lacp active periodic fast
            """.format(port) 
            
            conf_file.write(common_config)

        if "ps" in port:
            anchor = parameters['anchor']
            
            common_config = """
set chassis pseudowire-service device-count 32
set interfaces {0} flexible-vlan-tagging 
set interfaces {0} anchor-point {1}
set interfaces {1} hierarchical-scheduler implicit-hierarchy
            """.format(port,anchor)
            conf_file.write(common_config)                
        else:
                pass



def CreateServiceUnitsInterface(conf_file,Variables):
    Interfaces = Variables['interfaces']
    for port,parameters in Interfaces.items():

        if parameters.get('unit'):
            units = parameters['unit']
            for unit,parameters in units.items():
    # initialize common config
                common_config = """\n"""
                description = parameters['description']
                local_config = """
set interfaces {0} unit {1} description "{2}"
                """.format(port,unit,description)
                common_config = common_config + local_config
    # If unit is 0 then remove the vlan tagging at the port level
                if unit == 0 and "ps" not in port:
                    local_config = """
del interfaces {0} flexible-vlan-tagging
del interfaces {0} encapsulation flexible-ethernet-services
                """.format(port)
                    common_config = common_config + local_config  
    # First check if interface is a trunk/access port for L2 access
                if parameters.get('interface_mode'):
                    mode = parameters['interface_mode']
                    local_config = """
set interfaces {0} unit {1} family bridge interface-mode {2}
                """.format(port,unit,mode)
                    common_config = common_config + local_config 
    # apply vlan_list for trunk interfaces
                if parameters.get('vlan_list'):
                    vlan_list = parameters['vlan_list']
                    for vlan in vlan_list:                      
                        local_config = """
set interfaces {0} unit {1} family bridge vlan-id-list {2}
                    """.format(port,unit,vlan)
                        common_config = common_config + local_config 
    # build vlan Translation maps 
                if parameters.get('vlan_translate'):
                    vlan_map = parameters['vlan_translate']
                    for from_vlan,to_vlan in vlan_map.items():                      
                        local_config = """
set interfaces {0} unit {1} family bridge vlan-rewrite translate {2} {3}
                    """.format(port,unit,from_vlan,to_vlan)
                        common_config = common_config + local_config

    # add interface encapsulation
                if parameters.get('encapsulation'):
                    encapsulation = parameters['encapsulation']
                    if unit == 0 and encapsulation == "ethernet-ccc" and "ps" not in port:                
                        local_config = """
set interfaces {0} encapsulation {1}
                    """.format(port,encapsulation)
                    else: 
                        local_config = """
set interfaces {0} unit {1} encapsulation {2}
                    """.format(port,unit,encapsulation)
                    common_config = common_config + local_config


    # Add all interface types to routing instance if apply  
                if parameters.get('routing_instance'):
                    routing_instance = parameters['routing_instance']
                    local_config = """
set routing-instances {0} interface {1}.{2}
                """.format(routing_instance,port,unit)
                    common_config = common_config + local_config 

    # apply vlan_id for L3 sub interface
                if parameters.get('vlan_id'):
                    vlan_id= parameters['vlan_id']
                    local_config = """
set interfaces {0} unit {1} vlan-id {2}
                """.format(port,unit,vlan_id)
                    common_config = common_config + local_config 

    # apply IP adddressing, V4/V6/VGW



                if parameters.get('ipv4_addr'):
                    inet = parameters['ipv4_addr']
                    local_config = """
set interfaces {0} unit {1} family inet address {2} 
                    """.format(port,unit,inet)
                    common_config = common_config + local_config 
                if parameters.get('vgav4_addr'):
                    vgav4 = parameters['vgav4_addr']
                    local_config = """
set interfaces {0} unit {1} family inet address {2} virtual-gateway-address {3}
set interfaces {0} unit {1} virtual-gateway-v4-mac 00:00:5e:00:01:01
set interfaces {0} unit {1} virtual-gateway-accept-data
                    """.format(port,unit,inet,vgav4)
                    common_config = common_config + local_config 
    
                if parameters.get('ipv6_addr'):
                    inet6 = parameters['ipv6_addr']
                    local_config = """
set interfaces {0} unit {1} family inet6 address {2} 
                    """.format(port,unit,inet6)
                    common_config = common_config + local_config
                
                if parameters.get('vgav6_addr'):
                    vgav6 = parameters['vgav6_addr']
                    local_config = """
set interfaces {0} unit {1} family inet address {2} virtual-gateway-address {3}
set interfaces {0} unit {1} virtual-gateway-v6-mac 00:00:5e:00:02:01
                    """.format(port,unit,inet,vgav6)
                    common_config = common_config + local_config
                
                
                if parameters.get('ipv4_addr') or parameters.get('ipv6_addr'):
                    pass

                elif Interfaces[port].get('multi_homed'):
                        if Interfaces[port].get('esi_mac'):
                            esi_mac = Interfaces[port]['esi_mac']
                            if parameters.get('vlan_list'):
                                vlan_list = parameters['vlan_list']
                            else: 
                                vlan_list = "0"
                            esi = esiGen(vlan_list,esi_mac)
            # if single_active set to True, configure as A/S
                            if Interfaces[port].get('single_active'):
                                local_config = """
set interfaces {0} unit {1} esi {2}
set interfaces {0} unit {1} esi single-active
                        """.format(port,unit,esi)
                            else: 
                                local_config = """
set interfaces {0} unit {1} esi {2}
set interfaces {0} unit {1} esi all-active
                        """.format(port,unit,esi)
                            common_config = common_config + local_config

                        if Interfaces[port].get('esi_preference'):
                            pref = Interfaces[port]['esi_preference']
                            local_config = """
set interfaces {0} unit {1} esi df-election-type preference value {2}
                        """.format(port,unit,pref)
                            common_config = common_config + local_config 

        # configure ESI value, first need to calculate the 
        # write unit configuration to the configuration file.
        #    
                conf_file.write(common_config)

def TrunkUnits(vlan_list):
    #create an empty list to store all the trunk VLANS. 
    TrunkVLANs = []
    for vlan_range in vlan_list:
        if type(vlan_range) == str:
                range_min = int(vlan_range.split("-")[0])
                range_max = int(vlan_range.split("-")[1])
                vlan = range_min
                while vlan <= range_max:
                    TrunkVLANs.append(vlan)
                    vlan = vlan + 1
        else:
                TrunkVLANs.append(vlan_range)
    TrunkVLANs.sort()

    return TrunkVLANs



def CreateTrunkUnitsInterface(conf_file,Variables):
    Interfaces = Variables['interfaces']
    common_config = """\n"""
    for port,parameters in Interfaces.items():

        if parameters.get('vlan_list'):
            vlan_list = parameters['vlan_list']
            TrunkVLANs = TrunkUnits(vlan_list)

            for vlan in TrunkVLANs:
                common_config = """\n"""                                       
                local_config = """
set interfaces {0} unit {1} family bridge interface-mode trunk
set interfaces {0} unit {1} family bridge vlan-id-list {1}
                    """.format(port,vlan)
                common_config = common_config + local_config
    # Add all interface types to routing instance if apply  
                if parameters.get('routing_instance'):
                    routing_instance = parameters['routing_instance']
                    local_config = """
set routing-instances {0} interface {1}.{2}
                """.format(routing_instance,port,vlan)
                    common_config = common_config + local_config 

                if Interfaces[port].get('multi_homed'):
                        if Interfaces[port].get('esi_mac'):
                            esi_mac = Interfaces[port]['esi_mac']
                            esi = esiGen(vlan,esi_mac)
            # if single_active set to True, configure as A/S
                            if Interfaces[port].get('single_active'):
                                local_config = """
set interfaces {0} unit {1} esi {2}
set interfaces {0} unit {1} esi single-active
                        """.format(port,vlan,esi)
                            else: 
                                local_config = """
set interfaces {0} unit {1} esi {2}
set interfaces {0} unit {1} esi all-active
                        """.format(port,vlan,esi)
                            common_config = common_config + local_config

                        if Interfaces[port].get('esi_preference'):
                            pref = Interfaces[port]['esi_preference']
                            local_config = """
set interfaces {0} unit {1} esi df-election-type preference value {2}
                        """.format(port,vlan,pref)
                            common_config = common_config + local_config 

        # configure ESI value, first need to calculate the 
        # write unit configuration to the configuration file.
                conf_file.write(common_config)


def ConfigGeneration(conf_file, Variables):
    #QoS_Inventory = Inventory['QoSTesting']
    # for hostname in Inventory:
    #     RouterVars = "{}.yml".format(hostname)
    #     ConfFile = "Configs/{}.set".format(hostname)    
        # try:
        #     conf_file = open(ConfFile,"a+")
        # except:
        #     print("unable to create new configuration file!")
        #     sys.exit(0)
    
# Read in the Variables 
        #Variables = ReadYamlVars(RouterVars)
        CreatePhysicalInterface(conf_file,Variables)
        CreateServiceUnitsInterface(conf_file,Variables)
        CreateTrunkUnitsInterface(conf_file,Variables)

if __name__ == "__main__":
    ConfigGeneration()




