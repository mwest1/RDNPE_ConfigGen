#!/usr/bin/env python3

import yaml
import sys
import random
from datetime import datetime
import re

def esiGen(vlan_list,MAC):
    ESI_padding = "00:00"
    # find lowest value in vlan_list
    VLAN = min(vlan_list)
    # Pad vlan to 4 digits using zfill
    VLAN = str(VLAN).zfill(4)
    esi = ESI_padding+":"+VLAN[0:2]+":"+VLAN[2:]+":"+MAC
    return esi




def ReadYamlVars(yaml_file):

    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)





# def CreatePhysicalInterface(conf_file,Variables):

#     Interfaces = Variables['interfaces']

#     for port,parameters in Interfaces.items():

            
#         description = parameters['description']
#         if parameters.get('bundle'):
#             ae = parameters['bundle']
#             common_config = """
# delete interfaces {0}
# set interfaces {0} description "{1}"
# set interfaces {0} gigether-options 802.3ad {2}
#         """.format(port,description,ae)
#             conf_file.write(common_config)

# # If IRB interface do not configure any IFD level settings
# # configure bundle specific configuraiton
#         elif "irb" in port:
#             common_config = """
# delete interfaces irb
#         """
#             conf_file.write(common_config)

#         else:
#             mtu = parameters['mtu']
#             common_config = """
# delete interfaces {0}
# set interfaces {0} description "{1}"
# set interfaces {0} mtu {2}
# set interfaces {0} hierarchical-scheduler
# set interfaces {0} encapsulation flexible-ethernet-services flexible-vlan-tagging
#         """.format(port,description,mtu)
#             conf_file.write(common_config)
# # if single active then do NOT configure LACP
#         if "ae" in port:
#             if parameters.get('single_active'):
#             # then do not configure LACP i.e do nothing
#                 pass
#             else: 
#             # configure LACP with system id aligned to the MAC address
#                 id = parameters['system_id']
#                 common_config = """
# set interfaces {0} aggregated-ether-options lacp active periodic fast
# set interfaces {0} aggregated-ether-options lacp system-id {1}
#             """.format(port,id)
#                 conf_file.write(common_config)
        
#             if parameters.get('epl_pwht'):
#                 id = parameters['system_id']
#                 common_config = """
# set interfaces {0} encapsulation ethernet-ccc 
#             """.format(port)
#                 conf_file.write(common_config)                
#             else:
#                 pass
#         else:
#             pass


# def CreateServiceInterface(conf_file,Variables):
    
#     Interfaces = Variables['interfaces']
#     # 
#     for port,parameters in Interfaces.items():
#         if parameters.get('unit'):
#             units = parameters['unit']
#             for unit,parameters in units.items():
#     # initialize common config
#                 common_config = """\n"""
#                 description = parameters['description']
#                 local_config = """
# set interfaces {0} unit {1} description "{2}"
#                 """.format(port,unit,description)
#                 common_config = common_config + local_config 
#                 if parameters.get('interface_mode'):
#                     mode = parameters['interface_mode']
#                     local_config = """
# set interfaces {0} unit {1} family bridge interface-mode {2}
#                 """.format(port,unit,mode)
#                 common_config = common_config + local_config 
#                 if parameters.get('vlan_list'):
#                     vlan_list = parameters['vlan_list']
#                     for vlan in vlan_list:                      
#                         local_config = """
# set interfaces {0} unit {1} family bridge vlan-id-list {2}
#                     """.format(port,unit,vlan)
#                         common_config = common_config + local_config 
#                 if parameters.get('vlan_translate'):
#                     vlan_map = parameters['vlan_translate']
#                     for from_vlan,to_vlan in vlan_map.items():                      
#                         local_config = """
# set interfaces {0} unit {1} family bridge vlan-rewrite translate {2} {3}
#                     """.format(port,unit,from_vlan,to_vlan)
#                         common_config = common_config + local_config 
#                 if parameters.get('routing_instance'):
#                     routing_instance = parameters['routing_instance']
#                     local_config = """
# set routing-instances {0} interface {1}.{2}
#                 """.format(routing_instance,port,unit)
#                     common_config = common_config + local_config 
#                 if parameters.get('ipv4_addr'):
#                     inet = parameters['ipv4_addr']
#                     local_config = """
# set interfaces {0} unit {1} family inet address {2} 
#                     """.format(port,unit,inet)
#                     common_config = common_config + local_config 
#                 if parameters.get('vgav4_addr'):
#                     vgav4 = parameters['vgav4_addr']
#                     local_config = """
# set interfaces {0} unit {1} family inet address {2} virtual-gateway-address {3}
# set interfaces {0} unit {1} virtual-gateway-v4-mac 00:00:5e:00:01:01
# set interfaces {0} unit {1} virtual-gateway-accept-data
#                     """.format(port,unit,inet,vgav4)
#                     common_config = common_config + local_config 
    
