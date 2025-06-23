import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
import json
import eventlet
import ssl

eventlet.monkey_patch()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Database Configuration - UPDATE THESE WITH YOUR CREDENTIALS
db_config = {
    'host': 'localhost',  
    'user': 'root',
    'password': 'password',
    'database': 'greenhouse_monitor',
    'autocommit': True,
    'connect_timeout': 5  # 5 second timeout
}

# db_config = {
#     'host': 'procodex.mysql.pythonanywhere-services.com',  
#     'user': 'procodex',
#     'password': 'QQ99XBCDL',
#     'database': 'procodex$default',
#     'autocommit': True,
#     'connect_timeout': 5  # 5 second timeout
# }


# # HiveMQ Cloud Configuration - UPDATE THESE
# HIVEMQ_URL = "fee58338fdf74c2ca59bc0a0d5bf477c.s1.eu.hivemq.cloud"
# HIVEMQ_PORT = 8883
# HIVEMQ_USER = "pasindu"
# HIVEMQ_PASS = "Pasindu1234"

# HiveMQ Cloud Configuration - UPDATE THESE
HIVEMQ_URL = "6da50eee270d490d86688a1ad70aa6dc.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
HIVEMQ_USER = "AgroSphere"
HIVEMQ_PASS = "AgroSpherex3421"

# Track last sensor values and tank levels
last_sensor_values = {}
last_tank_levels = {}
last_secondary_tank_levels = {}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"MySQL Connection Error: {e}")
    return None

def hash_password(password):
    # Better password hashing with salt
    salt = "greenhouse_system_2025"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def validate_login(username, password):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user['id'] if user and user['password_hash'] == hash_password(password) else False
    except Error as e:
        print(f"Login Error: {e}")
        return False
    finally:
        if conn.is_connected():
            conn.close()

def get_user_devices(user_id):
    """Simplified query to avoid SQL errors"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get basic device info
        cursor.execute("SELECT id, device_id, device_name FROM devices WHERE user_id = %s", (user_id,))
        devices = cursor.fetchall()
        
        # Get latest readings for each device
        for device in devices:
            # Get latest LED state
            cursor.execute("""
                SELECT new_state FROM led_changes 
                WHERE device_id = %s 
                ORDER BY changed_at DESC LIMIT 1
            """, (device['device_id'],))
            led_state = cursor.fetchone()
            device['led_state'] = led_state['new_state'] if led_state else False
            
            # Get latest main tank level
            cursor.execute("""
                SELECT level FROM tank_levels 
                WHERE device_id = %s 
                ORDER BY recorded_at DESC LIMIT 1
            """, (device['device_id'],))
            tank_level = cursor.fetchone()
            device['tank_level'] = tank_level['level'] if tank_level else 0
            
            # Get latest secondary tank level
            cursor.execute("""
                SELECT level FROM secondary_tank_levels 
                WHERE device_id = %s 
                ORDER BY recorded_at DESC LIMIT 1
            """, (device['device_id'],))
            secondary_tank_level = cursor.fetchone()
            device['secondary_tank_level'] = secondary_tank_level['level'] if secondary_tank_level else 0
        
        return devices
    except Error as e:
        print(f"Devices Query Error: {e}")
        return []
    finally:
        if conn.is_connected():
            conn.close()

def record_sensor_reading(device_id, value):
    """Only record if value changed significantly"""
    threshold = 5.0
    last_value = last_sensor_values.get(device_id)
    
    if last_value is None or abs(value - last_value) >= threshold:
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_readings (device_id, value)
                VALUES (%s, %s)
            """, (device_id, float(value)))
            conn.commit()
            last_sensor_values[device_id] = value
        except Error as e:
            print(f"Sensor Recording Error: {e}")
        finally:
            if conn.is_connected():
                conn.close()

