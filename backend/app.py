from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, date
import json, os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SNAP_FILE = os.path.join(DATA_DIR, "snapshots.json")
os.makedirs(DATA_DIR, exist_ok=True)
for f in (USERS_FILE, SNAP_FILE):
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as fh:
            json.dump({}, fh)

app = FastAPI(title="Medical Clone — User Profile (baseline)")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 👈 allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- helpers ---
def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)

def age_from_dob(dob_str):
    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def calculate_bmi(weight_kg: float, height_cm: float):
    h_m = height_cm / 100.0
    if h_m <= 0: return None
    return round(weight_kg / (h_m * h_m), 2)

def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str):
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex.lower() == "male":
        return round(base + 5, 0)
    else:
        return round(base - 161, 0)

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9
}

def calculate_tdee(bmr: float, activity_level: str):
    factor = ACTIVITY_FACTORS.get(activity_level, 1.2)
    return round(bmr * factor, 0)

# --- models ---
class UserCreate(BaseModel):
    name: str
    dob: str
    sex: str
    height_cm: float
    weight_kg: float
    activity_level: str = Field("sedentary")
    user_id: str

class UserOut(UserCreate):
    id: str

class SnapshotCreate(BaseModel):
    weight_kg: float
    height_cm: float = None
    activity_level: str = None
    sleep_hours: float = None
    calories_intake: float = None
    notes: str = None
    timestamp: str = None

class SnapshotOut(BaseModel):
    id: str
    user_id: str
    timestamp: str
    weight_kg: float
    height_cm: float
    activity_level: str
    sleep_hours: Optional[float] = None
    calories_intake: Optional[float] = None
    notes: Optional[str] = None
    bmi: float
    bmr: float
    tdee: float


# --- ROUTES ---
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/users", response_model=UserOut)
def create_user(u: UserCreate):
    users = read_json(USERS_FILE)
    uid = u.user_id
    if uid in users:
        raise HTTPException(400, detail="user_id already exists")
    users[uid] = u.dict()
    users[uid]["created_at"] = datetime.utcnow().isoformat()
    write_json(USERS_FILE, users)
    return {"id": uid, **u.dict()}

@app.get("/api/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    users = read_json(USERS_FILE)
    if user_id not in users:
        raise HTTPException(404, detail="User not found")
    return {"id": user_id, **{k:v for k,v in users[user_id].items() if k in UserCreate.__fields__}}

@app.post("/api/users/{user_id}/snapshots", response_model=SnapshotOut)
def create_snapshot(user_id: str, s: SnapshotCreate):
    users = read_json(USERS_FILE)
    if user_id not in users:
        raise HTTPException(404, detail="User not found")

    user = users[user_id]
    height = s.height_cm or user.get("height_cm")
    activity = s.activity_level or user.get("activity_level", "sedentary")
    weight = s.weight_kg
    age = age_from_dob(user["dob"])

    bmi = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, user["sex"])
    tdee = calculate_tdee(bmr, activity)
    ts = s.timestamp or datetime.utcnow().isoformat()

    snaps = read_json(SNAP_FILE)
    sid = str(uuid4())
    snaps[sid] = {
        "user_id": user_id,
        "timestamp": ts,
        "weight_kg": weight,
        "height_cm": height,
        "activity_level": activity,
        "sleep_hours": s.sleep_hours,
        "calories_intake": s.calories_intake,
        "notes": s.notes,
        "bmi": bmi,
        "bmr": bmr,
        "tdee": tdee
    }
    write_json(SNAP_FILE, snaps)

    return {"id": sid, "user_id": user_id, "timestamp": ts, **snaps[sid]}

@app.get("/api/users/{user_id}/snapshots", response_model=list[SnapshotOut])
def list_snapshots(user_id: str):
    users = read_json(USERS_FILE)
    if user_id not in users:
        raise HTTPException(404, detail="User not found")

    snaps = read_json(SNAP_FILE)
    user_snaps = [
        {"id": sid, **snap}
        for sid, snap in snaps.items()
        if snap["user_id"] == user_id
    ]
    user_snaps.sort(key=lambda x: x["timestamp"])
    return user_snaps
