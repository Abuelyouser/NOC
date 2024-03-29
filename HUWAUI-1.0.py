import re

ip = crt.Dialog.Prompt("Please Enter Your Cabinet")
SSHname = "mohamed.a.youser"
SSHpassword = "Sky!sThelimit990"


crt.Screen.Send("alias " + ip + "\r")

"""
This method take the port/card and return >> 0/port/card
"""
def write_port(p):
    p = p.split('/')
    Card_Port = "0/{fcard}/{fport}".format(fcard=p[0], fport=p[1])
    return Card_Port


"""
this method used to only read string from the screen
"""
def reader(stop_word):
    return crt.Screen.ReadString(stop_word)

alias_result = reader("[")

p = crt.Dialog.Prompt("Please Enter Your ADSL Port as Card/Port '0/0'")
card_port = write_port(p)


"""
This method used to return value(s) after the word mark and return an empty list if the mark word not found in text.
text >> we can pass this value from reader method
"""
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

"""
this is the same method excpet it takes 2 marks and returns the most repeated one .. we use this func to get the last service port 
from the command display service-port all 
"""
def get_my_value2(text2,mark1,mark2):
    for i in range(2):
        r = []
        r1 = get_my_value(text2,mark1)
        r2 = get_my_value(text2,mark2)
        rr = r1 + r2
    for i in range(len(rr)):
        r.append(int(rr[i]))
    return r


"""
this method used to only send the command
"""
def send_only(command):
    return crt.Screen.Send(str(command)+ "\r")


"""
this method used to send command and get the output screen from this command  take two argument 1. the command 2. what we need to read (start word,last word)
then return the value of the screen
"""
def send_get_screen(command, stop_word ,start_word="", last_word=""):
    crt.Screen.Send(str(command)+ "\r\r")
    all_screen = crt.Screen.ReadString(str(stop_word))
    all_screen = all_screen.split()
    if start_word == "" and last_word == "":
        return all_screen
    return all_screen[all_screen.index(start_word):all_screen.index(last_word)]

"""
check if the returned string from alias <hostname> have an SSH or Telnet word and return the IP.
"""
def login_check(alias_result):
    if "not found" not in alias_result:
        if "ssh" in alias_result:
            aliasip = alias_result.find("'ssh")
            aliasip1 = alias_result.find("'", aliasip+1)
            the_ip = alias_result[aliasip+5:aliasip1]
            return the_ip
        elif "telnet" in alias_result:
            aliasip = alias_result.find("'telnet")
            aliasip1 = alias_result.find("'", aliasip+1)
            the_ip = alias_result[aliasip+8:aliasip1]
            return the_ip

#crt.Dialog.MessageBox(str(login_check(alias_result)))


"""
used to connect to the remote.
"""
def connect(user_name=SSHname,host=login_check(alias_result),password=SSHpassword):
    crt.Screen.Send("ssh " + user_name + "@" + host + "\r")
    if crt.Screen.WaitForString("yes", 6) == 1:
        crt.Screen.Send("yes\r")
    crt.Screen.WaitForString("password", 6)
    crt.Screen.Send(password + "\r")

"""
this method used to get the most frequent items.
"""
def most_frequent(List):
    return max(set(List), key=List.count)


def starter():
    if "10." not in ip:
        crt.Screen.Send("alias " + ip + "\r")
        alias_result = crt.Screen.ReadString("[")
        #crt.Dialog.MessageBox(str(alias_result))
        connect()
    else:
        crt.Dialog.MessageBox("this is an IP")
        crt.Screen.Send("ssh " + SSHname + "@" + ip + "\r")
        if crt.Screen.WaitForString("yes", 3) == 1:
            crt.Screen.Send("yes\r")
        crt.Screen.WaitForString("password", 3)
        crt.Screen.Send(SSHpassword + "\r")
"""
This is a simple method that change or replace the value of any string but return the string at the changed value only.
"""
def change_me(text,word,value):
    text = text.split()
    if type(word) is str:
        text = text.split()
        word = word.split()
    for i in range(len(word)):
        no = text.index(word[i]) + 1
        text.pop(no)
        text.insert(no,value[i])
    return " ".join(text)


"""
Huwai cabinet user configuration
"""
h_user_config = {

    "line_1":"service-port 208 vlan 1701 vdsl mode atm 0/4/16 vpi 0 vci 35 single-service tag-transform add-double inner-vlan 309 inbound traffic-table index 6 outbound  traffic-table index 6"
    ,"line_2":"service-port 1040 vlan 1701 vdsl mode ptm 0/4/16 tag-transform add-double inner-vlan 309 inbound traffic-table index 6 outbound traffic-table index 6"
}


