from napalm import get_network_driver

driver = get_network_driver('ios')
device = driver(10'1'1'11', 'ccnp', 'cisco')
device.open()

config = device.get_config()

device.close()

print(config)
