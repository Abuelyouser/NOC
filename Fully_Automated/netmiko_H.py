from netmiko import ConnectHandler
import time
import csv
import random
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
####################################################################################################

#service_port_value=" "

########################################################

# Reading domain username & password from D:\
with open(r'D:\Password.txt', mode='r') as up:

        lu=up.readline()
        lp=up.readline()
Username = lu.replace('\n','')

Password = lp.replace('\n','')

def Netmiko_Huawei(Cabinet_IP,Username,Password):
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
        'username': 'tednoc',
        'password': 'tednoc#123' ,
        'port': 22,  # optional, default 22
        'fast_cli': False,
        }
        connection = ConnectHandler(**device1)
        print("Login Success with tednoc !")
        return connection

####################################################################################################################################


def Restart_Port(Card,Port,connection,board_type):
    connection.write_channel(" interface "+board_type+" 0/"+Card + "\r")
    time.sleep(1)
    connection.write_channel(" deactivate " + Port + "\r")
    time.sleep(1)
    connection.write_channel(" activate " + Port + "\r")
    time.sleep(1)
    connection.write_channel("\r")
    time.sleep(1)
    connection.write_channel("quit\r")
    time.sleep(1)

def Stacking_label(outer_vlan,Stacking_Shelf,connection):

    if  Stacking_Shelf=="1"  :

        connection.write_channel("stacking label vlan "+ outer_vlan+" baselabel 101" + "\ry\r")

    elif Stacking_Shelf=="2"  :

        connection.write_channel("stacking label vlan "+ outer_vlan+" baselabel 2501" + "\ry\r")

    else : 
        pass

    time.sleep(1)

def Connection_Terminate(connection):

    print('Closing connection')
    connection.disconnect()

def Undo_service_port(port_serviceport,connection):

    connection.write_channel(" undo service-port " + port_serviceport + "\r")
    time.sleep(2)


def Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection):

    connection.write_channel(" service-port " + port_serviceport + " vlan "+outer_vlan+" adsl "+Card_Port+"  vpi 0 vci 35 single-service tag-transform add-double inner-vlan "+ inner_vlan +" inbound traffic-table index 6 outbound traffic-table index 6"+"\r")
    time.sleep(2)

def Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection):

    connection.write_channel(" service port " + " vlan "+outer_vlan+" vdsl mode atm "+Card_Port+"  vpi 0 vci 35 single-service tag-transform add-double inner-vlan "+inner_vlan +" inbound traffic-table index 6 outbound traffic-table  index 6"+"\r")
    time.sleep(2)
    
def Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection):

    connection.write_channel(" service port " + " vlan "+outer_vlan+" vdsl mode ptm "+Card_Port+"  tag-transform add-double inner-vlan "+inner_vlan +" inbound traffic-table index 6 outbound traffic-table  index 6"+"\r")
    time.sleep(2)




    

    

def Huawei(Cabinet_Host,Cabinet_IP,Port_Location):

    connection=Netmiko_Huawei(Cabinet_IP,Username,Password)

   

############################ Getting shelf number/Card/Port/inner vlan  values from ASSIA ######################### 
   
    ipsplit=Cabinet_IP.split(".")
    #crt.Dialog.MessageBox(str(ipsplit))
    ipremainder=int(ipsplit[3])%2
    #crt.Dialog.MessageBox(str(ipremainder))

    if ipremainder==0:

        shelf_number=1

    if ipremainder==1:

        shelf_number=2
##########################################################################################################################

    Stacking_Shelf=Cabinet_Host[Cabinet_Host.index("-M0")+3]
    #print("stacking shelf is : "+Stacking_Shelf+"\r")



#########################################################################################################################

    Port_Splitted=Port_Location.split("-")
    Port=str(Port_Splitted[-1])
    Card=str(Port_Splitted[-2])
    Card_Port="0/"+Card+"/"+Port
    int_inner_vlan=(((shelf_number -1) * 1520) +100 )   +   ( int(Card) * 76  )+int( Port )
    inner_vlan=str(int_inner_vlan)
    #print("Right Inner VLAN is : "+inner_vlan)