def record_led_change(device_id, new_state):
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO led_changes (device_id, new_state)
            VALUES (%s, %s)
        """, (device_id, bool(new_state)))
        conn.commit()
    except Error as e:
        print(f"LED Recording Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

def record_tank_level(device_id, level):
    """Record tank level if it changed significantly"""
    threshold = 2.0  # 2% change threshold
    last_level = last_tank_levels.get(device_id)
    
    if last_level is None or abs(level - last_level) >= threshold:
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tank_levels (device_id, level)
                VALUES (%s, %s)
            """, (device_id, float(level)))
            conn.commit()
            last_tank_levels[device_id] = level
        except Error as e:
            print(f"Tank Level Recording Error: {e}")
        finally:
            if conn.is_connected():
                conn.close()

def record_secondary_tank_level(device_id, level):
    """Record secondary tank level if it changed significantly"""
    threshold = 2.0  # 2% change threshold
    last_level = last_secondary_tank_levels.get(device_id)
    
    if last_level is None or abs(level - last_level) >= threshold:
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO secondary_tank_levels (device_id, level)
                VALUES (%s, %s)
            """, (device_id, float(level)))
            conn.commit()
            last_secondary_tank_levels[device_id] = level
        except Error as e:
            print(f"Secondary Tank Level Recording Error: {e}")
        finally:
            if conn.is_connected():
                conn.close()

# MQTT Setup
try:
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
    mqtt_client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
    mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    mqtt_client.tls_insecure_set(True)
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connected!")
            client.subscribe("greenhouse/+/+/led/status")
            client.subscribe("greenhouse/+/+/tank/level")
            client.subscribe("greenhouse/+/+/secondary-tank/level")
        else:
            print(f"MQTT Connection Failed: {rc}")
    
    def on_message(client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) < 4:
                return
                
            username = topic_parts[1]
            device_id = topic_parts[2]
            msg_type = topic_parts[3]
            
            payload = msg.payload.decode()
            
            if msg_type == "led" and topic_parts[4] == "status":
                new_state = payload == "ON"
                record_led_change(device_id, new_state)
                socketio.emit('led_status_update', {
                    'device_id': device_id,
                    'status': new_state,
                    'timestamp': datetime.now().isoformat()
                }, room=username)
                
            elif msg_type == "tank" and topic_parts[4] == "level":
                level = float(payload)
                record_tank_level(device_id, level)
                socketio.emit('tank_level_update', {
                    'device_id': device_id,
                    'level': level,
                    'timestamp': datetime.now().isoformat()
                }, room=username)
                
            elif msg_type == "secondary-tank" and topic_parts[4] == "level":
                level = float(payload)
                record_secondary_tank_level(device_id, level)
                socketio.emit('secondary_tank_level_update', {
                    'device_id': device_id,
                    'level': level,
                    'timestamp': datetime.now().isoformat()
                }, room=username)
                
        except Exception as e:
            print(f"MQTT Message Error: {e}")
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(HIVEMQ_URL, HIVEMQ_PORT, 60)
    mqtt_client.loop_start()
    
except Exception as e:
    print(f"MQTT Initialization Failed: {e}")
    mqtt_client = None

# Flask Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    devices = get_user_devices(session['user_id'])
    return render_template('index.html', devices=devices)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        
        if not username or not password:
            if request.is_json:
                return jsonify({'message': 'Please enter both username and password'}), 400
            flash('Please enter both username and password', 'danger')
            return redirect(url_for('login'))
        
        user_id = validate_login(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            if request.is_json:
                return jsonify({'message': 'Login successful!'}), 200
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'message': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        
        if len(username) < 4 or len(password) < 6:
            if request.is_json:
                return jsonify({'message': 'Username (4+ chars) and password (6+ chars) required'}), 400
            flash('Username (4+ chars) and password (6+ chars) required', 'danger')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        if not conn:
            if request.is_json:
                return jsonify({'message': 'Database error. Try again later.'}), 500
            flash('Database error. Try again later.', 'danger')
            return redirect(url_for('register'))
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                if request.is_json:
                    return jsonify({'message': 'Username already exists'}), 400
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hash_password(password))
            )
            conn.commit()
            
            if request.is_json:
                return jsonify({'message': 'Registration successful! Please login.'}), 201
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            if request.is_json:
                return jsonify({'message': 'Registration failed. Please try again.'}), 500
            flash('Registration failed. Please try again.', 'danger')
            print(f"Registration Error: {e}")
        finally:
            if conn.is_connected():
                conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/add_device', methods=['POST'])
def add_device():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    device_id = request.form.get('device_id', '').strip()
    device_name = request.form.get('device_name', '').strip()
    
    if not device_id or not device_name:
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM devices WHERE device_id = %s", (device_id,))
        if cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Device ID exists'}), 400
        
        cursor.execute("""
            INSERT INTO devices (user_id, device_id, device_name)
            VALUES (%s, %s, %s)
        """, (session['user_id'], device_id, device_name))
        conn.commit()
        
        return jsonify({
            'status': 'success',
            'device': {
                'id': cursor.lastrowid,
                'device_id': device_id,
                'device_name': device_name
            }
        })
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    finally:
        if conn.is_connected():
            conn.close()

@app.route('/control_led', methods=['POST'])
def control_led():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    device_id = request.json.get('device_id')
    state = request.json.get('state')
    
    if not device_id or state is None:
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    if not mqtt_client or not mqtt_client.is_connected():
        return jsonify({'status': 'error', 'message': 'MQTT not connected'}), 503
    
    try:
        topic = f"greenhouse/{session['username']}/{device_id}/led/control"
        mqtt_client.publish(topic, "ON" if state else "OFF", qos=1)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_sensor_history/<device_id>')
def get_sensor_history(device_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT value, recorded_at 
            FROM sensor_readings 
            WHERE device_id = %s 
            ORDER BY recorded_at DESC 
            LIMIT 100
        """, (device_id,))
        
        readings = []
        for row in cursor:
            readings.append({
                'value': row['value'],
                'recorded_at': row['recorded_at'].isoformat() if row['recorded_at'] else None
            })
        
        return jsonify({'status': 'success', 'readings': readings})
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            conn.close()

