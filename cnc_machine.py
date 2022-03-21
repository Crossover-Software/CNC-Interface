import ctypes
import os


class CncMachine:
    def __init__(self, ip="192.168.71.140", port=8193, timeout=10, libh=ctypes.c_ushort(0)):
        libpath = (
            os.path.join(os.getcwd(), "Fwlib64.dll")
        )
        self.focas = ctypes.cdll.LoadLibrary(libpath)
        # focas.cnc_startupprocess.restype = ctypes.c_short
        # focas.cnc_exitprocess.restype = ctypes.c_short
        self.focas.cnc_allclibhndl3.restype = ctypes.c_short
        self.focas.cnc_freelibhndl.restype = ctypes.c_short
        self.focas.cnc_rdcncid.restype = ctypes.c_short
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.libh = libh

    def get_focas(self):
        return self.focas

    def get_port(self):
        return self.port

    def get_timeout(self):
        return self.timeout

    def get_libh(self):
        return self.libh

    def get_ip(self):
        return self.ip

    def set_ip(self, newip):
        self.ip = newip

    def set_timeout(self, newtimeout):
        self.timeout = newtimeout

    def set_port(self, newport):
        self.port = newport

    def establish_connection(self, ip, port, timeout, libh, focas):
        print(f"connecting to machine at {ip}:{port}...")
        ret = focas.cnc_allclibhndl3(
            ip.encode(),
            port,
            timeout,
            ctypes.byref(libh),
        )
        if ret != 0:
            raise Exception(f"Failed to connect to cnc! ({ret})")

    def read_machineid(self, focas, libh):
        # read machine id
        cnc_ids = (ctypes.c_uint32 * 4)()
        ret = focas.cnc_rdcncid(libh, cnc_ids)
        if ret != 0:
            raise Exception(f"Failed to read cnc id! ({ret})")

        machine_id = "-".join([f"{cnc_ids[i]:08x}" for i in range(4)])
        print(f"machine_id={machine_id}")

    def write_macro(self, focas, libh, macroid, macroval):
        # write macrovar
        macrovarid = macroid  # Specify the custom macro variable number.
        length = 10  # standaard 10
        macrovarval = macroval  # Specify the value of variable/numerical part of variable.
        macrovardec = 0  # Specify the number of places of decimals/exponent part of variable.
        ret = focas.cnc_wrmacro(libh, macrovarid, length, macrovarval, macrovardec)
        if ret != 0:
            raise Exception(f"Failed to write cnc macrovar! ({ret})")
        print("macrovar written succesfully!")

    def read_macro(self, focas, libh, macroid):
        # read macrovar
        class ODBM(ctypes.Structure):
            _fields_ = [("datano", ctypes.c_short),
                        ("dummy", ctypes.c_short),
                        ("mcr_val", ctypes.c_long),
                        ("dec_val", ctypes.c_short)]

        odbm = ODBM()
        # param 1 = libhandle, param2 = macrovarid, param3 = length, param4 = returnval
        ret = focas.cnc_rdmacro(libh, macroid, 10, ctypes.byref(odbm))
        if ret != 0:
            raise Exception(f"Failed to read macro variable! ({ret})")

        divider = 10 ** (odbm.dec_val)
        print(odbm.mcr_val / divider)
        # end read macrovar

    def read_statinfo(self, focas, libh):
        # read statinfo
        print("********START STAT-INFO********")
        cnc_statinfo = (ctypes.c_uint32 * 8)()
        ret = focas.cnc_statinfo(libh, cnc_statinfo)
        if ret != 0:
            raise Exception(f"Failed to read macro variable! ({ret})")

        print(f"dummy={cnc_statinfo[0]:01x}")

        # checks for AUTOMATIC/MANUAL mode selection (short aut in docs)
        if cnc_statinfo[1] == 0:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: MDI")
        elif cnc_statinfo[1] == 1:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: MEM")
        elif cnc_statinfo[1] == 3:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: EDT")
        elif cnc_statinfo[1] == 4:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: HAND")
        elif cnc_statinfo[1] == 5:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: JOG")
        elif cnc_statinfo[1] == 10:
            print(f"AUTOMATIC/MANUAL mode selection= {cnc_statinfo[1]:01x}: TAPE")

        # checks for status of automatic operation (short run in docs)
        if cnc_statinfo[2] == 0:
            print(f"status of automatic operation= {cnc_statinfo[2]:01x}: NOT READY")
        elif cnc_statinfo[2] == 1:
            print(f"status of automatic operation= {cnc_statinfo[2]:01x}: M-READY")
        elif cnc_statinfo[2] == 2:
            print(f"status of automatic operation= {cnc_statinfo[2]:01x}: C-START")
        elif cnc_statinfo[2] == 3:
            print(f"status of automatic operation= {cnc_statinfo[2]:01x}: F-HOLD")
        elif cnc_statinfo[2] == 4:
            print(f"status of automatic operation= {cnc_statinfo[2]:01x}: B-STOP")

        # checks for status of axis movement, dwell (short motion in docs)
        if cnc_statinfo[3] == 0:
            print(f"status of axis movement, dwell= {cnc_statinfo[3]:01x}: ****")
        elif cnc_statinfo[3] == 1:
            print(f"status of axis movement, dwell= {cnc_statinfo[3]:01x}: CMTN")
        elif cnc_statinfo[3] == 2:
            print(f"status of axis movement, dwell= {cnc_statinfo[3]:01x}: CDWL")

        # checks for status of M,S,T,B function (short mstb in docs)
        if cnc_statinfo[4] == 0:
            print(f"status of M,S,T,B function= {cnc_statinfo[4]:01x}: ****")
        elif cnc_statinfo[4] == 1:
            print(f"status of M,S,T,B function= {cnc_statinfo[4]:01x}: CFIN")

        # NOT USED checks for status of emergency (short emergency in docs)
        print(f"NOT USED: emergency status={cnc_statinfo[5]:01x}")

        # checks for status of alarm (short alarm in docs)
        if cnc_statinfo[6] == 0:
            print(f"status of alarm= {cnc_statinfo[6]:01x}: ****(Not emergency)")
        elif cnc_statinfo[6] == 1:
            print(f"status of alarm= {cnc_statinfo[6]:01x}: ALARM")
        elif cnc_statinfo[6] == 2:
            print(f"status of alarm= {cnc_statinfo[6]:01x}: BATTERY LOW")

        # checks for status of edit (short edit in docs)
        if cnc_statinfo[7] == 0:
            print(f"status of edit= {cnc_statinfo[7]:01x}: ****(Not editing)")
        elif cnc_statinfo[7] == 1:
            print(f"status of edit= {cnc_statinfo[7]:01x}: EDITING(during search)")
        elif cnc_statinfo[7] == 2:
            print(f"status of edit= {cnc_statinfo[7]:01x}: SEARCH(during search)")
        elif cnc_statinfo[7] == 3:
            print(f"status of edit= {cnc_statinfo[7]:01x}: RESTART(during restart)")
        elif cnc_statinfo[7] == 4:
            print(f"status of edit= {cnc_statinfo[7]:01x}: RETRACE(during retrace)")
        print("********END STAT-INFO********")

    def freelibhandle(self, focas, libh):
        ret = focas.cnc_freelibhndl(libh)
        if ret != 0:
            raise Exception(f"Failed to free library handle! ({ret})")

# focas.cnc_exitprocess()
