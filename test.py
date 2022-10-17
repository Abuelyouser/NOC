#final test: the inner vlan not worked yet.


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
this method works with get_my_value() method but it takes two marks. we use it to get the last service-port used in cabinet configuratin
and after knowing this service-port we add one to it and then we have a new service-port not repeated. 
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


def change_me(text,word,value):
    text = text.split()
    #result = []
    if type(word) is str:
        text = text.split()
        word = word.split()
    for i in range(len(word)):
        no = text.index(word[i]) + 1
        text.pop(no)
        text.insert(no,value[i])
        #result += text[no-1:no+1]
    return " ".join(text)



h_user_config = {
    "line_1":"service-port 208 vlan 1701 vdsl mode atm 0/4/16 vpi 0 vci 35 single-service tag-transform add-double inner-vlan 309 inbound traffic-table index 6 outbound  traffic-table index 6"
    ,"line_2":"service-port 1040 vlan 1701 vdsl mode ptm 0/4/16 tag-transform add-double inner-vlan 309 inbound traffic-table index 6 outbound traffic-table index 6"
    ,"line_3":"mac-address max-mac-count service-port 208 1"
}

s = "[vdsl]\
  <vdsl-0/14>\
 interface vdsl 0/14\
 deactivate 17\
 activate 17 prof-idx us-rate 87 ds-rate 26 spectrum 2 upbo 2 noise-margin 4\
inp-delay 7 \
#\
[bbs-config]\
  <bbs-config>\
 service-port 545 vlan 480 mohamed 22 vdsl mode atm  0/14/17 vpi 0 vci 35 single-service\
tag-transform add-double inner-vlan 1181 inbound traffic-table index 6 outbound traffic-table index \
\
service-port 1317 vlan 54 vdsl mode ptm  0/14/17 tag-transform add-double \
inner-vlan 2118 asd 3333 inbound traffic-table index 6 service-port 27 outbound traffic-table index 6 \
  mac-address max-mac-count service-port 208 1 \
  mac-address max-mac-count service-port 208 1 \
  return"

ja = " INDEX VLAN VLAN     PORT F/ S/ P VPI  VCI   FLOW  FLOW       RX   TX   STATE " \
     "ID   ATTR     TYPE                    TYPE  PARA" \
     "-----------------------------------------------------------------------------" \
     "0  402 stacking adl  0/12/0  0    35    -     -          6    6    down " \
     "1  402 stacking vdl  0/8 /0  0    35    -     -          6    6    down " \
     "2  402 stacking adl  0/12/2  0    35    -     -          6    6    down " \
     "3  402 stacking adl  0/12/3  0    35    -     -          6    6    up   " \
     "4 1701 stacking adl  0/12/4  0    35    -     -          6    6    down " \
     "5  402 stacking adl  0/12/5  0    35    -     -          6    6    down " \
     "6  402 stacking adl  0/12/6  0    35    -     -          6    6    down " \
     "7  402 stacking vdl  0/8 /1  0    35    -     -          6    6    up   " \
     "9  402 stacking vdl  0/8 /2  0    35    -     -          6    6    down " \
     "10  402 stacking adl  0/12/10 0    35    -     -         6    6    up" \
     " 11"

# s = "service-port 545 vlan 1710 mohamed 22 vdsl mode atm  0/14/17 vpi 0 vci 35 single-service \
#  tag-transform add-double inner-vlan 1181 inbound traffic-table index 6 outbound traffic-table index"
s = "adsl"

the_outer_vlan = "480"
card_port = "0/4/14"

