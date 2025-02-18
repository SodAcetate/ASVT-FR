import serial

class Com:
    def __init__(self, path):
        self.port = serial.Serial(path)
    def write(self, msg):   # Отправляет на порт набор байт, msg -- объект типа bytes
        self.port.write(msg)  
    def read_byte(self):    # Считывает один байт с порта
        byte = self.port.read()
        print(f"COM API: Read byte {byte}")
        return byte
    def read(self,term=None,length=None): # Считывает один байт с порта, либо пока не встретит term если term!=None, либо length байт если lenth!=None
        res = bytes()
        while True:
            last = self.read_byte()
            if term and int.from_bytes(last,'big')==term or length and len(res)==length or (not length and not term and res):
                break
            else:
                res += last
        return res

class Printer:
    def __init__(self, output_path):
        self.buffer = bytes()
        self.output_path = output_path
        self.ready_to_print = False
    
    def print_and_feed_line(self):
        with open(self.output_path, "a") as file:
            if not self.ready_to_print:
                file.write("<div class=receipt>\n")
                self.ready_to_print = True
            file.write(self.buffer.decode("utf-8"))
            file.write("\n<br>\n")
        self.buffer = bytes()

    def partial_cut(self):
        with open(self.output_path, "a") as file:
            if self.ready_to_print:
                file.write("</div>\n")
                self.ready_to_print = False
    def full_cut(self):
        with open(self.output_path, "a") as file:
            if self.ready_to_print:
                file.write("</div>\n")
                file.write("<br>\n")
                self.ready_to_print = False

class Interpreter:
    def __init__(self, com_path, print_path):
        self.cmds = bytes([
                        0x0a, #LF
                        0x0d, #CR
                        0x1b, #ESC
                        0x09, #HT
                        0x0c, #FF
                        0x18, #CAN
                        0x10, #DLE
                        0x1c, #FS
                        0x1d #GS
                    ])
        self.com = Com(com_path)
        self.printer = Printer(print_path)
    


    def interpret_cmd(self, cmd):
        print(f"INTERPRETER: Received cmd {cmd}")
        if cmd == b'\x1b': #ESC
            cmd_args = bytes()
            cmd_args += self.com.read_byte()
            print(f"ESC {bytes([cmd_args[0]])}")
            match cmd_args[0]:
                case 0x4a: # ESC J -- print and feed line
                    self.printer.print_and_feed_line()
                    print("Print and feed line")
                case 0x6D: # ESC m -- full cut
                    self.printer.full_cut()
                    print("Full cut\n")
                case 0x69: # ESC i -- partial cut
                    self.printer.partial_cut()
                    print("Partial cut")

    def read_and_interpret_byte(self):
        byte = self.com.read_byte()
        if byte in self.cmds:
            self.interpret_cmd(byte)
        else:
            self.printer.buffer += byte

    

App = Interpreter("/dev/pts/6", "example.html")

while True:
    App.read_and_interpret_byte()