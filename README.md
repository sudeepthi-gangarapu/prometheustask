# prometheustask
# College Signup/Login Web App

A simple full-stack web application with:
- **Frontend:** HTML, CSS, and vanilla JS (no frameworks)
- **Backend:** FastAPI (Python)
- **Database:** SQLite

## Features
- Signup/Login with strong validation (username & password must have at least 1 capital letter, 1 special character, 1 number, and be at least 6 characters)
- Passwords are hashed (bcrypt)
- Username availability check (AJAX)
- Password strength meter (red to green)
- Animated college-themed landing page
- User profile page after login

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Create and activate a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI server
```bash
uvicorn main:app --reload
```

- The server will start at [http://localhost:8000](http://localhost:8000)
- Open this URL in your browser to use the app

---

## Usage
- **Signup:**
  - Username and password must each be at least 6 characters, contain at least 1 capital letter, 1 special character, and 1 number.
  - The signup form will show a live password strength meter and check if the username is already taken.
- **Login:**
  - Enter your registered username and password.
- **Profile:**
  - After login/signup, you are redirected to your profile page.

---

## Project Structure
```
main.py           # FastAPI backend
index.html        # Frontend (HTML/CSS/JS)
requirements.txt  # Python dependencies
users.db          # SQLite database (auto-created)
```

---

## Notes
- The database file (`users.db`) is created automatically on first run.
- Passwords are securely hashed using bcrypt (via passlib).
- All validation is enforced both client-side and server-side.
- To reset the app, you can delete `users.db` (this will remove all users).

---

## License
MIT (or specify your license) 
