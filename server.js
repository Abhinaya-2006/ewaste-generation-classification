// app.js
const express = require('express');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises; // Import the promise-based file system module
const bcrypt = require('bcrypt');   // Import bcrypt for password hashing

const app = express();
const PORT = process.env.PORT || 5000;
const SECRET_KEY = process.env.SECRET_KEY || 'your_super_secret_key_please_change_in_production_!'; // Use environment variable for secret key
const USERS_FILE = path.join(__dirname, 'users.json'); // Path to store user data

// --- In-memory (now file-backed) 'database' for demonstration ---
let users = []; // This will be loaded from users.json

// Data for E-Waste specific operations (remains in-memory for simplicity)
const eWasteData = {
    classify: (deviceType, deviceCondition) => {
        let message = `You classified a ${deviceCondition} ${deviceType}.`;
        let recommendation = 'Please consult local recycling guidelines.';

        if (deviceCondition === 'Working' || deviceCondition === 'Partially Working') {
            recommendation = `Consider donating or repairing your ${deviceType} before recycling.`;
        } else if (deviceType === 'Smartphone' || deviceType === 'Laptop' || deviceType === 'Tablet') {
            recommendation = `This ${deviceType} likely contains valuable materials. Find a specialized e-waste recycler.`;
        } else if (deviceType === 'Battery') {
            recommendation = `Batteries should always be recycled separately. Do NOT dispose of them in regular trash.`;
        } else if (deviceType === 'TV' || deviceType === 'Monitor') {
            recommendation = `Large electronics like ${deviceType} often require special pick-up or drop-off.`;
        }
        return { deviceType, deviceCondition, message, recommendation };
    },
    locations: [
        {
            id: 1,
            name: 'Green Earth Recycling Center',
            address: '123 E-Waste Lane, Hyderabad, Telangana',
            contact: '040-12345678',
            hours: 'Mon-Fri: 9 AM - 5 PM',
            acceptedTypes: ['Laptop', 'Smartphone', 'TV', 'Monitor', 'Printer', 'Desktop', 'Battery', 'Cable']
        },
        {
            id: 2,
            name: 'Eco-Friendly Disposal Hub',
            address: '456 Recycle Road, Gachibowli, Hyderabad',
            contact: '040-87654321',
            hours: 'Mon-Sat: 10 AM - 6 PM',
            acceptedTypes: ['Smartphone', 'Tablet', 'Battery', 'Cable', 'Other']
        },
        {
            id: 3,
            name: 'City E-Waste Drop-off Point',
            address: '789 Urban Street, Begumpet, Hyderabad',
            contact: 'N/A',
            hours: '24/7 Drop-off (Bin)',
            acceptedTypes: ['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Printer', 'Battery', 'Cable']
        },
        {
            id: 4,
            name: 'TechReuse Solutions',
            address: '101 Tech Park, Hitech City, Hyderabad',
            contact: '040-99887766',
            hours: 'Mon-Fri: 9 AM - 7 PM',
            acceptedTypes: ['Laptop', 'Desktop', 'Monitor', 'Smartphone', 'Tablet']
        },
        {
            id: 5,
            name: 'Battery Recycle Point',
            address: '22 Recharge Blvd, Jubilee Hills, Hyderabad',
            contact: '040-11223344',
            hours: 'Mon-Sun: 8 AM - 8 PM',
            acceptedTypes: ['Battery', 'Smartphone', 'Tablet']
        }
    ],
    educationGuides: [
        {
            id: 1,
            title: 'The Hidden Dangers of E-Waste',
            description: 'Learn about the hazardous materials present in electronic waste and their environmental impact.',
            imageUrl: 'https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=Dangers'
        },
        {
            id: 2,
            title: 'How to Prepare Your Devices for Recycling',
            description: 'Step-by-step guide on data wiping and preparing your electronics for safe disposal.',
            imageUrl: 'https://via.placeholder.com/300x200/8BC34A/FFFFFF?text=Prepare'
        },
        {
            id: 3,
            title: 'The Benefits of E-Waste Recycling',
            description: 'Discover how recycling electronics conserves resources and reduces pollution.',
            imageUrl: 'https://via.placeholder.com/300x200/66BB6A/FFFFFF?text=Benefits'
        },
        {
            id: 4,
            title: 'DIY: Extend Your Device\'s Lifespan',
            description: 'Simple tips and tricks to maintain and prolong the life of your electronic gadgets.',
            imageUrl: 'https://via.placeholder.com/300x200/A5D6A7/FFFFFF?text=Lifespan'
        }
    ]
};

