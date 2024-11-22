import os
import csv
import subprocess
import time
import re
from twilio.rest import Client
from flask import Flask, render_template, request, redirect, url_for


twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')


twilio_number = ''  # 
to_number = '' 
# إعداد عميل Twilio
client = Client(account_sid, auth_token)

# قائمة الأجهزة المتصلة بالشبكة
devices = [
    {'ip': '192.168.1.2', 'device_name': 'Device1'},
    {'ip': '192.168.1.3', 'device_name': 'Device2'},
    {'ip': '192.168.1.4', 'device_name': 'Device3'}
]

# إعداد تطبيق Flask
app = Flask(__name__)

# دالة لفحص الاتصال باستخدام Ping وحساب وقت الاستجابة
def ping_device(ip, device_name):
    try:
        response = subprocess.run(['ping', '-n', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if response.returncode == 0:
            output = response.stdout.decode()
            match = re.search(r'time=(\d+)ms', output)
            if match:
                latency = match.group(1)
                save_data_to_csv(device_name, ip, latency)
                return True, latency
            else:
                save_data_to_csv(device_name, ip, "N/A")
                return True, "N/A"
        else:
            save_data_to_csv(device_name, ip, "Disconnected")
            return False, None
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        save_data_to_csv(device_name, ip, "Error")
        return False, None

# دالة لحفظ البيانات في ملف CSV
def save_data_to_csv(device_name, ip, latency):
    with open('network_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([device_name, ip, latency, time.strftime("%Y-%m-%d %H:%M:%S")])

# دالة لإرسال رسالة نصية عبر Twilio
def send_sms(message_body):
    try:
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=to_number
        )
        print(f"Message sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")

# دالة لطباعة حالة الشبكة وإرسال إشعار عند انقطاع الأجهزة
def print_network_status_and_notify():
    print("Network Devices Status:")
    for device in devices:
        ip = device['ip']
        device_name = device['device_name']
        is_connected, result = ping_device(ip, device_name)
        
        if is_connected:
            print(f"{device_name} ({ip}) is Connected. Latency: {result} ms")
        else:
            print(f"{device_name} ({ip}) is Disconnected")
            send_sms(f"ALERT: {device_name} with IP {ip} is disconnected from the network.")

# مراقبة الشبكة بشكل دوري
def monitor_network():
    print("Starting network monitoring...")
    while True:
        print_network_status_and_notify()
        time.sleep(5)

# دالة لقراءة البيانات من ملف CSV
def read_data_from_csv():
    if not os.path.exists('network_data.csv'):
        return []
    with open('network_data.csv', mode='r') as file:
        reader = csv.reader(file)
        return list(reader)

@app.route('/')
def index():
    data = read_data_from_csv()
    return render_template('index.html', data=data)

# صفحة الفلترة
@app.route('/filter_data', methods=['GET', 'POST'])
def filter_data():
    data = read_data_from_csv()

    if request.method == 'POST':
        filter_value = request.form.get('filter_value')
        if filter_value:
            filtered_data = [row for row in data if filter_value.lower() in str(row).lower()]
            return render_template('filter_data.html', data=filtered_data)
        else:
            return render_template('filter_data.html', data=data)
    
    return render_template('filter_data.html', data=data)

# صفحة إدارة الأجهزة
@app.route('/manage_devices', methods=['GET', 'POST'])
def manage_devices():
    global devices

    if request.method == 'POST':
        device_name = request.form.get('device_name')
        ip = request.form.get('ip')
        if device_name and ip:
            devices.append({'device_name': device_name, 'ip': ip})
            save_data_to_csv(device_name, ip, "N/A")  # حفظ البيانات في CSV
    
    return render_template('manage_devices.html', devices=devices)

# حذف جهاز
@app.route('/delete_device/<ip>', methods=['POST'])
def delete_device(ip):
    global devices
    devices = [device for device in devices if device['ip'] != ip]
    return redirect(url_for('manage_devices'))

if __name__ == "__main__":
    # تشغيل المراقبة في الخلفية
    import threading
    monitoring_thread = threading.Thread(target=monitor_network)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    # تشغيل تطبيق Flask
    app.run(debug=True, use_reloader=False)