####Pushing Scroll 512 to show output in 512 lines + enable + config + getting Outer VLAN value####################

    connection.send_command_timing('scroll 512 \r enable \r config\r')
    show_vlan=connection.send_command_timing('display service-port all | include stacking\r\003',cmd_verify=False, read_timeout=120)
    a = re.findall("[4-5][0-9][0-9]", show_vlan)
        
    def most_frequent(a): 
        return max(set(a), key = a.count)

    outer_vlan=(most_frequent(a))
    #print(show_vlan)
    #print(outer_vlan)

####################################################################################################################

    Port_Conf = connection.send_command_timing('display current-configuration port 0/'+Card+'/'+Port+"\r",cmd_verify=False, read_timeout=10)

    

    if  "Failure:" in Port_Conf:
        print("Cabinet is saving configuration, 120 seconds count-down timer started..")
        time.sleep(120)
        Port_Conf = connection.send_command_timing('display current-configuration port 0/'+Card+'/'+Port+"\r",cmd_verify=False, read_timeout=10)
        pass


    if  "mac-address" in Port_Conf:
        Port_Conf=Port_Conf[:Port_Conf.find("mac-address")]

    print(Port_Conf)
    


    if  "[adsl]" in Port_Conf:

        board_type="adsl"

        if  "service-port" not in Port_Conf: #### config messing

            if  outer_vlan=="480": ## Schema
                port_serviceport=" "
                Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection)
                Restart_Port(Card,Port,connection,board_type)
                Connection_Terminate(connection)
                return "Schema-There is No Configuration"


            else : ### Old cabinets

                port_serviceport=" "
                Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection)
                Restart_Port(Card,Port,connection,board_type)
                Stacking_label(outer_vlan,Stacking_Shelf,connection)
                Connection_Terminate(connection)
                
                return "There is No Configuration"

        else : ####### else service port exists.

            Conf_Split=Port_Conf.split()

            port_outervlan=Conf_Split[(Conf_Split.index("vlan"))+1]
            port_serviceport=Conf_Split[(Conf_Split.index("service-port"))+1]
            port_innervlan=Conf_Split[(Conf_Split.index("inner-vlan"))+1]

            if  port_outervlan!=outer_vlan: ###### matching if port outer vlan not equal with cabinet outer vlan

                if outer_vlan=="480": ## if cabinet outer vlan == 480 ( Schema )
                    
                    Undo_service_port(port_serviceport,connection)
                    Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection)
                    Restart_Port(Card,Port,connection,board_type)
                    Connection_Terminate(connection)
                    return ("Schema-Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)

                else :   ##if cabinet outer vlan != 480 ( Old Cabinet )

                    Undo_service_port(port_serviceport,connection)
                    Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection)
                    Restart_Port(Card,Port,connection,board_type)
                    Stacking_label(outer_vlan,Stacking_Shelf,connection)
                    Connection_Terminate(connection)

                    return ("Wrong Outer VLAN,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)


            else : ### else if port outer vlan equal to cabinet outer vlan

                

                if  outer_vlan =="480": #### else its schema cabinet will check port inner vlan with schema inner vlan


                    if  port_innervlan !=inner_vlan:

                        Undo_service_port(port_serviceport,connection)
                        Push_ADSL_ATM(port_serviceport,outer_vlan,Card_Port,inner_vlan,connection)
                        Restart_Port(Card,Port,connection,board_type)
                        Connection_Terminate(connection)

                        return ("Schema-ATM Inner Mismatch,"+"Old Inner="+port_innervlan+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)
                        
                    else :
                        Restart_Port(Card,Port,connection,board_type)
                        Connection_Terminate(connection)
                        return ("Right Configuration")

                else : ## if its old cabinet stacking label will be pushed.

                    Restart_Port(Card,Port,connection,board_type)
                    Stacking_label(outer_vlan,Stacking_Shelf,connection)
                    Connection_Terminate(connection)

                    return ("Right Configuration")




    if  "[vdsl]" in Port_Conf:

        board_type="vdsl"

        if  "service-port" not in Port_Conf: #### config messing

            if outer_vlan=="480": # Schema
            
                
                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                Restart_Port(Card,Port,connection,board_type)
                Connection_Terminate(connection)
                return "Schema-There is No Configuration"

            else: # Old Cabinet

                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                Restart_Port(Card,Port,connection,board_type)
                Stacking_label(outer_vlan,Stacking_Shelf,connection)
                Connection_Terminate(connection)

                return "There is No Configuration"


        else : # there is 1 or 2 service ports.

            Conf_Split=Port_Conf.split()
            Service_Port_Count=Conf_Split.count('service-port')

            if Service_Port_Count ==1 :

                port_outervlan=Conf_Split[(Conf_Split.index("vlan"))+1]
                port_serviceport=Conf_Split[(Conf_Split.index("service-port"))+1]
                port_innervlan=Conf_Split[(Conf_Split.index("inner-vlan"))+1]

                if  "atm" in Port_Conf :

                    if  outer_vlan=="480":

                        if  port_outervlan!=outer_vlan:

                            Undo_service_port(port_serviceport,connection)
                            Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                            Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Connection_Terminate(connection)
                            return ("Schema-Wrong Outer VLAN + no PTM Conf,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)

                        else :

                            if  port_innervlan !=inner_vlan:
                                Undo_service_port(port_serviceport,connection)
                                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                                Restart_Port(Card,Port,connection,board_type)
                                Connection_Terminate(connection)
                                return ("Schema-ATM Inner Mismatch + no PTM Conf ,"+"Old Inner="+port_innervlan+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)

                            else:
                                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                                Restart_Port(Card,Port,connection,board_type)
                                Connection_Terminate(connection)
                                return ("Schema-There is no PTM configuration")
                    else:

                        if  port_outervlan!=outer_vlan:

                            Undo_service_port(port_serviceport,connection)
                            Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                            Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Stacking_label(outer_vlan,Stacking_Shelf,connection)
                            Connection_Terminate(connection)


                            return ("Wrong Outer VLAN + no PTM Conf,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)

                        else:

                            Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Stacking_label(outer_vlan,Stacking_Shelf,connection)
                            Connection_Terminate(connection)

                            return ("There is no PTM configuration")





                else : ### there is PTM in config and atm is messing

                    if  outer_vlan=="480":

                        if  port_outervlan!=outer_vlan:

                            Undo_service_port(port_serviceport,connection)
                            Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                            Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Connection_Terminate(connection)
                            return ("Schema-Wrong Outer VLAN + no ATM Conf,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)

                        else :

                            if  port_innervlan !=inner_vlan:
                                Undo_service_port(port_serviceport,connection)
                                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                                Restart_Port(Card,Port,connection,board_type)
                                Connection_Terminate(connection)
                                return ("Schema-PTM Inner Mismatch + no ATM Conf,"+"Old Inner="+port_innervlan+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)

                            else:
                                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                                Restart_Port(Card,Port,connection,board_type)
                                Connection_Terminate(connection)
                                return ("Schema-There is no ATM configuration")
                    else:

                        if  port_outervlan!=outer_vlan:

                            Undo_service_port(port_serviceport,connection)
                            Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                            Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Stacking_label(outer_vlan,Stacking_Shelf,connection)
                            Connection_Terminate(connection)

                            return ("Wrong Outer VLAN + no ATM Conf,"+port_outervlan+","+outer_vlan+","+Cabinet_IP)

                        else:

                            Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                            Restart_Port(Card,Port,connection,board_type)
                            Stacking_label(outer_vlan,Stacking_Shelf,connection)
                            Connection_Terminate(connection)

                            return ("There is no ATM configuration")


                            

            if  Service_Port_Count ==2 :

                port_outervlan=Conf_Split[(Conf_Split.index("vlan"))+1]
                port_serviceport=Conf_Split[(Conf_Split.index("service-port"))+1]
                port_innervlan=Conf_Split[(Conf_Split.index("inner-vlan"))+1]
                

                port_outervlan1=Conf_Split[(Conf_Split.index("vlan",Conf_Split.index("vlan")+1))+1]
                port_serviceport1=Conf_Split[(Conf_Split.index("service-port",Conf_Split.index("service-port")+1))+1]
                port_innervlan1=Conf_Split[(Conf_Split.index("inner-vlan",Conf_Split.index("inner-vlan")+1))+1]

                #print(port_outervlan)
                #print(port_serviceport)
                #print(port_innervlan)
                #print(port_outervlan1)
                #print(port_serviceport1)
                #print(port_innervlan1)



                ATM_inner_vlan=Conf_Split[Conf_Split.index("atm")+10]
                PTM_inner_vlan=Conf_Split[Conf_Split.index("ptm")+5]
                ATM_service_port=Conf_Split[Conf_Split.index("atm")-5]
                PTM_service_port=Conf_Split[Conf_Split.index("ptm")-5]


                if  port_outervlan != outer_vlan or port_outervlan1 !=outer_vlan :

                    wrong_outer = port_outervlan if port_outervlan != outer_vlan else port_outervlan1

                    if  outer_vlan=="480":
                        Undo_service_port(port_serviceport,connection)
                        Undo_service_port(port_serviceport1,connection)
                        Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                        Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                        Restart_Port(Card,Port,connection,board_type)
                        Connection_Terminate(connection)
                        return ("Schema-Wrong Outer VLAN,"+wrong_outer+","+outer_vlan+","+Cabinet_IP)




                    else:
                        Undo_service_port(port_serviceport,connection)
                        Undo_service_port(port_serviceport1,connection)
                        Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                        Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                        Restart_Port(Card,Port,connection,board_type)
                        Stacking_label(outer_vlan,Stacking_Shelf,connection)
                        Connection_Terminate(connection)
                        return ("Wrong Outer VLAN,"+wrong_outer+","+outer_vlan+","+Cabinet_IP)
                else :

                    if  outer_vlan=="480":
                        
                        if  ATM_inner_vlan != inner_vlan or PTM_inner_vlan != inner_vlan :

                            g=""

                            if  ATM_inner_vlan != inner_vlan :
                                
                                Undo_service_port(ATM_service_port,connection)
                                Push_VDSL_ATM(outer_vlan,Card_Port,inner_vlan,connection)
                                g=("Schema-ATM Inner Mismatch,"+"Old Inner="+ATM_inner_vlan+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)

                            if  PTM_inner_vlan != inner_vlan :
                                
                                Undo_service_port(PTM_service_port,connection)
                                Push_VDSL_PTM(outer_vlan,Card_Port,inner_vlan,connection)
                                g=g+("Schema-PTM Inner Mismatch,"+"Old Inner="+PTM_inner_vlan+", New Inner = "+inner_vlan +", Cabinet IP="+Cabinet_IP)

                            Restart_Port(Card,Port,connection,board_type)
                            Connection_Terminate(connection)
                            return g

                        else:

                            Restart_Port(Card,Port,connection,board_type)
                            Connection_Terminate(connection)
                            return ("Right Configuration")


                    else :

                        Restart_Port(Card,Port,connection,board_type)
                        Stacking_label(outer_vlan,Stacking_Shelf,connection)
                        Connection_Terminate(connection)
                        return ("Right Configuration")





    else :

        return "Couldn't detect Port type"



    
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
    result=Huawei(Cabinet_Host,Cabinet_IP,Port_Location)
    print("Ticket Status is : "+result+"\r\r\r")
        
    #except Exception:
        #print("Connection is Failed!")

Main()














