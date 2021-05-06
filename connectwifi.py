"""
AISEL-DroneLab: Search for a specific wifi ssid and connect to it.
@author mrammens
"""
import os
import time

class WifiFinder:
    def __init__(self, *args, **kwargs):
        print(args,kwargs)
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        #self.interface_to_gateway = kwargs['interface_to_gateway']
        self.main_dict = {}
        self.timer=0
    
    def get_ssid_list(self,command):

        while True:
            result = os.popen(command.format())
            result_list = list(result)
            print(result,result_list)

            if "Device or resource busy" in result or len(result_list)==0:
                print("Retrying in 2 seconds",self.timer)
                self.timer=self.timer+1
                time.sleep(4)
            else:
                break

            if self.timer>5:
                result = None
                result_list = None
                break
            
        return result,result_list


    def connect(self):


        command = """sudo iw dev wlan0 scan ap-force | grep -ioE 'ssid:.*'"""
        print(command)

        result, result_list = self.get_ssid_list(command)
        print(result)
        print(result_list)
        if not result:
                return None
        else:
            self.ssid_list = [item.lstrip('SSID:').strip('"\n').strip() for item in result_list]
            print("Successfully got ssids {}".format(str(self.ssid_list)))

        if not self.server_name in self.ssid_list:
            print(self.server_name, "not in list of found SSIDs... retunring")
            return None


        cmd_selectwifi = "wpa_cli -i{} select_network 1 ".format(self.interface_name)        
        result_select = os.popen(cmd_selectwifi)

        #cmd_selectwifi_gateway = "wpa_cli -i{} select_network 0 ".format(self.interface_to_gateway)        
        #result_select = os.popen(cmd_selectwifi_gateway)
        try:
                result = self.connection(self.server_name)
        except Exception as exp:
                print("Couldn't connect to name : {}. {}".format(self.server_name, exp))
        else:
              if result:
                    print("Successfully connected to {}".format(self.server_name))
                    return 1

    def connection(self, name):
        try:
            os.system("wpa_cli -i{} select_network 0 ".format(self.interface_name))
        except:## this doesping  not really catch an error
            raise
        else:
            return True

    #def protect_gateway_interface(self):
    #    try:
    #        os.system("wpa_cli -i{} select_network 0 ".format(self.interface_to_gateway))
    #    except:## this does not really catch an error
    #        raise
    #    else:
    #        return True
     

if __name__ == "__main__":
    # Server_name is a case insensitive string, and/or regex pattern which demonstrates
    # the name of targeted WIFI device or a unique part of it.
    server_name = "TELLO-588A0C"
    password = ""
    interface_name = "wlan0" # i. e wlp2s0 
    #interface_to_gateway = "wlan1" ## if raspberry is connected via wlan to backend/gateway
    F = WifiFinder(server_name=server_name,
                    password=password,
                    interface=interface_name#,
    #               interface_to_gateway=interface_to_gateway
               )
    #F.protect_gateway_interface()
    F.connect()

