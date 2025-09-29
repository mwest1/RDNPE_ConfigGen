#!/usr/bin/env python3

import yaml
import sys




def ReadYamlVars(yaml_file):
    with open(yaml_file,"r") as yaml_file:
            try:
                parsed_yaml = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
    return(parsed_yaml)


def CreateVRF(conf_file,Variables):
    RoutingInstances = Variables['routing_instances']
    if RoutingInstances is not None: 
        for instance,parameters in RoutingInstances.items():
            description = parameters['description']
            ri_type = parameters['instance_type']
            rt = parameters['rt']
            rd = parameters['rd']
            if ri_type == "vrf":
                common_config = """
del routing-instances {0}
set routing-instances {0} instance-type vrf
set routing-instances {0} routing-options maximum-prefixes 10000
set routing-instances {0} routing-options maximum-prefixes threshold 80
set routing-instances {0} routing-options auto-export
set routing-instances {0} description "{1}"
set routing-instances {0} route-distinguisher {2}
set routing-instances {0} vrf-target {3}
set routing-instances {0} vrf-table-label
set routing-instances {0} no-vrf-propagate-ttl
        """.format(instance,description,rd,rt)
                conf_file.write(common_config)
            if parameters.get('vrf_import'):
                common_config = ""
                for policy in parameters.get('vrf_import'):
                        common_config = common_config +  """
set routing-instances {0} vrf-import {1} 
                        """.form(instance,policy)
                conf_file.write(common_config)
            if parameters.get('vrf_export'):
                common_config = ""
                for policy in parameters.get('vrf_export'):
                        common_config = common_config +  """
set routing-instances {0} vrf-export {1} 
                        """.form(instance,policy)
                        conf_file.write(common_config)
        # add VRF routing protocols 
            if parameters.get('protocols'):
                for protocol, attributes in parameters['protocols'].items():
                    if protocol == "static":
                        common_config = """
    """
                        for prefix, next_hop in attributes.items():
                            for gw in next_hop:
                                common_config = common_config + """
set routing-instances {0} routing-options static route {1} next-hop {2}
""".format(instance,prefix,gw)
                conf_file.write(common_config)
                if protocol == "bgp":
                    common_config = """
"""
                    for group, parameters in attributes['group'].items():
                        peer_as = parameters['peer_as']
                        import_policy = parameters['import_policy']
                        export_policy = parameters['export_policy']
                        bfd = parameters['bfd']
                        neighbor = parameters['neighbor']
                        common_config = common_config + """
set routing-instances {0} protocols bgp group {1} peer-as {2}
""".format(instance,group,peer_as)
                        if bfd:
                            common_config = common_config + """
set routing-instances {0} protocols bgp group {1} apply-groups SET_BFD_TIMERS_PE_CE_300
""".format(instance,group)
                        if import_policy: 
                            for policy in import_policy:
                                common_config = common_config + """
set routing-instances {0} protocols bgp group {1} import {2}
    """.format(instance,group,policy)
                        if export_policy: 
                            for policy in export_policy:
                                common_config = common_config + """
set routing-instances {0} protocols bgp group {1} import {2}
""".format(instance,group,policy)
                        for neighbor,parameters in neighbor.items():
                            description = parameters['description']
                            common_config = common_config + """
set routing-instances {0} protocols bgp group {1} neighbor {2} description "{3}"
""".format(instance,group,neighbor,description)

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
    
        CreateVRF(conf_file,Variables)
        conf_file.close()


    

if __name__ == "__main__":
    ConfigGeneration()




