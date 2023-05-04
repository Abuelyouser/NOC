

from netmiko import ConnectHandler
import time
import csv
import random
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



# Reading domain username & password from D:\
with open(r'D:\Password.txt', mode='r') as up:

        lu=up.readline()
        lp=up.readline()
Username = lu.replace('\n','')

Password = lp.replace('\n','')

def Netmiko_NOKIA(Cabinet_IP,Username,Password):
    # creating a dictionary for the device to connect to
    try:
        device = {
        'device_type': 'autodetect',
        'host': Cabinet_IP,
        'username': Username,
        'password': Password ,
        'port': 22,  # optional, default 22
        'fast_cli': False,

        }

    ###################################### Connecting to the device and returning an ssh connection object ############
        connection = ConnectHandler(**device)
        print("Login Success with Domain UN&PW !")
        return connection
    
    except :

        device1 = {
        'device_type': 'autodetect',
        'host': Cabinet_IP,
        'username': 'isadmin',
        'password': 'ANS#150' ,
        'port': 22,  # optional, default 22
        'fast_cli': False,
        }
        connection = ConnectHandler(**device1)
        print("Login Success with isadmin !")
        return connection

####################################################################################################################################


def NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection):

     #connection.write_channel("configure xdsl line 1/1/"+Card_Port+"\r" )
     #time.sleep(1)
     #connection.write_channel("transfer-mode ptm"+"\r"+"spectrum-profile 4"+"\r"+"auto-switch"+"\r"+"exit\r"+"exit\r"+"exit\r" )
     #time.sleep(1)
     connection.write_channel("configure bridge no port 1/1/"+Card_Port+"\r"+"exit\r"+"exit\r" )
     time.sleep(1)
     connection.write_channel("configure atm no pvc  1/1/"+Card_Port+"\r" )
     time.sleep(1)
     connection.write_channel("configure atm pvc  1/1/"+Card_Port+ " aal5-encap-type llc-snap"+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan) +" mode cross-connect""\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan)+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan) +" pppoe-relay-tag true"+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port 1/1/"+Card_Port+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+" vlan-id stacked:"+outer_vlan+":"+ str(inner_vlan)+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+" vlan-id " +str(inner_vlan)+" no tag l2fwder-vlan stacked:"+outer_vlan+":"+ str(inner_vlan)+ " vlan-scope local no qos no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid"+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+" pvid " +str(inner_vlan) +"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+" max-unicast-mac 2 "+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+" vlan-id "+str(inner_vlan)+" l2fwder-vlan stacked:"+outer_vlan+":"+ str(inner_vlan)+" vlan-scope local"+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan)+" circuit-id-pppoe physical-id remote-id-pppoe customer-id"+"\r" )
     time.sleep(1)
     connection.write_channel("configure xdsl line 1/1/"+Card_Port+"\r" )
     time.sleep(1)
     connection.write_channel("no admin-up"+"\r" )
     time.sleep(1)
     connection.write_channel("admin-up"+"\r" )
     time.sleep(1)

     print('Closing connection')
     connection.disconnect()
     

def NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection): 
     #connection.write_channel("configure xdsl line 1/1/"+Card_Port+"\r" )
     #time.sleep(1)
     #connection.write_channel("transfer-mode atm"+"\r"+"spectrum-profile 1"+"\r"+"auto-switch"+"\r"+"exit\r"+"exit\r"+"exit\r" )
     #time.sleep(1)
     connection.write_channel("configure bridge no port 1/1/"+Card_Port+":0:35"+ "\r"+"exit\r"+"exit\r" )
     time.sleep(1)
     connection.write_channel("configure atm no pvc  1/1/"+Card_Port+":0:35"+"\r" )
     time.sleep(1)
     connection.write_channel("configure atm pvc  1/1/"+Card_Port+":0:35"+ " aal5-encap-type llc-snap"+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan) +" mode cross-connect"+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan)+"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan) +" pppoe-relay-tag true"+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port 1/1/"+Card_Port+":0:35"+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+":0:35"+" pvid " +str(inner_vlan) +"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port 1/1/"+Card_Port+":0:35"+" vlan-id "+ str(inner_vlan)+" no tag l2fwder-vlan stacked:"+outer_vlan+":"+ str(inner_vlan)+ " vlan-scope local no qos no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid" +"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port 1/1/"+Card_Port+":0:35"+" vlan-id "+"stacked:"+outer_vlan+":"+ str(inner_vlan)+"\r" )
     time.sleep(1)
     connection.write_channel("configure bridge port  1/1/"+Card_Port+":0:35"+" pvid " +str(inner_vlan) +"\r" )
     time.sleep(1)
     connection.write_channel("configure vlan id stacked:"+outer_vlan+":"+ str(inner_vlan)+" circuit-id-pppoe physical-id remote-id-pppoe customer-id"+"\r" )
     time.sleep(1)
     connection.write_channel("configure xdsl line 1/1/"+Card_Port+"\r" )
     time.sleep(1)
     connection.write_channel("no admin-up"+"\r" )
     time.sleep(1)
     connection.write_channel("admin-up"+"\r" )
     time.sleep(1)
     print('Closing connection')
     connection.disconnect()
     




        

    

