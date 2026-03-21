<<<<<<< HEAD
# 🔐 SecurePass – Password Generator

> A cryptographically-strong password generator with a **Flask web app**.

---

## ✨ Features

| Feature | Web |
|---|:---:|
| Cryptographically secure (`secrets` module) | ✅ |
| Configurable length (4–64) | ✅ |
| Uppercase / Lowercase / Digits / Symbols toggles | ✅ |
| **At-least-one** guarantee per category | ✅ |
| Animated strength indicator (Weak → Very Strong) | ✅ |
| Shannon entropy display | ✅ |
| Show / Hide password toggle | ✅ |
| Copy to clipboard | ✅ |
| Last 5 passwords history | ✅ |
| Dark theme | ✅ |

---

## 📁 Project Structure

```
Password Generator/
├── password_generator.py   # Core engine (secrets, entropy, strength)
├── flask_app.py            # Flask REST API + web server
├── templates/
│   └── index.html          # Single-page web UI
├── requirements.txt        # External dependencies
└── README.md
```

---

## 🚀 How to Run

### Web App (Flask)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python flask_app.py

# 3. Open your browser
# → http://127.0.0.1:5000
```

### Test the Core Engine Alone

```bash
python password_generator.py
```

---

## 🧪 REST API Reference (Flask)

### `POST /generate`
```json
// Request
{ "length": 20, "use_upper": true, "use_lower": true, "use_digits": true, "use_symbols": true }

// Response
{ "password": "aB3$xY…", "entropy": 131.1, "strength": "Very Strong", "score": 4 }
```

### `POST /check`
```json
// Request
{ "password": "hello123" }

// Response
{ "strength": "Weak", "score": 0, "entropy": 37.6 }
```

---

## 🔬 How Entropy Is Calculated

```
H = L × log₂(N)
```
- **L** = password length  
- **N** = alphabet size (number of unique characters available)  
- **128+ bits** → computationally infeasible to brute-force in any foreseeable future

---

## 🛣️ Future Improvements

| Area | Idea |
|---|---|
| **Storage** | Save password vault encrypted with AES-256 (e.g., `cryptography` library) |
| **CLI** | Add an `argparse`-powered terminal interface |
| **Breach check** | Integrate HaveIBeenPwned API (k-anonymity model) to check if a password was leaked |
| **Password rules** | Add per-site rule profiles (e.g., "no symbols", "max 12 chars") |
| **Mobile** | Port to Kivy for iOS/Android |
| **Testing** | Add `pytest` unit tests for the core engine |
| **Docker** | Containerise the Flask app for one-click cloud deployment |

---

## 🤝 Acknowledgements

- Python [`secrets`](https://docs.python.org/3/library/secrets.html) module  
- [`Flask`](https://flask.palletsprojects.com/) – lightweight web framework

---

> **Built with Vaishnavi Pandav 
=======
# 🔐 SecurePass – Professional Password Generator

> A cryptographically-strong password generator with a **Flask web app**.

---

## ✨ Features

| Feature | Web |
|---|:---:|
| Cryptographically secure (`secrets` module) | ✅ |
| Configurable length (4–64) | ✅ |
| Uppercase / Lowercase / Digits / Symbols toggles | ✅ |
| **At-least-one** guarantee per category | ✅ |
| Animated strength indicator (Weak → Very Strong) | ✅ |
| Shannon entropy display | ✅ |
| Show / Hide password toggle | ✅ |
| Copy to clipboard | ✅ |
| Last 5 passwords history | ✅ |
| Dark theme | ✅ |

---

## 📁 Project Structure

```
Password Generator/
├── password_generator.py   # Core engine (secrets, entropy, strength)
├── flask_app.py            # Flask REST API + web server
├── templates/
│   └── index.html          # Single-page web UI
├── requirements.txt        # External dependencies
└── README.md
```

---

## 🚀 How to Run

### Web App (Flask)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python flask_app.py

# 3. Open your browser
# → http://127.0.0.1:5000
```

### Test the Core Engine Alone

```bash
python password_generator.py
```

---

## 🧪 REST API Reference (Flask)

### `POST /generate`
```json
// Request
{ "length": 20, "use_upper": true, "use_lower": true, "use_digits": true, "use_symbols": true }

// Response
{ "password": "aB3$xY…", "entropy": 131.1, "strength": "Very Strong", "score": 4 }
```

### `POST /check`
```json
// Request
{ "password": "hello123" }

// Response
{ "strength": "Weak", "score": 0, "entropy": 37.6 }
```

---

## 🔬 How Entropy Is Calculated

```
H = L × log₂(N)
```
- **L** = password length  
- **N** = alphabet size (number of unique characters available)  
- **128+ bits** → computationally infeasible to brute-force in any foreseeable future

---

## 🛣️ Future Improvements

| Area | Idea |
|---|---|
| **Storage** | Save password vault encrypted with AES-256 (e.g., `cryptography` library) |
| **CLI** | Add an `argparse`-powered terminal interface |
| **Breach check** | Integrate HaveIBeenPwned API (k-anonymity model) to check if a password was leaked |
| **Password rules** | Add per-site rule profiles (e.g., "no symbols", "max 12 chars") |
| **Mobile** | Port to Kivy for iOS/Android |
| **Testing** | Add `pytest` unit tests for the core engine |
| **Docker** | Containerise the Flask app for one-click cloud deployment |

---

## 🤝 Acknowledgements

- Python [`secrets`](https://docs.python.org/3/library/secrets.html) module  
- [`Flask`](https://flask.palletsprojects.com/) – lightweight web framework

---

> **Built with Vaishnavi Pandav 
>>>>>>> c83d8f2cbbc873c011c33a36c4fa1118bed09959