// --- File-based User Storage Functions ---
async function loadUsers() {
    try {
        const data = await fs.readFile(USERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            // File not found, return an empty array (first run)
            console.log('users.json not found, initializing with empty user list.');
            return [];
        }
        console.error('Error loading users from file:', error);
        return []; // Return empty array on other errors as well
    }
}

async function saveUsers(usersArray) {
    try {
        await fs.writeFile(USERS_FILE, JSON.stringify(usersArray, null, 2), 'utf8');
        console.log('Users saved to users.json');
    } catch (error) {
        console.error('Error saving users to file:', error);
    }
}

// Middleware
app.use(cors()); // Enable CORS for all routes
app.use(express.json()); // For parsing application/json

// Serve static files from the current directory (your HTML, CSS, client-side JS)
app.use(express.static(__dirname));

// Default route to serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Middleware to protect routes
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) {
        console.warn('Authentication attempt: No token provided');
        return res.status(401).json({ message: 'Authentication required: No token provided.' }); // Unauthorized
    }

    jwt.verify(token, SECRET_KEY, (err, user) => {
        if (err) {
            console.error('Authentication error:', err.message);
            return res.status(403).json({ message: 'Authentication failed: Invalid or expired token.' }); // Forbidden
        }
        req.user = user;
        console.log('User authenticated:', user.username);
        next();
    });
}

// --- API Endpoints ---

// Register
app.post('/api/register', async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required.' });
    }

    users = await loadUsers(); // Ensure current state from file

    if (users.some(u => u.username === username)) {
        return res.status(409).json({ message: 'Username already exists. Please choose a different one.' });
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10); // Hash the password
        users.push({ username, password: hashedPassword }); // Store hashed password
        await saveUsers(users); // Save updated user list to file

        console.log('New user registered:', username);
        res.status(201).json({ message: 'Registration successful! You can now log in.' });
    } catch (error) {
        console.error('Error during registration:', error);
        res.status(500).json({ message: 'Server error during registration.' });
    }
});

// Login
app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;

    users = await loadUsers(); // Ensure current state from file

    const user = users.find(u => u.username === username);

    if (!user) {
        return res.status(401).json({ message: 'Invalid username or password.' });
    }

    try {
        const passwordMatch = await bcrypt.compare(password, user.password); // Compare with hashed password

        if (!passwordMatch) {
            return res.status(401).json({ message: 'Invalid username or password.' });
        }

        // Generate JWT token
        const token = jwt.sign({ username: user.username }, SECRET_KEY, { expiresIn: '1h' });
        console.log('User logged in:', user.username);
        res.json({ message: 'Login successful!', token: token, username: user.username });
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).json({ message: 'Server error during login.' });
    }
});

// E-Waste Classification (Protected)
app.post('/api/classify', authenticateToken, (req, res) => {
    const { deviceType, deviceCondition } = req.body;

    if (!deviceType || !deviceCondition) {
        return res.status(400).json({ message: 'Device type and condition are required.' });
    }

    const result = eWasteData.classify(deviceType, deviceCondition);
    res.json(result);
});

// Recycling Locations (Protected)
app.get('/api/recycling_locations', authenticateToken, (req, res) => {
    const deviceTypeFilter = req.query.device_type; // 'All' or specific type

    let filteredLocations = eWasteData.locations;

    if (deviceTypeFilter && deviceTypeFilter !== 'All') {
        filteredLocations = eWasteData.locations.filter(location =>
            location.acceptedTypes.includes(deviceTypeFilter)
        );
    }
    res.json(filteredLocations);
});

// Education Guides (Public - no authentication needed)
app.get('/api/education/guides', (req, res) => {
    res.json(eWasteData.educationGuides);
});

// Catch-all for undefined routes
app.use((req, res, next) => {
    res.status(404).sendFile(path.join(__dirname, '404.html')); // Assuming you might have a 404 page
});


// Start the server and load users
async function startServer() {
    users = await loadUsers(); // Load users at startup
    // If no users.json exists or it's empty, and you want a default user,
    // you can add it here IF `users` is empty after load.
    if (users.length === 0) {
        console.log("No users found, adding a default 'testuser'.");
        const defaultHashedPassword = await bcrypt.hash('password123', 10);
        users.push({ username: 'testuser', password: defaultHashedPassword });
        await saveUsers(users); // Save the default user
    }

    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
        console.log(`To access the app, open your browser and navigate to http://localhost:${PORT}`);
        console.log(`Remember to replace 'your_super_secret_key_please_change_in_production_!' with a strong, random key.`);
        console.log(`User data will be stored in: ${USERS_FILE}`);
    });
}

startServer(); // Call the async function to start the server