def Nokia(Cabinet_Host,Cabinet_IP,Port_Location):

    connection=Netmiko_NOKIA(Cabinet_IP,Username,Password)

   

############################ Getting shelf number/Card/Port/inner vlan  values from ASSIA #########################    
    shelf_number=Cabinet_Host[Cabinet_Host.index("-M0")+3]
    Port_Splitted=Port_Location.split("-")
    Port=str(Port_Splitted[-1])
    Card=str(Port_Splitted[-2])
    Card_Port=Card+"/"+Port
    int_inner_vlan=(((int(shelf_number) -1) * 1520) +100 )   +   ( int(Card) * 76  )+int( Port )
    inner_vlan=str(int_inner_vlan)
    print("Right Inner VLAN is : "+inner_vlan)


    


    #################################### Getting Outer VLAN ########################################################
    time.sleep(1)
    show_vlan = connection.send_command_timing('show vlan fdb-board\r', cmd_verify=False, read_timeout=120)
    #print(show_vlan)
    a = re.findall("[4-4][0-9][0-9]", show_vlan)
        
    def most_frequent(a): 
        return max(set(a), key = a.count)

    outer_vlan=(most_frequent(a))
    


    #################################### Getting Port configuration and Action is starting ;) #####################################################
    time.sleep(1)

    Port_Conf = connection.send_command_timing("info configure bridge port 1/1/"+Card+"/"+Port+":0:35\r", cmd_verify=False, read_timeout=10)

    if  "invalid token" in Port_Conf: #####  VDSL Config
        
        Port_Conf = connection.send_command_timing("info configure bridge port 1/1/"+Card+"/"+Port+"\r", cmd_verify=False, read_timeout=10)
        Conf_Split=Port_Conf.split()


        if  "vlan-id" not in Conf_Split or "l2fwder-vlan" not in Conf_Split or "pvid" not in Conf_Split : # No Conf or there is some messing Conf.
            if  outer_vlan =="480":
                NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection)
                return ("Port Configuration Adjusted")
            else :
                inner_vlan=str(random.randint(3500,4000))
                NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection)
                return ("Port Configuration Adjusted")

        
        else : ### Config exists and will check Outer VLAN is equal 480 or not and act accordingly

            Current_inner=Conf_Split[(Conf_Split.index("vlan-id"))+1]
            Getting_stacked=Conf_Split[(Conf_Split.index("l2fwder-vlan"))+1]
            stacked_split=Getting_stacked.split(":")
            port_outervlan=stacked_split[1]

            if  outer_vlan =="480":

                if  port_outervlan==outer_vlan :

                    if  Current_inner==inner_vlan:

                        print('Closing connection')
                        connection.disconnect()
                        return ("Right Configuration")
                        
                    else :

                        NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection)
                        return ("Inner Mismatch,"+"Old Inner="+Current_inner+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)
                else :

                    NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection)
                    return ("Schema-Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)




            else :

                inner_vlan=str(random.randint(3500,4000))

                if  port_outervlan==outer_vlan :
                    print('Closing connection')
                    connection.disconnect()
                    return ("Right Configuration")
                    

                else :

                    NOKIA_VDSL(Card_Port,outer_vlan,inner_vlan,connection)
                    return ("Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)






            

    else : ################################  ADSL Config

        Conf_Split=Port_Conf.split()


        if  "vlan-id" not in Conf_Split or "l2fwder-vlan" not in Conf_Split or "pvid" not in Conf_Split : # No Conf or there is some messing Conf.
            if  outer_vlan =="480":
                NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection)
                return ("Port Configuration Adjusted")
            else :
                inner_vlan=str(random.randint(3500,4000))
                NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection)
                return ("Port Configuration Adjusted")
        
        else : ### Config exists and will check Outer VLAN is equal 480 or not and act accordingly

            Current_inner=Conf_Split[(Conf_Split.index("vlan-id"))+1]
            Getting_stacked=Conf_Split[(Conf_Split.index("l2fwder-vlan"))+1]
            stacked_split=Getting_stacked.split(":")
            port_outervlan=stacked_split[1]

            if  outer_vlan =="480":

                if  port_outervlan==outer_vlan :

                    if  Current_inner==inner_vlan:
                        print('Closing connection')
                        connection.disconnect()
                        return ("Right Configuration")
                    else :

                        NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection)
                        return ("Inner Mismatch,"+"Old Inner="+Current_inner+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)
                else :

                    NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection)
                    return ("Schema-Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)




            else :

                inner_vlan=str(random.randint(3500,4000))

                if  port_outervlan==outer_vlan :
                    print('Closing connection')
                    connection.disconnect()
                    return ("Right Configuration")

                else :

                    NOKIA_ADSL(Card_Port,outer_vlan,inner_vlan,connection)
                    return ("Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)
        


    
# Using Initiated Session from Selenium Iterator function to iterate on the accounts from TTS.

def SeleniumIterator():
    Accountnum=str(input("Please Enter Account number : "))
    options1 = webdriver.ChromeOptions()
    options1.add_argument("--headless")
    options1.add_argument('--ignore-certificate-errors')
    options1.add_argument('--ignore-ssl-errors')
    options1.add_experimental_option('excludeSwitches', ['enable-logging'])
    options1.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
    options1.add_experimental_option("detach", True)
    driver1 = webdriver.Chrome( options=options1)
    driver1.maximize_window()
    driver1.get("https://10.42.187.100:8080/expresse/login-page")
    
    search_input2=driver1.find_element('xpath',"(//input[contains(@id, 'j_username')])")
    search_input2.send_keys("Mostafa_h_mostafa")
    search_input3=driver1.find_element('xpath',"(//input[contains(@id, 'j_password')])")
    search_input3.send_keys("Ahmed_1_1_1")
    search_input3.send_keys(Keys.ENTER)
    
    try :
        
        link="https://10.42.187.100:8080/expresse/lineSummary?lineId="+Accountnum
        driver1.get(link)
        Cabinet_Host=driver1.find_element('xpath','//*[@id="j_idt97:text:text"]').text
        Port_Location=driver1.find_element('xpath','//*[@id="portInfoRow:portInfo:singlePort_linkOrText:linkAsText:text"]').text
        CabinetIPUrl="https://10.42.187.100:8080/expresse/dslam?dslam="+Cabinet_Host
        driver1.get(CabinetIPUrl)
        Cabinet_IP=driver1.find_element('xpath','//*[@id="basicDslamData:basicDslamData:1:value:linkAsText:text"]').text
        #CabinetType=driver1.find_element('xpath','//*[@id="basicDslamData:basicDslamData:2:value:linkAsText:text"]').text

    
    except :

        Cabinet_Host,Cabinet_IP,Port_Location="None","None","None"
    #print(Cabinet_Host,Cabinet_IP,Port_Location)
    driver1.quit()

    return Cabinet_Host,Cabinet_IP,Port_Location
    

def Main():
    try:
        Cabinet_Host,Cabinet_IP,Port_Location=SeleniumIterator()
        result=Nokia(Cabinet_Host,Cabinet_IP,Port_Location)
        print("Ticket Status is : "+result+"\r\r\r")
        
    except Exception:
        print("Connection is Failed!")

Main()














