from napalm import get_network_driver

driver = get_network_driver('ios')
device = driver(10'1'1'11', 'ccnp', 'cisco')
device.open()

config = device.get_config()

device.close()

print(config)




from napalm import get_network_driver
driver = get_network_driver('ios')
device = driver(nostname='10.1.1.11', username='ccnp', password='cisco')
device.open()
interface = device.get_interfaces()
print (interface)
device.close()


