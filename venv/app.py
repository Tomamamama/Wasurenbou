from flask import Flask, jsonify, request, render_template, redirect, url_for
import asyncio
from bleak import BleakScanner
from supabase import create_client, Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Supabaseの初期化
supabase_url = "https://nnomgnwlsgnundohnpdm.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ub21nbndsc2dudW5kb2hucGRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI1MjU3NDUsImV4cCI6MjAzODEwMTc0NX0.Ss_GMgsz-MLGFuMEQBLSnfHi4wWlgeAjoRqWfeX8CdQ"
supabase: Client = create_client(supabase_url, supabase_key)

# Bluetooth信号強度の計算
def calculate_distance(rssi, A=-50, n=2):
    return 10 ** ((A - rssi) / (10 * n))

# Bluetooth信号強度の取得
async def get_bluetooth_signal_strength(target_device):
    devices = await BleakScanner.discover()
    device_signal_data = {}
    
    for device in devices:
        if device.address == target_device:
            try:
                signal_strength = device.rssi  # 信号強度（dBm）を取得
                distance = calculate_distance(signal_strength)  # 距離を計算
                device_signal_data[device.address] = {
                    'rssi': signal_strength,
                    'distance': distance
                }
                print(f"Device found: {device.address} with RSSI {signal_strength}")
            except Exception as e:
                device_signal_data[device.address] = str(e)
            break
    if not device_signal_data:
        print(f"No devices found matching the address {target_device}")
    
    return device_signal_data

def fetch_signal_strengths(target_device):
    return asyncio.run(get_bluetooth_signal_strength(target_device))

# Bluetooth情報の取得ルート
@app.route('/bluetooth', methods=['GET'])
def bluetooth_info():
    return render_template('bluetooth.html')

# Bluetoothデータの取得ルート
@app.route('/bluetooth_data', methods=['POST'])
def bluetooth_data():
    data = request.json
    device_address = data.get('mac_address')
    signal_strengths = fetch_signal_strengths(device_address)
    
    if signal_strengths:
        # Supabaseにデバイス情報を保存
        db_data = {
            "user_name": data.get('user_name'),
            "mac_address": device_address
        }
        response = supabase.table("Bluetooth").insert(db_data).execute()
    else:
        print("No signal strengths found to save to the database")
    
    return jsonify(signal_strengths)

# Bluetoothデバイスリストの取得ルート
@app.route('/devices', methods=['GET'])
def devices():
    devices = supabase.table("Bluetooth").select("*").execute()
    return jsonify(devices.data)

@app.route('/')
def root():
    return redirect(url_for('bluetooth_info'))

if __name__ == '__main__':
    app.run(debug=True)