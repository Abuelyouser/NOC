

from netmiko import ConnectHandler
import time
import csv
import random
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import itertools
import re

####################################################################################################

#service_port_value=" "

########################################################

# Reading domain username & password from D:\
with open(r'D:\password.txt', mode='r') as up:

        lu=up.readline()
        lp=up.readline()
Username = lu.replace('\n','')

Password = lp.replace('\n','')

def Netmiko_ZTE(Cabinet_IP,Username,Password):
    try:
        device = {
        'device_type': 'autodetect',
        'host': Cabinet_IP,
        'username': Username,
        'password': Password ,
        'port': 22,
        'secret': 'zxr10',
        'fast_cli': False
        }
        connection = ConnectHandler(**device)
        print("Login Success with Domain UN&PW !")
        return connection
    except:
        device1 = {
        'device_type': 'autodetect',
        'host': Cabinet_IP,
        'username': 'tednoc',
        'password': 'tednoc#123' ,
        'port': 22,  # optional, default 22
        'secret': 'zxr10',
        'fast_cli': False
        }
        connection = ConnectHandler(**device1)
        print("Login Success with tednoc !")
        return connection
    


    
def get_my_value(text, mark):
    text = text.split()
    values = []
    if text.count(mark) > 1:
        for i in range(text.count(mark)):
            values.insert(i,text[text.index(mark) + 1])
            text.remove(mark)
    elif text.count(mark) == 1:
        values.insert(0,text[text.index(mark) + 1])
    else:
        values = []
    return values


def delete_confvdsl(connection):
    connection.write_channel(" no switchport default vlan \r")
    connection.write_channel(" no switchport default cvlan \r")
    connection.write_channel(" no switchport default vlan pvc 1\r")
    connection.write_channel(" no switchport default cvlan pvc 1\r")
    time.sleep(2)

def delete_confadsl(connection):
    connection.write_channel(" no switchport default cvlan pvc 1"+"\r")
    connection.write_channel(" no switchport default vlan pvc 1"+"\r")
    time.sleep(2)
    

def conf_atm(connection):
    connection.write_channel(" atm pvc 1 vpi 0 vci 35 "+"\r")
    connection.write_channel(" atm pvc 2 vpi 0 vci 32 "+"\r")
    time.sleep(2)


def Enter_interface(connection,interface_type,Card_Port): 

    connection.write_channel(" interface "+interface_type+"_"+Card_Port+"\r")
    time.sleep(1)

def Exit_interface(connection):
    connection.write_channel("exit\r")
    time.sleep(1)

def ZTE_VDSL_Push(the_outer_vlan,inner_vlan,connection):
    
    connection.write_channel(" switchport default vlan "+the_outer_vlan+"\r")
    connection.write_channel(" switchport default vlan "+the_outer_vlan+" pvc 1"+"\r")
    connection.write_channel(" switchport default cvlan "+inner_vlan+"\r")
    connection.write_channel(" switchport default cvlan "+inner_vlan+" pvc 1"+"\r")
    time.sleep(2)


def ZTE_ADSL_Push(the_outer_vlan,inner_vlan,connection):
    
    connection.write_channel(" switchport default vlan "+the_outer_vlan+" pvc 1" +"\r")
    connection.write_channel(" switchport default cvlan "+inner_vlan+" pvc 1" +"\r")
    time.sleep(2)

def Restart_Port(connection):
    connection.write_channel("shut" +"\r")
    connection.write_channel("no shut" +"\r")
    time.sleep(1)

def Connection_Terminate(connection):

    print('Closing connection')
    connection.disconnect()
    

def ZTE(Cabinet_Host,Cabinet_IP,Port_Location):


    connection=Netmiko_ZTE(Cabinet_IP,Username,Password)

   

############################ Getting shelf number/Card/Port/inner vlan  values from ASSIA ######################### 
   
    ipsplit=Cabinet_IP.split(".")
    #crt.Dialog.MessageBox(str(ipsplit))
    ipremainder=int(ipsplit[3])%2
    #crt.Dialog.MessageBox(str(ipremainder))

    if ipremainder==0:

        shelf_number=1

    if ipremainder==1:

        shelf_number=2

#########################################################################################################################

    Port_Splitted=Port_Location.split("-")
    Port=str(Port_Splitted[-1])
    Card=str(Port_Splitted[-2])
    ADSL_Shelf=str(Port_Splitted[-3])
    Card_Port=ADSL_Shelf+"/"+Card+"/"+Port
    int_inner_vlan=(((shelf_number -1) * 1520) +100 )   +   ( int(Card) * 76  )+int( Port )
    inner_vlan=str(int_inner_vlan)
    #print("Right Inner VLAN is : "+inner_vlan)
    randomInner = str(random.randint(3600,3999))
    atm_pvc1="atm pvc 1 vpi 0 vci 35"