#                 if parameters.get('ipv6_addr'):
#                     inet6 = parameters['ipv6_addr']
#                     local_config = """
# set interfaces {0} unit {1} family inet6 address {2} 
#                     """.format(port,unit,inet6)
#                     common_config = common_config + local_config
                
#                 if parameters.get('vgav6_addr'):
#                     vgav6 = parameters['vgav6_addr']
#                     local_config = """
# set interfaces {0} unit {1} family inet address {2} virtual-gateway-address {3}
# set interfaces {0} unit {1} virtual-gateway-v6-mac 00:00:5e:00:02:01
#                     """.format(port,unit,inet,vgav6)
#                     common_config = common_config + local_config 
#                 if Interfaces[port].get('multi_homed'):
#                     if Interfaces[port].get('esi_mac'):
#                         esi_mac = Interfaces[port]['esi_mac']
#                         vlan_list = parameters['vlan_list']
#                         esi = esiGen(vlan_list,esi_mac)
#         # if single_active set to True, configure as A/S
#                         if Interfaces[port].get('single_active'):
#                             local_config = """
# set interfaces {0} unit {1} esi {2}
# set interfaces {0} unit {1} esi single-active
#                         """.format(port,unit,esi)
#                         else: 
#                             local_config = """
# set interfaces {0} unit {1} esi {2}
# set interfaces {0} unit {1} esi all-active
#                         """.format(port,unit,esi)
#                     common_config = common_config + local_config 
#     # configure ESI value, first need to calculate the 
#     # write unit configuration to the configuration file. 
#                 conf_file.write(common_config)
                    

                

def CreateEvpnSecurity(conf_file,Variables):
    
    common_config = """
del groups EVPN_FLOOD_FILTER
set groups EVPN_FLOOD_FILTER routing-instances <*> bridge-domains <*> forwarding-options flood input EVPN_FLOOD_FILTER

set firewall family bridge filter EVPN_FLOOD_FILTER term BROADCAST from traffic-type broadcast
set firewall family bridge filter EVPN_FLOOD_FILTER term BROADCAST then policer POLICER_2M
set firewall family bridge filter EVPN_FLOOD_FILTER term MULTICAST from traffic-type multicast
set firewall family bridge filter EVPN_FLOOD_FILTER term MULTICAST then policer POLICER_2M
set firewall family bridge filter EVPN_FLOOD_FILTER term UNKNOWN_UNICAST from traffic-type unknown-unicast
set firewall family bridge filter EVPN_FLOOD_FILTER term UNKNOWN_UNICAST then policer POLICER_2M
set firewall family bridge filter EVPN_FLOOD_FILTER term OTHERS then accept

set firewall policer POLICER_2M if-exceeding bandwidth-limit 2m
set firewall policer POLICER_2M if-exceeding burst-size-limit 200k
set firewall policer POLICER_2M then discard

del groups EVPN_PARAMETERS_SPECIFIC
set groups EVPN_PARAMETERS_SPECIFIC routing-instances <*> protocols evpn duplicate-mac-detection detection-threshold 5
set groups EVPN_PARAMETERS_SPECIFIC routing-instances <*> protocols evpn duplicate-mac-detection detection-window 180
set groups EVPN_PARAMETERS_SPECIFIC routing-instances <*> protocols evpn duplicate-mac-detection auto-recovery-time 5
set groups EVPN_PARAMETERS_SPECIFIC routing-instances <*> protocols evpn designated-forwarder-election-hold-time 5

del groups EVPN_PARAMETERS_GENERIC
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options mac-table-size 500
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options mac-table-size packet-action drop
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options mac-ip-table-size 500
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options interface-mac-limit 250
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options interface-mac-limit packet-action drop
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options interface-mac-ip-limit 250
set groups EVPN_PARAMETERS_GENERIC routing-instances <*> bridge-domains <*> bridge-options mac-statistics
            """
    conf_file.write(common_config)
        


