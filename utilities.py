import time
import sqlite3
import struct
import datetime
import requests
import pandas as pd
from pyrf24 import *

class RF_recevier:
    # initialization
    def __init__(self, CSN_PIN=0, CE_PIN=22, address=[b"1Node", b"2Node"]) -> None:
        self.radio = RF24(CE_PIN, CSN_PIN)
        self.address = address

        if not self.radio.begin():
            raise RuntimeError("radio hardware is not responding")
        
        self.radio.setPALevel(RF24_PA_LOW)
        self.radio.payload_size = struct.calcsize("fff")
        
        for pipe_n, addr in enumerate(self.address):
            self.radio.openReadingPipe(pipe_n, addr)

    # read the data from pipeline
    def read_data(self):
        has_payload, pipe_number = self.radio.available_pipe()
        # if there is data, then we receive it, or the function will return None

        if has_payload:
            buffer = self.radio.read(self.radio.payload_size)
        else:
            return pipe_number, None

        unpacked_data = struct.unpack("<fff", buffer) # Data dictionary

        print(
            f"Received {self.radio.payloadSize} bytes on pipe {pipe_number}:",
            f"The data received:\n {unpacked_data} "
        )

        return pipe_number, unpacked_data
      
    def receive_data(self,timeout=30):
        self.radio.startListening()
        start_timer = time.monotonic()

        while(time.monotonic() - start_timer) < timeout:
            pipe_number, unpacked_data = self.read_data()
            if(unpacked_data == None):
                continue
            
            time_now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            return pipe_number, time_now, unpacked_data
        print(f"Nothing received in {timeout} seconds.")
        return None, None, None


    def listen(self, timeout=1.0):
        
        data = {
        "Pipe_n": None,
        "Time": None,
        "DisplayTime": None,
        "Conductivity": None,
        "Level": None,
        "Turbidity": None
        }
        
        flag = 0
        for _ in range(len(self.address)):
            pipe_number, time_now, unpacked_data = self.receive_data(timeout)
            if time_now == None:
                continue
                
            flag = 1
            
            data["Pipe_n"] = pipe_number
            data["Time"] = time_now
            data["Conductivity"] = round(unpacked_data[0], 2)
            data["Level"] = round(unpacked_data[1],2 )
            # if unpacked_data[1] <= 0.0:
            #     data["Turbidity"] = float(0.0)
            # else:
            data["Turbidity"] = round(unpacked_data[2], 2)
        
        server_url = f"http://localhost:5000/api/data/insert"
        if flag:
            response = requests.post(server_url, json=data)
            if response.status_code == 200:
                print("Data posted successfully: ", response.json())
            else:
                print("Failed to post: ", response.status_code, response.text)
            
                    
        
        self.radio.stopListening()