############################################################################################################################
    connection.send_command('terminal length 0\n')
    connection.send_command('configure terminal\n', cmd_verify=False, read_timeout=10, expect_string='#')
    show_mac = connection.send_command('show mac\n', cmd_verify=False, read_timeout=120)
    all_vlans = show_mac.split()
    r = re.compile("[4-4][0-9][0-9]")
    new_list = list(filter(r.match, all_vlans))

    """
    this method used to get the most frequent items.
    """
    def most_frequent(List):
        return max(set(List), key=List.count)
    the_outer_vlan = most_frequent(new_list)
    print('the outer vlan is : ' + the_outer_vlan)


    show_card = connection.send_command('show card\n', cmd_verify=False, read_timeout=10)
    #print(show_card)
    #print("*********************************************************")
    entries = show_card.splitlines()[3:] ## spliting show card by lines
    #print(entries)
    for entry in entries:                    ## looping on each line 
        splitedentry=entry.split()           ## spliting each line
        if splitedentry[2]==Card:            ## checking third item in each line which is slot if its equal to card which we get from ASSIA
            
            if  splitedentry[3]=="VDWVD" or splitedentry[3]=="VBWKD" :## if Card number from ASSIA matched,checking fourth item in the line which is CFGtype
                card_type="VDSL"
                interface_type='vdsl'
            elif splitedentry[3]=="ACWVC" or splitedentry[3]=="ACWKC" or splitedentry[3]=="GELCA":
                card_type="ADSL"
                interface_type='adsl'
                                              
            else :
                continue
            
        else :
            continue
    print("Card type is : "+card_type +"\r\r\r")

    if card_type=="VDSL" :
        
        Port_Conf = connection.send_command_timing('show running-config interface vdsl_'+Card_Port+"\r",cmd_verify=False, read_timeout=10)
        print("**************************\r***********************\r"+Port_Conf+"\r\r\r\r\r\r")
        outerVlanOfPort = get_my_value(Port_Conf, "vlan")
        innerVlanOfPort = get_my_value(Port_Conf, "cvlan")
        


        if  outerVlanOfPort == [] and innerVlanOfPort == []:

            if the_outer_vlan == "480":

                Enter_interface(connection,interface_type,Card_Port)
                conf_atm(connection)
                ZTE_VDSL_Push(the_outer_vlan,inner_vlan,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "Schema-There is no Configuration"

            else:

                Enter_interface(connection,interface_type,Card_Port)
                conf_atm(connection)
                ZTE_VDSL_Push(the_outer_vlan,randomInner,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "There is no Configuration"

        elif len(outerVlanOfPort) < 2 or  len(innerVlanOfPort) < 2:

            if the_outer_vlan == "480":
                Enter_interface(connection,interface_type,Card_Port)
                delete_confvdsl(connection)
                conf_atm(connection)
                ZTE_VDSL_Push(the_outer_vlan,inner_vlan,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "Corrected"

            else:

                Enter_interface(connection,interface_type,Card_Port)
                delete_confvdsl(connection)
                conf_atm(connection)
                ZTE_VDSL_Push(the_outer_vlan,randomInner,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "Corrected"



        elif len(outerVlanOfPort) == 2 and len(outerVlanOfPort) == 2 : 

            if  the_outer_vlan != outerVlanOfPort[0] or the_outer_vlan != outerVlanOfPort[1]:

                wrong_outer = outerVlanOfPort[0] if outerVlanOfPort[0] != the_outer_vlan else outerVlanOfPort[1]

                if the_outer_vlan == "480" :

                    Enter_interface(connection,interface_type,Card_Port)
                    delete_confvdsl(connection,the_outer_vlan,inner_vlan)
                    conf_atm(connection)
                    ZTE_VDSL_Push(the_outer_vlan,inner_vlan,connection)
                    Restart_Port(connection)
                    Exit_interface(connection)
                    Connection_Terminate(connection)
                    return "Schema-Wrong Outer VLAN,"+wrong_outer+","+the_outer_vlan+","+Cabinet_IP

                else:

                    Enter_interface(connection,interface_type,Card_Port)
                    delete_confvdsl(connection)
                    conf_atm(connection)
                    ZTE_VDSL_Push(the_outer_vlan,innerVlanOfPort[0],connection)
                    Restart_Port(connection)
                    Exit_interface(connection)
                    Connection_Terminate(connection)
                    return "Wrong Outer VLAN,"+wrong_outer+","+the_outer_vlan+","+Cabinet_IP



            else: 

                if the_outer_vlan == "480" :

                    if inner_vlan !=innerVlanOfPort[0] or inner_vlan != innerVlanOfPort[1]:

                        wrong_inner = innerVlanOfPort[0] if innerVlanOfPort[0] != inner_vlan else innerVlanOfPort[1] 

                        Enter_interface(connection,interface_type,Card_Port)
                        delete_confvdsl(connection)
                        conf_atm(connection)
                        ZTE_VDSL_Push(the_outer_vlan,inner_vlan,connection)
                        Restart_Port(connection)
                        Exit_interface(connection)
                        Connection_Terminate(connection)

                        return "Schema-Inner Mismatch,"+"Old Inner="+wrong_inner+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP

                    else :
                        
                        if  atm_pvc1 not in Port_Conf:
                            Enter_interface(connection,interface_type,Card_Port)
                            conf_atm(connection)
                            Exit_interface(connection)
                            Connection_Terminate(connection)
                            return "Corrected ATM"

                        else:
                            return "Right Configuration"
                else :

                    if  atm_pvc1 not in Port_Conf:
                        Enter_interface(connection,interface_type,Card_Port)
                        conf_atm(connection)
                        Exit_interface(connection)
                        Connection_Terminate(connection)
                        return "Corrected ATM"
                            
                    else:
                        return "Right Configuration"

                        


                
                

    elif card_type=="ADSL" :
        
        Port_Conf = connection.send_command_timing('show running-config interface adsl_'+Card_Port+"\r",cmd_verify=False, read_timeout=10)
        print(Port_Conf)
        outerVlanOfPort = get_my_value(Port_Conf, "vlan")
        innerVlanOfPort = get_my_value(Port_Conf, "cvlan")
        if outerVlanOfPort == [] and innerVlanOfPort == []:

            if the_outer_vlan == "480" :

                Enter_interface(connection,interface_type,Card_Port)
                conf_atm(connection)
                ZTE_ADSL_Push(the_outer_vlan,inner_vlan,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "Schema-There is no Configuration"


            else :

                Enter_interface(connection,interface_type,Card_Port)
                conf_atm(connection)
                ZTE_ADSL_Push(the_outer_vlan,randomInner,connection)
                Restart_Port(connection)
                Exit_interface(connection)
                Connection_Terminate(connection)
                return "There is no Configuration"


        else:
            if  the_outer_vlan != outerVlanOfPort[0]:

                if the_outer_vlan =="480":

                    Enter_interface(connection,interface_type,Card_Port)
                    delete_confadsl(connection)
                    conf_atm(connection)
                    ZTE_ADSL_Push(the_outer_vlan,inner_vlan,connection)
                    Restart_Port(connection)
                    Exit_interface(connection)
                    Connection_Terminate(connection)

                else :

                    Enter_interface(connection,interface_type,Card_Port)
                    delete_confadsl(connection)
                    conf_atm(connection)
                    ZTE_ADSL_Push(the_outer_vlan,randomInner,connection)
                    Restart_Port(connection)
                    Exit_interface(connection)
                    Connection_Terminate(connection)

            else :

                if  the_outer_vlan =="480":

                    if  inner_vlan !=innerVlanOfPort[0]:

                        Enter_interface(connection,interface_type,Card_Port)
                        delete_confadsl(connection)
                        conf_atm(connection)
                        ZTE_ADSL_Push(the_outer_vlan,inner_vlan,connection)
                        Restart_Port(connection)
                        Exit_interface(connection)
                        Connection_Terminate(connection)
                        return "Schema-Inner Mismatch,"+"Old Inner="+innerVlanOfPort[0]+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP

                    else :

                        if  atm_pvc1 not in Port_Conf:
                            Enter_interface(connection,interface_type,Card_Port)
                            conf_atm(connection)
                            Exit_interface(connection)
                            Connection_Terminate(connection)
                            return "Corrected ATM"
                                    
                        else:

                            return "Right Configuration"
                else :

                    if  atm_pvc1 not in Port_Conf:
                        Enter_interface(connection,interface_type,Card_Port)
                        conf_atm(connection)
                        Exit_interface(connection)
                        Connection_Terminate(connection)
                        return "Corrected ATM"
                                    
                    else:

                        return "Right Configuration"


                        
                        
                

                





            


    
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
    #try:
    Cabinet_Host,Cabinet_IP,Port_Location=SeleniumIterator()
    result=ZTE(Cabinet_Host,Cabinet_IP,Port_Location)
    print("Ticket Status is : "+result+"\r\r\r")
        
    #except Exception:
        #print("Connection is Failed!")

Main()