@app.route('/get_tank_history/<device_id>')
def get_tank_history(device_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get main tank readings
        cursor.execute("""
            SELECT level as main_level, recorded_at 
            FROM tank_levels 
            WHERE device_id = %s 
            ORDER BY recorded_at DESC 
            LIMIT 100
        """, (device_id,))
        main_readings = cursor.fetchall()
        
        # Get secondary tank readings
        cursor.execute("""
            SELECT level as secondary_level, recorded_at 
            FROM secondary_tank_levels 
            WHERE device_id = %s 
            ORDER BY recorded_at DESC 
            LIMIT 100
        """, (device_id,))
        secondary_readings = cursor.fetchall()
        
        # Combine readings
        readings = []
        for i in range(max(len(main_readings), len(secondary_readings))):
            reading = {
                'recorded_at': None,
                'main_level': 0,
                'secondary_level': 0
            }
            
            if i < len(main_readings):
                reading['recorded_at'] = main_readings[i]['recorded_at']
                reading['main_level'] = main_readings[i]['main_level']
            
            if i < len(secondary_readings):
                if not reading['recorded_at']:
                    reading['recorded_at'] = secondary_readings[i]['recorded_at']
                reading['secondary_level'] = secondary_readings[i]['secondary_level']
            
            readings.append(reading)
        
        return jsonify({'status': 'success', 'readings': readings})
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            conn.close()

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        socketio.server.enter_room(request.sid, session['username'])
        print(f"Client connected: {request.sid}")
        
        devices = get_user_devices(session['user_id'])
        for device in devices:
            emit('sensor_update', {
                'device_id': device['device_id'],
                'value': device.get('last_value', 0),
                'timestamp': datetime.now().isoformat()
            })
            
            emit('led_status_update', {
                'device_id': device['device_id'],
                'status': device.get('led_state', False),
                'timestamp': datetime.now().isoformat()
            })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    # Verify database connection at startup
    test_conn = get_db_connection()
    if test_conn:
        print("✅ Database connection successful")
        test_conn.close()
    else:
        print("❌ Database connection failed")
    
    # Verify MQTT connection
    if mqtt_client and mqtt_client.is_connected():
        print("✅ MQTT connection successful")
    else:
        print("❌ MQTT connection failed")
    
    socketio.run(app, debug=True)