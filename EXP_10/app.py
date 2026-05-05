from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import pickle
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "water_quality.db"

# Load model & scaler
model = pickle.load(open("models/xgboost.sav", "rb"))
scaler = pickle.load(open("models/scaler.sav", "rb"))

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ph REAL,
            turbidity REAL,
            sulfate REAL,
            conductivity REAL,
            chloramines REAL,
            trihalomethanes REAL,
            hardness REAL,
            organic_carbon REAL,
            solids REAL,
            prediction TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[2] == password:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            conn.close()
            return "Username already exists!"

    return render_template("register.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- PREDICT ----------------
def safe_float(value, name):
    if value is None or value == "":
        raise ValueError(f"{name} is missing")
    return float(value)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        ph = safe_float(data.get("ph"), "ph")
        turbidity = safe_float(data.get("turbidity"), "turbidity")
        sulfate = safe_float(data.get("sulfate"), "sulfate")
        conductivity = safe_float(data.get("conductivity"), "conductivity")
        chloramines = safe_float(data.get("chloramines"), "chloramines")
        trihalomethanes = safe_float(data.get("trihalomethanes"), "trihalomethanes")
        hardness = safe_float(data.get("hardness"), "hardness")
        organic_carbon = safe_float(data.get("organic_carbon"), "organic_carbon")
        solids = safe_float(data.get("solids"), "solids")

        # RULE BASED SAFETY CHECK
        if turbidity > 5 or sulfate > 500 or ph < 4 or ph > 10:
            result = "Non-Potable Water (Unsafe Parameters)"
        else:
            features = pd.DataFrame([{
                "ph": ph,
                "Hardness": hardness,
                "Solids": solids,
                "Chloramines": chloramines,
                "Sulfate": sulfate,
                "Conductivity": conductivity,
                "Organic_carbon": organic_carbon,
                "Trihalomethanes": trihalomethanes,
                "Turbidity": turbidity
            }])

            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]

            result = "Potable Water" if prediction == 1 else "Non-Potable Water"

        # SAVE TO DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("""
            INSERT INTO history (
                user_id, ph, turbidity, sulfate, conductivity,
                chloramines, trihalomethanes, hardness,
                organic_carbon, solids, prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.get("user_id"),
            ph, turbidity, sulfate, conductivity,
            chloramines, trihalomethanes, hardness,
            organic_carbon, solids, result
        ))

        conn.commit()
        conn.close()

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"prediction": f"Error: {str(e)}"})


# ---------------- HISTORY ----------------
@app.route('/history')
def history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT ph, prediction, created_at
        FROM history
        ORDER BY id DESC
        LIMIT 5
    """)

    data = c.fetchall()
    conn.close()

    return jsonify(data)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)