def check_customer_configuration(customer_config):
    theNumOfServicePort = get_my_value(customer_config, "service-port")
    the_inner_vlan = get_my_value(customer_config, "inner-vlan")
    vlan_from_user_config = get_my_value(customer_config,'vlan')
    the_last_service_port = max(get_my_value2(ja, 'up', 'down'))   # ja is the output from display service-port all

    if len(vlan_from_user_config) == 2 :
        if the_outer_vlan == vlan_from_user_config[0] and the_outer_vlan == vlan_from_user_config[1]:
            print ("outer matched")
            print (vlan_from_user_config)

        elif the_outer_vlan != vlan_from_user_config[0] and the_outer_vlan != vlan_from_user_config[1]:
            print('not matched the two vlans are not equal the outer valn')
            print("undo service-port " + str(theNumOfServicePort[0]))
            print(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm', 'inner-vlan'],
                            [theNumOfServicePort[0], the_outer_vlan, card_port,
                             the_inner_vlan[0]]))
            print("undo service-port " + str(theNumOfServicePort[1]))  # [1] is the second line (second service port)
            print(change_me(h_user_config['line_2'], ['service-port', 'vlan', 'ptm', 'inner-vlan'],
                            [theNumOfServicePort[1], the_outer_vlan, card_port,
                             the_inner_vlan[1]]))
        else:
            #change the outer valn
            if "vdsl" in customer_config:
                if get_my_value(customer_config,"vlan")[1] != the_outer_vlan:
                    print("undo service-port " + str(theNumOfServicePort[1])) # [1] is the second line (second service port)
                    print(change_me(h_user_config['line_2'], ['service-port', 'vlan', 'ptm', 'inner-vlan'],
                                    [theNumOfServicePort[1], the_outer_vlan, card_port,
                                     the_inner_vlan[1]]))
                elif get_my_value(customer_config,"vlan")[0] != the_outer_vlan:
                    print("undo service-port " + str(theNumOfServicePort[0]))
                    print(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm', 'inner-vlan'],
                                    [theNumOfServicePort[0], the_outer_vlan, card_port,
                                     the_inner_vlan[0]]))
            elif "adsl" in customer_config:
                print('atm!')
                print("undo service-port " + str(theNumOfServicePort[0])) # [0] is the first line (first service port)
                print(change_me(h_user_config['line_1'],['service-port','vlan','atm','inner-vlan'],[theNumOfServicePort[0],the_outer_vlan
                    ,card_port,the_inner_vlan[0]]))
    elif len(vlan_from_user_config) == 1:
        if the_outer_vlan not in vlan_from_user_config:
            if "vdsl" in customer_config:
                print('not matched in ptm')
                print("undo service-port " + str(theNumOfServicePort[0])) # [1] is the second line (second service port)
                print(change_me(h_user_config['line_2'], ['service-port', 'vlan', 'ptm', 'inner-vlan'],
                                    [theNumOfServicePort[0], the_outer_vlan, card_port,
                                     the_inner_vlan[0]]))

                print(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm', 'inner-vlan'],
                                [str(the_last_service_port + 1), the_outer_vlan, card_port,
                                 the_inner_vlan[0]]))

            elif "adsl" in customer_config:
                print('atm!')
                print("undo service-port " + str(theNumOfServicePort[0])) # [0] is the first line (first service port)
                print(change_me(h_user_config['line_1'],['service-port','vlan','atm','inner-vlan'],[theNumOfServicePort[0],the_outer_vlan
                    ,card_port,the_inner_vlan[0]]))

    else:
        print('not atm (adsl) nor ptm(vdsl)!')
        # this just a test we get the inner valn with other method
        if "vdsl" in customer_config:
            print(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm'],
                            [str(the_last_service_port+1), the_outer_vlan, card_port,
                             ]))   ######################################### note that inner- vlan not handeled yet
            print(change_me(h_user_config['line_2'], ['service-port', 'vlan', 'ptm'],
                                [str(the_last_service_port+2), the_outer_vlan, card_port]))
        elif "adsl" in customer_config:
            print('no config adsl only')
            print(change_me(h_user_config['line_1'], ['service-port', 'vlan', 'atm'],
                            [str(the_last_service_port+1), the_outer_vlan, card_port,
                             ]))




# print(change_me(h_user_config['line_1'],['vlan','inner-vlan'],['878787','448gfh7']))
# print(change_me(h_user_config['line_1'],['service-port','atm','vlan','inner-vlan'],[get_my_value(s,'service-port')[0],card_port,get_my_value(s,'vlan')[0],get_my_value(s,'inner-vlan')[0]]))


print(check_customer_configuration(s))
