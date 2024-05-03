from netmiko import ConnectHandler

cisco_device = {
    'device_type': 'cisco_ios',  # 장비 타입
    'host': '10.1.1.21',      # 장비의 IP 주소
    'username': 'ccnp',         # 로그인 유저 이름
    'password': 'cisco',  # 로그인 패스워드
}

net_connect = ConnectHandler(**cisco_device)

output = net_connect.send_command('show ip int brief')
print(output)

config_commands = [
    'interface loopback0',
    'ip address 1.1.1.1 255.255.255.0',
]
output = net_connect.send_config_set(config_commands)
print(output)
output = net_connect.send_command('show ip int brief')
print(output)

net_connect.disconnect()
