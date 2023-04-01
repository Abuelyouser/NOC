

from netmiko import ConnectHandler

# creating a dictionary for the device to connect to
device = {
    'device_type': 'autodetect',
    'host': '10.50.138.58',
    'username': 'mostafa.h.mostafa',
    'password': 'Shemodesha-11',
    'port': 22,  # optional, default 22
    'secret': 'zxr10',  # this is enable password
    'fast_cli': False,

}

# connecting to the device and returning an ssh connection object
connection = ConnectHandler(**device)
print("Login Success!")

# sending a command and getting the output
connection.send_command('terminal length 0\n')
connection.send_command('configure terminal\n', cmd_verify=False, read_timeout=10, expect_string='#')
output = connection.send_command('show mac\n', cmd_verify=False, read_timeout=10)

print(output)
print("\n\n" " Port configuration is : \n")
output1 = connection.send_command('show running-config interface vdsl_1/19/28 \n', cmd_verify=False, read_timeout=10)
print(output1)
split=output1.split()
vlan=split[split.index("vlan")+1]
print("VLAN is : "+str(vlan))

output2 = connection.send_command('show card \n', cmd_verify=False, read_timeout=10)
print(output2)

# closing the connection
print('Closing connection')
connection.disconnect()
