import cnc_machine

c = cnc_machine.CncMachine()
ip = c.ip
port = c.port
timeout = c.timeout

try:
    c.read_machineid()
    c.write_macro(500, 150)
    c.read_macro(500)
    c.read_statinfo()
finally:
    c.freelibhandle()