def CreateEvpnInstance(conf_file,Variables):
    
    RoutingInstances = Variables['routing_instances']
    common_config = """\n"""
    for instance,parameters in RoutingInstances.items():
        description = parameters['description']
        ri_type = parameters['instance_type']
        rt = parameters['rt']
        rd = parameters['rd']
# create EVPN VPWS
        if ri_type == "evpn-vpws":
            vpws = parameters['interface']

            local_config = """
del routing-instances {0}
set routing-instances {0} description "{1}"
set routing-instances {0} instance-type {2}
set routing-instances {0} vrf-target {3}
set routing-instances {0} route-distinguisher {4}
        """.format(instance,description,ri_type,rt,rd)
            common_config = common_config + local_config

            for interface,service_ids in vpws.items():
                local = service_ids['local_service']
                remote = service_ids['remote_service']
                local_config = """
set routing-instances {0} protocols evpn interface {1} vpws-service-id local {2}
set routing-instances {0} protocols evpn interface {1} vpws-service-id remote {3}                
        """.format(instance,interface,local,remote)
                common_config = common_config + local_config



        
        
        
        
        if ri_type == "virtual-switch":
            local_config = """
del routing-instances {0}
set routing-instances {0} description "{1}"
set routing-instances {0} instance-type {2}
set routing-instances {0} vrf-target {3}
set routing-instances {0} route-distinguisher {4}
set routing-instances {0} protocols evpn default-gateway no-gateway-community
set routing-instances {0} apply-groups EVPN_FLOOD_FILTER
set routing-instances {0} apply-groups EVPN_PARAMETERS_GENERIC
set routing-instances {0} apply-groups EVPN_PARAMETERS_SPECIFIC
        """.format(instance,description,ri_type,rt,rd)
            common_config = common_config + local_config
            if parameters.get('l2_stretch_vlan_list'):
                vlan_list = parameters['l2_stretch_vlan_list']
                for vlan in vlan_list:
                    local_config = """
set routing-instances {0} protocols evpn extended-vlan-list {1}
set routing-instances {0} bridge-domains {0} vlan-id-list {1}
        """.format(instance,vlan)
                    common_config = common_config + local_config 
            if parameters.get('bridge_domains'):
                bridge_domains = parameters['bridge_domains']
                for bd,parameters in bridge_domains.items():
                    description = parameters['description']
                    VLAN = parameters['VLAN']
                    local_config = """
set routing-instances {0} bridge-domains {1} description "{2}"
set routing-instances {0} bridge-domains {1} vlan-id {3}
set routing-instances {0} protocols evpn extended-vlan-list {3}
        """.format(instance,bd,description,VLAN)
                    common_config = common_config + local_config
                    if parameters.get('IRB'):
                        local_config = """
set routing-instances {0} bridge-domains {1} routing-interface irb.{2}
        """.format(instance,bd,VLAN)
                        common_config = common_config + local_config
    # configure ESI value, first need to calculate the 
    # write unit configuration to the configuration file.    

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

        CreateEvpnSecurity(conf_file,Variables)
        CreateEvpnInstance(conf_file,Variables)
        # CreatePhysicalInterface(conf_file,Variables)
        # CreateServiceInterface(conf_file,Variables)
        
        

        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




