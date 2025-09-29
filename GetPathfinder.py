#!/usr/bin/env python3

import urllib.request
import urllib.parse
import yaml



def FetchData(url):
    try: 
        with open(yaml_file,"r") as yaml_file:
            try:
                Inventory = yaml.safe_load(yaml_file)
        
            except yaml.YAMLError:
                print("Unable to load file {0}.Please check file for host exists.".format(yaml_file))
                sys.exit(0)
            #print(parsed_yaml)
            return Inventory
            
    except:
        print("Unable to open file {0}. Please check yaml file for host exists.".format(yaml_file))
        sys.exit(0)


def main():
    
    # get the inventory file
    yaml_file = (input("Enter Base inventory (default Tunnel.yml):") or "Tunnel.yml")
    
    Inventory = GetInventory(yaml_file)

    # Create the SSH tunnel for each host in the inventory 
    for hostname,paramaters in Inventory.items():
        SSHTunnel(hostname,paramaters)
    
    print("Script complete. The list of SSH processes is shown below")
    SSHProcesses = os.system('ps -ef | grep ssh')
    print(SSHProcesses)
    
main()

