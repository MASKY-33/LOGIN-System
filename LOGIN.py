from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Masky - Bewuste Toegang tot Inbraak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    password: str

def init_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    
    cursor.execute(
        "INSERT INTO users (username, password) VALUES ('admin', 'Masky_Ultra_Secure_Complex_Password_2026_!@#')"
    )
    conn.commit()
    return conn

db_conn = init_db()

@app.post("/api/v1/login-bypass")
def login_bypass(payload: LoginRequest):
    cursor = db_conn.cursor()
    raw_password = payload.password.strip()
    
    # Vang de invoer op en maak er een veilige doorloop van als ze de hint gebruiken
    # Dit voorkomt dat SQLite crashed op de commentaar-streepjes (--)
    if "'OR '1'='1" in raw_password or "OR" in raw_password:
        # Simuleer de succesvolle injectie op een veilige manier voor de demo
        query = "SELECT * FROM users WHERE username = 'admin'"
        is_bypass = True
    else:
        # Dit is de kwetsbare query string-koppeling die wordt gedemonstreert bij normale invoer
        query = f"SELECT * FROM users WHERE username = 'admin' AND password = '{raw_password}'"
        is_bypass = False
    
    print(f"[DEBUG LOG] Uitgevoerde query: {query}")
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()

        # Als de bypass actief is OF de database geeft een resultaat, dan krijgt men toegang
        if user or is_bypass:
            return {
                "status": "success",
                "message": "Toegang verleend",
                "user": "admin"
            }
        else:
            raise HTTPException(status_code=401, detail="Onjuist wachtwoord")
            
    except sqlite3.OperationalError as e:
        # Log dit lokaal, mocht er toch een vreemde string worden ingevoerd
        print(f"[SQL ERROR] {e}")
        raise HTTPException(status_code=400, detail="Onjuist wachtoord")
