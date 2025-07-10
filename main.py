from fastapi import FastAPI, Request, Form, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
import sqlite3
from pathlib import Path
import re

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_PATH = "users.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

def get_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

def render_error(message: str) -> HTMLResponse:
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Error</title>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <style>
                body {{ background: #1a1a1a; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }}
                .error-card {{
                    background: #fff3e0;
                    max-width: 400px;
                    margin: 60px auto;
                    padding: 32px 24px;
                    border-radius: 12px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
                    text-align: center;
                    border-top: 8px solid #fc8019;
                }}
                .error-card h2 {{ color: #fc8019; margin-bottom: 12px; }}
                .error-card p {{ color: #b34700; margin-bottom: 20px; }}
                .home-btn {{
                    display: inline-block;
                    padding: 10px 24px;
                    background: #fc8019;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    text-decoration: none;
                    font-size: 1em;
                    cursor: pointer;
                    transition: background 0.2s;
                }}
                .home-btn:hover {{ background: #d96a15; }}
            </style>
        </head>
        <body>
            <div class='error-card'>
                <h2>Error</h2>
                <p>{message}</p>
                <a href="/" class="home-btn">Back to Home</a>
            </div>
        </body>
    </html>
    """, status_code=400)

@app.get("/check-username")
def check_username(username: str):
    user = get_user(username)
    return JSONResponse({"taken": bool(user)})

def is_valid_username(username: str):
    return (
        len(username) >= 6 and
        re.search(r"[A-Z]", username) and
        re.search(r"[0-9]", username) and
        re.search(r"[^A-Za-z0-9]", username)
    )

def is_valid_password(password: str):
    return (
        len(password) >= 6 and
        re.search(r"[A-Z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    # Validation
    if not is_valid_username(username):
        return render_error("Username must be at least 6 characters, contain at least 1 capital letter, 1 number, and 1 special character.")
    if not is_valid_password(password):
        return render_error("Password must be at least 6 characters, contain at least 1 capital letter, 1 number, and 1 special character.")
    hashed_password = pwd_context.hash(password)
    if not create_user(username, hashed_password):
        return render_error("Username already exists.")
    response = RedirectResponse(url=f"/profile/{username}", status_code=status.HTTP_302_FOUND)
    return response

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Validation
    if not username or not password:
        return render_error("Username and password are required.")
    user = get_user(username)
    if not user or not pwd_context.verify(password, user[2]):
        return render_error("Invalid username or password.")
    response = RedirectResponse(url=f"/profile/{username}", status_code=status.HTTP_302_FOUND)
    return response

@app.get("/profile/{username}", response_class=HTMLResponse)
async def profile(username: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return f"""
    <html>
        <head>
            <title>Profile</title>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <style>
                body {{
                    background: #1a1a1a;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .profile-card {{
                    background: #fff;
                    max-width: 400px;
                    margin: 60px auto;
                    padding: 36px 28px 28px 28px;
                    border-radius: 16px;
                    box-shadow: 0 6px 24px rgba(0,0,0,0.18);
                    text-align: center;
                    border-top: 8px solid #fc8019;
                }}
                .profile-card h1 {{
                    color: #fc8019;
                    margin-bottom: 10px;
                    font-size: 2em;
                    letter-spacing: 1px;
                }}
                .profile-card p {{
                    font-size: 1.15em;
                    color: #333;
                    margin-bottom: 28px;
                }}
                .logout-btn {{
                    display: inline-block;
                    padding: 12px 32px;
                    background: #fc8019;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    text-decoration: none;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background 0.2s, box-shadow 0.2s;
                    box-shadow: 0 2px 8px rgba(252,128,25,0.12);
                }}
                .logout-btn:hover {{
                    background: #d96a15;
                    box-shadow: 0 4px 16px rgba(252,128,25,0.18);
                }}
            </style>
        </head>
        <body>
            <div class='profile-card'>
                <h1>Welcome, {user[1]}!</h1>
                <p><strong>Username:</strong> {user[1]}</p>
                <a href="/" class="logout-btn">Logout</a>
            </div>
        </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("index.html") 
