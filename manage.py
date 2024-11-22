from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy device data (you can replace it with a database in the future)
devices = [
    {'id': 1, 'name': 'Device 1', 'ip': '192.168.1.10', 'status': 'active'},
    {'id': 2, 'name': 'Device 2', 'ip': '192.168.1.20', 'status': 'inactive'},
]

# Home route
@app.route('/')
def home():
    return redirect(url_for('manage_devices'))

# Manage devices route
@app.route('/manage_devices', methods=['GET', 'POST'])
def manage_devices():
    if request.method == 'POST':
        # Handling the form to add a new device
        name = request.form['name']
        ip = request.form['ip']
        status = request.form['status']
        
        # Generate a new ID (In real-world cases, this will come from the database)
        new_id = len(devices) + 1
        devices.append({'id': new_id, 'name': name, 'ip': ip, 'status': status})
        
        return redirect(url_for('manage_devices'))
    
    return render_template('manage_devices.html', devices=devices)

# Route to delete a device
@app.route('/delete_device/<int:device_id>', methods=['GET'])
def delete_device(device_id):
    # Find the device by ID and remove it
    global devices
    devices = [device for device in devices if device['id'] != device_id]
    return redirect(url_for('manage_devices'))

@app.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = next((d for d in devices if d['id'] == device_id), None)
    if not device:
        return "Device not found", 404

    if request.method == 'POST':
        device['name'] = request.form['name']
        device['ip'] = request.form['ip']
        device['status'] = request.form['status']
        return redirect(url_for('manage_devices'))

    return render_template('edit_device.html', device=device)


if __name__ == '__main__':
    app.run(debug=True)