"""
This method used to check the outer vlan and change it if there is any error. 
"""
def check_change_outer(outerVlan, userOuter):
    theOuterVlanOfPort = get_my_value(userOuter, "vlan")
    if outerVlan ==  theOuterVlanOfPort[0] and theOuterVlanOfPort[1] :
        crt.Dialog.MessageBox("Outer Matched")
    else:
        theNumOfServicePort = get_my_value(userOuter, "service-port")
        theInnerVlan = get_my_value(userOuter, "inner-vlan")
        if len(theNumOfServicePort) > 1 :
            crt.Screen.Send("undo service-port " + str(theNumOfServicePort[0]) + "\r")
            crt.Screen.Send("undo service-port " + str(theNumOfServicePort[1]) + "\r")

            portConfiguration = "service-port {service_port} vlan {outerVlan} vdsl mode atm {port} vpi 0 vci 35 single-service tag-transform add-double inner-vlan {innerVlan} inbound traffic-table index 6 outbound  traffic-table index 6".format(service_port = theNumOfServicePort[0], outerVlan = the_outer_vlan, port = card_port, innerVlan = theInnerVlan[0])
            portConfiguration1 = "service-port {servicePort} vlan {outervlan} vdsl mode ptm {portCard} tag-transform add-double inner-vlan {innervlan} inbound traffic-table index 6 outbound traffic-table index 6".format(servicePort = theNumOfServicePort[1], outervlan = the_outer_vlan, portCard = card_port, innervlan = theInnerVlan[1])
            crt.Screen.Send(portConfiguration + "\r")
            crt.Screen.Send(portConfiguration1 + "\r")
        elif len(theNumOfServicePort) == 1 :
            crt.Screen.Send("undo service-port " + str(theNumOfServicePort[0]) + "\r")
            portConfig = "service-port {x} vlan {y} adsl {z} vpi 0 vci 35 single-service tag-transform  add-double inner-vlan {a} inbound traffic-table index 6 outbound traffic-table  index 6".format(x = str(theNumOfServicePort[0]), y = the_outer_vlan, z = card_port, a = str(theInnerVlan[0]))
            crt.Screen.Send(portConfig + "\r")



"""
this method checks the customer configuration and change it if there is any wrong in his configuration
"""
def check_customer_configuration(customer_config):
    if the_outer_vlan == get_my_value(customer_config,"vlan")[0] and get_my_value(customer_config,"vlan")[1]:
        crt.Dialog.MessageBox("outer matched")
    else:
        #change the outer valn
        theNumOfServicePort = get_my_value(customer_config,"service-port")
        theInnerVlan = get_my_value(customer_config,"inner-vlan")
        if "atm" in customer_config:
            crt.Dialog.MessageBox(str('not matched'))
            send_only("undo service-port " + str(theNumOfServicePort[0])) # [0] is the first line (first service port)
            send_only(change_me(h_user_config['line_1'],['service-port','vlan','atm','inner-vlan'],[get_my_value(customer_config,'service-port')[0],the_outer_vlan
                ,card_port,get_my_value(customer_config,'inner-vlan')[0]]))

        elif "ptm" in customer_config:
            send_only("undo service-port " + str(theNumOfServicePort[0])) # [1] is the second line (second service port)
            send_only("undo service-port " + str(theNumOfServicePort[1]))
            send_only(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm', 'inner-vlan'],
                                [get_my_value(customer_config, 'service-port')[0], the_outer_vlan, card_port,
                                 get_my_value(customer_config, 'inner-vlan')[0]]))

            send_only(change_me(h_user_config['line_2'], ['service-port', 'vlan', 'ptm', 'inner-vlan'],
                                [get_my_value(customer_config, 'service-port')[1], the_outer_vlan, card_port,
                                 get_my_value(customer_config, 'inner-vlan')[1]]))


    #     else:  # there is no configuration
    #         send_only(change_me(h_user_config['line_1'],['service-port','vlan','atm','inner-vlan'],[max(get_my_value2(all_service_ports,'up','down'))+1,the_outer_vlan,card_port,]
    #
    # pass
    #




starter()
crt.Screen.WaitForString(">",3)
send_only("enable")
send_only("config")

### now get outer vlan
# returned list from command that list contains outer vlan as an element
send_only("scroll 512")
send_only("display service-port all"+ "\r\r\r\t\t\t\t\t\t\t\t")
all_service_ports = reader("Total")

ol_vlan = all_service_ports.split()
#crt.Dialog.MessageBox(str(ol_vlan))

r = re.compile("[4-4][0-9][0-9]")
new_list = list(filter(r.match, ol_vlan))

the_outer_vlan = most_frequent(new_list)
crt.Dialog.MessageBox(str(the_outer_vlan))
crt.Screen.WaitForString("Q",3)
send_only("Q")


# now get the customer configuration
send_only("display current-configuration port " + card_port)
customer_configuration = reader("return")

crt.Dialog.MessageBox(str(customer_configuration))

check_customer_configuration(customer_configuration)

#display current-configuration | include inner-vlan [number]

