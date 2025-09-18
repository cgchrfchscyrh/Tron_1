import json
import uuid
import threading
import time
import websocket
from datetime import datetime

# Replace this ACCID value with your robot's actual serial number (SN)
ACCID = "PF_TRON1A_260"

# Atomic flag for graceful exit
should_exit = False

# WebSocket client instance
ws_client = None

# 控制是否显示收到的消息 & 打印频率
show_messages = False
last_print_time = 0
print_interval = 5   # 默认每 5 秒打印一次

# Generate dynamic GUID
def generate_guid():
    return str(uuid.uuid4())

# Send WebSocket request with title and data
def send_request(title, data=None):
    if data is None:
        data = {}
    
    # Create message structure with necessary fields
    message = {
        "accid": ACCID,
        "title": title,
        "timestamp": int(time.time() * 1000),  # Current timestamp in milliseconds
        "guid": generate_guid(),
        "data": data
    }

    message_str = json.dumps(message)
    
    # Send the message through WebSocket if client is connected
    if ws_client:
        ws_client.send(message_str)

# Handle user commands
def handle_commands():
    global should_exit, show_messages, print_interval
    while not should_exit:
        command = input("Enter command ('stand', 'walk', 'twist', 'sit', 'stair', 'stop', 'imu', 'showmsg', 'setfreq') or 'exit' to quit:\n")
        
        if command == "exit":
            should_exit = True
            break
        elif command == "stand":
            send_request("request_stand_mode")
        elif command == "walk":
            send_request("request_walk_mode")
        elif command == "twist":
            x = float(input("Enter x value:"))
            y = float(input("Enter y value:"))
            z = float(input("Enter z value:"))
            for _ in range(30):
                send_request("request_twist", {"x": x, "y": y, "z": z})
                time.sleep(1/30)
        elif command == "sit":
            send_request("request_sitdown")
        elif command == "stair":
            enable = input("Enable stair mode (true/false):").strip().lower() == 'true'
            send_request("request_stair_mode", {"enable": enable})
        elif command == "stop":
            send_request("request_emgy_stop")
        elif command == "imu":
            enable = input("Enable IMU (true/false):").strip().lower() == 'true'
            send_request("request_enable_imu", {"enable": enable})
        elif command == "showmsg":
            option = input("Show messages? (on/off): ").strip().lower()
            if option == "on":
                show_messages = True
                print("✅ Message display enabled.")
            else:
                show_messages = False
                print("❌ Message display disabled.")
        elif command == "setfreq":
            try:
                interval = float(input("Enter print interval in seconds: "))
                if interval > 0:
                    print_interval = interval
                    print(f"✅ Message print interval set to {print_interval} seconds.")
                else:
                    print("⚠️ Interval must be > 0.")
            except ValueError:
                print("⚠️ Invalid input, please enter a number.")

# WebSocket on_open callback
def on_open(ws):
    print("Connected!")
    threading.Thread(target=handle_commands, daemon=True).start()

# WebSocket on_message callback
def on_message(ws, message):
    global ACCID, show_messages, last_print_time, print_interval
    root = json.loads(message)
    ACCID = root.get("accid", None)

    if show_messages:
        current_time = time.time()
        if current_time - last_print_time >= print_interval:
            print(f"Received message: {message}")
            last_print_time = current_time

# WebSocket on_close callback
def on_close(ws, close_status_code, close_msg):
    print("Connection closed.")

# Close WebSocket connection
def close_connection(ws):
    ws.close()

def main():
    global ws_client
    
    ws_client = websocket.WebSocketApp(
        "ws://10.192.1.2:5000",
        on_open=on_open,
        on_message=on_message,
        on_close=on_close
    )
    
    print("Press Ctrl+C to exit.")
    ws_client.run_forever()

if __name__ == "__main__":
    main()
