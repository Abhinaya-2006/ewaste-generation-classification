from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
import json
import os
import secrets  # For generating a strong secret key

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# --- Configuration ---
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))  # Generates a random 32-byte hex string
app.config['USERS_FILE'] = 'users.json'  # Path to store user data

# Initialize Flask-JWT-Extended and Flask-Bcrypt
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# --- Data for E-Waste specific operations ---
e_waste_data = {
    'classify': lambda device_type, device_condition: {
        'message': f"You classified a {device_condition} {device_type}.",
        'recommendation': {
            'Working': f"Consider donating or repairing your {device_type} before recycling.",
            'Partially Working': f"Consider donating or repairing your {device_type} before recycling.",
            'Smartphone': f"This {device_type} likely contains valuable materials. Find a specialized e-waste recycler.",
            'Laptop': f"This {device_type} likely contains valuable materials. Find a specialized e-waste recycler.",
            'Tablet': f"This {device_type} likely contains valuable materials. Find a specialized e-waste recycler.",
            'Battery': f"Batteries should always be recycled separately. Do NOT dispose of them in regular trash.",
            'TV': f"Large electronics like {device_type} often require special pick-up or drop-off.",
            'Monitor': f"Large electronics like {device_type} often require special pick-up or drop-off.",
        }.get(device_condition, 'Please consult local recycling guidelines.')
    },
    'locations': [
        {
            'id': 1,
            'name': 'Green Earth Recycling Center',
            'address': '123 E-Waste Lane, Hyderabad, Telangana',
            'contact': '040-12345678',
            'hours': 'Mon-Fri: 9 AM - 5 PM',
            'acceptedTypes': ['Laptop', 'Smartphone', 'TV', 'Monitor', 'Printer', 'Desktop', 'Battery', 'Cable']
        },
        {
            'id': 2,
            'name': 'Eco-Friendly Disposal Hub',
            'address': '456 Recycle Road, Gachibowli, Hyderabad',
            'contact': '040-87654321',
            'hours': 'Mon-Sat: 10 AM - 6 PM',
            'acceptedTypes': ['Smartphone', 'Tablet', 'Battery', 'Cable', 'Other']
        },
        {
            'id': 3,
            'name': 'City E-Waste Drop-off Point',
            'address': '789 Urban Street, Begumpet, Hyderabad',
            'contact': 'N/A',
            'hours': '24/7 Drop-off (Bin)',
            'acceptedTypes': ['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Printer', 'Battery', 'Cable']
        },
        {
            'id': 4,
            'name': 'TechReuse Solutions',
            'address': '101 Tech Park, Hitech City, Hyderabad',
            'contact': '040-99887766',
            'hours': 'Mon-Fri: 9 AM - 7 PM',
            'acceptedTypes': ['Laptop', 'Desktop', 'Monitor', 'Smartphone', 'Tablet']
        },
        {
            'id': 5,
            'name': 'Battery Recycle Point',
            'address': '22 Recharge Blvd, Jubilee Hills, Hyderabad',
            'contact': '040-11223344',
            'hours': 'Mon-Sun: 8 AM - 8 PM',
            'acceptedTypes': ['Battery', 'Smartphone', 'Tablet']
        }
    ],
    'education_guides': [
        {
            'id': 1,
            'title': 'The Hidden Dangers of E-Waste',
            'description': 'Learn about the hazardous materials present in electronic waste and their environmental impact.',
            'full_content': 'Electronic waste contains toxic materials like lead, mercury, cadmium, and beryllium. When disposed of improperly in landfills, these substances can leach into the soil and groundwater, contaminating our ecosystems and posing severe health risks to humans and wildlife.'
        },
        {
            'id': 2,
            'title': 'How to Prepare Your Devices for Recycling',
            'description': 'Step-by-step guide on data wiping and preparing your electronics for safe disposal.',
            'full_content': 'Before recycling, it\'s crucial to protect your personal data. For smartphones and computers, perform a factory reset or securely wipe your hard drive. Remove all personal accounts, SIM cards, and memory cards.'
        },
        {
            'id': 3,
            'title': 'The Benefits of E-Waste Recycling',
            'description': 'Discover how recycling electronics conserves resources and reduces pollution.',
            'full_content': 'Recycling e-waste is vital for environmental sustainability. It helps recover valuable materials like gold, silver, copper, and platinum, reducing the need for new mining and conserving natural resources.'
        },
        {
            'id': 4,
            'title': 'DIY: Extend Your Device\'s Lifespan',
            'description': 'Simple tips and tricks to maintain and prolong the life of your electronic gadgets.',
            'full_content': 'Extending the life of your electronic devices is a great way to reduce e-waste. Simple steps include using protective cases, avoiding extreme temperatures, and keeping software updated.'
        }
    ]
}

# --- File-based User Storage Functions ---
def load_users():
    if not os.path.exists(app.config['USERS_FILE']):
        return []
    with open(app.config['USERS_FILE'], 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users_list):
    with open(app.config['USERS_FILE'], 'w', encoding='utf-8') as f:
        json.dump(users_list, f, indent=2)

# --- Initialize users ---
def initialize_users_on_startup():
    users = load_users()
    if not users:
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        users.append({'username': 'testuser', 'password': hashed_password})
        save_users(users)
    return users

# --- Frontend Serving Routes ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

# --- API Endpoints ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    users = load_users()
    if any(u['username'] == username for u in users):
        return jsonify({'message': 'Username already exists. Please choose a different one.'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users.append({'username': username, 'password': hashed_password})
    save_users(users)

    return jsonify({'message': 'Registration successful! You can now log in.'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_users()
    user = next((u for u in users if u['username'] == username), None)

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid username or password.'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'message': 'Login successful!', 'token': access_token, 'username': username}), 200

@app.route('/api/classify', methods=['POST'])
@jwt_required()
def classify_route():
    data = request.get_json()
    device_type = data.get('deviceType')
    device_condition = data.get('deviceCondition')

    if not device_type or not device_condition:
        return jsonify({'message': 'Device type and condition are required.'}), 400

    result_data = e_waste_data['classify'](device_type, device_condition)
    result_data['deviceType'] = device_type
    result_data['deviceCondition'] = device_condition

    return jsonify(result_data)

@app.route('/api/recycling_locations', methods=['GET'])
@jwt_required()
def get_recycling_locations():
    device_type_filter = request.args.get('device_type')

    filtered_locations = e_waste_data['locations']
    if device_type_filter and device_type_filter != 'All':
        filtered_locations = [
            loc for loc in e_waste_data['locations']
            if device_type_filter in loc['acceptedTypes']
        ]
    return jsonify(filtered_locations)

@app.route('/api/education/guides', methods=['GET'])
def get_education_guides():
    return jsonify(e_waste_data['education_guides'])

if __name__ == '__main__':
    initialize_users_on_startup()
    app.run(debug=True, port=5000)
