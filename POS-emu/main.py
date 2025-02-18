import tkinter as tk
import serial

class Com:
    def __init__(self, path):
        self.port = serial.Serial(path)
    def write(self, msg):   # Отправляет на порт набор байт, msg -- объект типа bytes
        self.port.write(msg)  
    def read_byte(self):    # Считывает один байт с порта
        return self.port.read()
    def read(self,term=None,length=None): # Считывает один байт с порта, либо пока не встретит term если term!=None, либо length байт если lenth!=None
        res = bytes()
        while True:
            last = self.read_byte()
            if term and int.from_bytes(last,'big')==term or length and len(res)==length or (not length and not term and res):
                break
            else:
                res += last
        return res
    

def int_to_bytes(i):
    len = (i.bit_length() + 7) // 8
    return(int(i).to_bytes(len,'big'))

class Message:
        def __init__(self, cmd,body=bytes()):
              self.cmd = int_to_bytes(cmd)
              self.body = body
              self.sent = False
              self.error_matrix = {
                     0x00: "Успех",
                     0x02: "Неверное состояние ФН",
                     0x03: "Ошибка ФН",
                     0x10: "Превышение размеров TLV данных"
                }
        # Функция для логирования ошибок
        def decode_error(self, error):
             return self.error_matrix[int.from_bytes(error,'little')]

        def send(self,com):
                com.write(self.cmd + self.body)
                print(self.cmd + self.body)
                response = com.read_byte()
                print(response)
                if response == self.cmd:
                        error = com.read_byte()
                        print(error)
                        print(self.decode_error(error))
                        return error
                else:
                        print(f"{self.cmd}: unexpected response")
                        return -1

class Terminal:
        def __init__(self,path):
                self.com = Com(path)
             
        # Функции протокола ККТ ------------------
        # Печать строки 17h
        def print(self, password, flag, string):
             if len(string) > 40:
                  string = string[:40]
             if len(string) < 40:
                  string += '\0'*(40-len(string))
             msg = Message(0x17,bytes(password + flag + string, 'utf-8'))
             error = msg.send(self.com)

        # Отрезать ленту 25h
        def cut(self, password, partial):
              cut_type = chr(0)
              if partial:
                    cut_type = chr(1)
              msg = Message(0x25, bytes(password + cut_type, 'utf-8')) 
              error = msg.send(self.com)     

        # Открытие чека 8dh
        def open_receipt(self, password, type): 
            msg = Message(0x8d, bytes(password + chr(type), 'utf-8')) 
              
             
        



t = Terminal('/dev/pts/5')
t.print('1234', '0' ,'helloworld')
t.cut('1234', False)
# while True:
#       t.com.write(int_to_bytes(0x17))



# root = tk.Tk()
# root.title("POS-emu")
# # root.geometry("512x512")

# sum_field = tk.Entry(root,width=40)
# sum_field.grid(row=0, column=0, columnspan=3)

# def digit_append(number):
#         current = sum_field.get()
#         if len(current)==0 and number==0:
#             return
#         sum_field.delete(0, tk.END)
#         sum_field.insert(0, str(current) + str(number))

# def digit_erase():
#         current = sum_field.get()
#         sum_field.delete(0, tk.END)
#         sum_field.insert(0, str(current)[:-1])

# # for i in range(3):
# #     for j in range(3):
# #         tk.Button(root, text=str(3*i+j+1),width=12,height=2,command=lambda: digit_append(3*i+j+1)).grid(column=j,row=i+1)
        
# tk.Button(root, text="1",width=12,height=2,command=lambda: digit_append(1)).grid(column=0,row=1)
# tk.Button(root, text="2",width=12,height=2,command=lambda: digit_append(2)).grid(column=1,row=1)
# tk.Button(root, text="3",width=12,height=2,command=lambda: digit_append(3)).grid(column=2,row=1)
# tk.Button(root, text="4",width=12,height=2,command=lambda: digit_append(4)).grid(column=0,row=2)
# tk.Button(root, text="5",width=12,height=2,command=lambda: digit_append(5)).grid(column=1,row=2)
# tk.Button(root, text="6",width=12,height=2,command=lambda: digit_append(6)).grid(column=2,row=2)
# tk.Button(root, text="7",width=12,height=2,command=lambda: digit_append(7)).grid(column=0,row=3)
# tk.Button(root, text="8",width=12,height=2,command=lambda: digit_append(8)).grid(column=1,row=3)
# tk.Button(root, text="9",width=12,height=2,command=lambda: digit_append(9)).grid(column=2,row=3)
# tk.Button(root, text="0",width=12,height=2,command=lambda: digit_append(0)).grid(column=1,row=4)
# tk.Button(root, text="<=",width=12,height=2,command=lambda: digit_erase()).grid(column=2,row=4)


# # btn_res = tk.Button(root, text ='Get Result')
# # btn_res.grid(column=0, row=2, pady=10, sticky=tk.W)

# # lbl_logo = tk.Label(root)

# # lbl_logo.grid(row=0, column=2,
# #               columnspan=2, rowspan=2,  # объединение ячеек.
# #               sticky=tk.W+tk.E+tk.N+tk.S,
# #               padx=5, pady=5)


# root.mainloop()