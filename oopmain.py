import cnc_machine

c = cnc_machine.CncMachine()
ip = c.ip
port = c.port
libh = c.libh
timeout = c.timeout
focas = c.focas

try:
    c.establish_connection(ip, port, timeout, libh, focas)
    c.read_machineid(focas, libh)
    c.write_macro(focas, libh, 500, 150)
    c.read_macro(focas, libh, 500)
    c.read_statinfo(focas, libh)
finally:
    c.freelibhandle(focas, libh)
