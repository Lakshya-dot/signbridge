# SignBridge v3.0: Complete 32-Sign ISL Cheatsheet
**End-Semester Machine Learning Project (23RAI303)**  
**Authors:** Lakshya Yarlagadda & Eshaan Sai | **Evaluator:** Dr. Prakash Marimuthu K  

---

## ⚡ Quick Rules for a 100% Flawless Live Demo

1. **The 0.35s Hold-to-Commit Rule:** Hold your hand steady for **10 frames (~0.35 seconds)**. Look at the HUD card on the left: watch the blue progress bar fill to 100% until it flashes green: **`LOCKED: [SIGN]`**.
2. **The 0.75s Cooldown Rule:** After a sign locks, the system ignores hand transitions for 0.75 seconds. **Do not rush!** Relax your hands or smoothly transition to the next gesture.
3. **1-Hand vs 2-Hand Rule:**
   - Single-hand signs (`YOU`, `I`, `GOOD`, `WHAT`, `PLEASE`) $\to$ Use **ONE hand** only; keep the other hand resting below the desk.
   - Two-hand signs (`WHERE`, `HELP`, `HOSPITAL`, `DOCTOR`, `MEET`, `TODAY`) $\to$ Raise **BOTH hands** clearly into the camera frame at chest level.
4. **Mistake Recovery:** If an accidental sign ever registers, tap **`[BACKSPACE]`** or **`[B]`** on your keyboard to instantly delete the last sign and re-synthesize the sentence!

---

## 1. Greetings & Personal Introductions

| Sign | Hands | Exact Hand Shape & Posture | Position & Orientation | English Translation Output |
| :--- | :---: | :--- | :--- | :--- |
| **`I`** | **1 Hand** | Index finger extended, other 4 fingers curled. | **Point downward/inward directly touching your chest/sternum.** | Single: *"I."* <br>Combo: *"I am feeling sick."* / *"I am good."* |
| **`YOU`** | **1 Hand** | Index finger extended, other 4 fingers curled. | **Point straight forward directly at the laptop camera lens.** | Single: *"You."* <br>Combo: *"Where are you?"* / *"How are you?"* |
| **`NAME`** | **2 Hands** | Index and middle fingers extended on both hands (forming an 'H' or 'U' shape). | **Tap the right index/middle fingers across the left index/middle fingers.** | Combo with YOU+WHAT: *"What is your name?"* <br>Combo with I: *"My name is..."* |
| **`HOW`** | **2 Hands** | Both hands curved/cupped, palms facing downward initially. | **Roll both hands upward and forward together so palms end facing upward.** | Combo with YOU: *"How are you?"* |
| **`NICE`** | **2 Hands** | Both hands completely flat and open (all 5 fingers extended). | **Left hand held flat horizontally (palm up). Right flat hand slides smoothly forward over the left palm.** | Combo with MEET+YOU: *"Nice to meet you."* |
| **`MEET`** | **2 Hands** | Index fingers extended upright on both hands (pointing to ceiling), other fingers curled. | **Bring both hands from sides toward center until the knuckles/index fingers touch.** | Combo with NICE+YOU: *"Nice to meet you."* |
| **`PLEASE`** | **1 Hand** | Right hand completely open and flat (palm facing inward). | **Place flat right hand on chest and make a gentle circular rubbing motion.** | Single: *"Please assist me."* <br>Combo: *"Could you please help me?"* |
| **`THANK YOU`** | **1 Hand** | Right hand flat, fingertips touching your chin/lips. | **Move the flat hand smoothly outward and forward away from the chin towards the camera.** | Single: *"Thank you very much."* |

---

## 2. Questions & Interrogatives (Wh-Signs)

| Sign | Hands | Exact Hand Shape & Posture | Position & Orientation | English Translation Output |
| :--- | :---: | :--- | :--- | :--- |
| **`WHERE`** | **2 Hands** | **BOTH hands open (all fingers extended), palms facing UPWARD to ceiling.** | **Hold both hands side-by-side at mid-chest level, shaking/tilting gently side to side.** | Combo with YOU: **`"Where are you?"`** <br>Combo with HOSPITAL: *"Where is the nearest hospital?"* |
| **`WHAT`** | **1 Hand** | Single right hand open, palm facing up/camera. | **Hold one hand at chest level, shaking palm slightly side to side.** | Single: *"What is that?"* <br>Combo with YOU: *"What are you doing?"* |
| **`WHEN`** | **2 Hands** | Both index fingers extended pointing horizontally toward each other. | **Bring index fingertips together in center until they touch horizontally.** | Single: *"When is it?"* <br>Combo with YOU: *"When will you arrive?"* |
| **`WHY`** | **1 Hand** | Form a "Y" hand (Thumb and Pinky extended, middle 3 fingers curled into fist). | **Touch thumb/knuckle near your right temple and pull outward slightly.** | Single: *"Why?"* <br>Combo with YOU: *"Why are you doing that?"* |

---

## 3. Medical & Emergency Triage

| Sign | Hands | Exact Hand Shape & Posture | Position & Orientation | English Translation Output |
| :--- | :---: | :--- | :--- | :--- |
| **`HELP`** | **2 Hands** | **Left hand flat palm facing UP. Right hand forms a closed FIST with thumb upright.** | **Rest the closed RIGHT fist firmly on top of the open flat LEFT palm.** | Single: **`"Please help me!"`** <br>Combo with EMERGENCY: *"Emergency! Please help me!"* |
| **`HOSPITAL`** | **2 Hands** | Both index fingers extended, all other fingers curled into fists. | **Cross both index fingers at right angles in front of chest to form a PLUS sign (`+`).** | Single: *"Hospital."* <br>Combo with WHERE: **`"Where is the nearest hospital?"`** |
| **`DOCTOR`** | **2 Hands** | Left arm extended flat (palm up). Right index and middle fingers extended. | **Tap the right index/middle fingertips onto the left inner wrist (checking pulse).** | Single: *"The doctor."* <br>Combo with WHERE: *"Where can I find a doctor?"* <br>Combo with CALL: *"Please call a doctor immediately."* |
| **`EMERGENCY`** | **2 Hands** | Both hands form closed fists at shoulder level. | **Shake/wave both fists rapidly side-to-side near upper chest/shoulders.** | Single: **`"Emergency! Please assist!"`** |
| **`FEVER`** | **1 Hand** | Right hand flat and open. | **Place the BACK of your right hand flat against your forehead.** | Single: **`"I have a high fever."`** |
| **`SICK`** | **1 Hand** | Right index finger extended or middle finger slightly bent. | **Touch fingertips to your forehead/temple with head slightly tilted.** | Single: **`"I am feeling sick."`** |
| **`PAIN`** | **2 Hands** | Both index fingers extended pointing toward each other horizontally. | **Hold in front of chest and twist wrists sharply back and forth.** | Single: **`"I am experiencing severe pain."`** |
| **`MEDICINE`** | **2 Hands** | Left hand flat palm up. Right hand fingers curled or middle finger bent into palm. | **Circular grinding motion of right fingertips into the center of the left palm (mortar/pestle).** | Combo with NEED: **`"I need my medicine."`** |
| **`TIRED`** | **2 Hands** | Both hands curved/clawed, fingertips resting against upper chest. | **Drop both hands downward and let wrists droop limply against chest.** | Single: **`"I am feeling very tired."`** |

---

## 4. Everyday Needs, Desires & Polite Commands

| Sign | Hands | Exact Hand Shape & Posture | Position & Orientation | English Translation Output |
| :--- | :---: | :--- | :--- | :--- |
| **`WATER`** | **1 Hand** | Form a 'W' hand (Index, Middle, and Ring fingers extended upright; thumb holds pinky). | **Tap the side of your index finger against your chin twice.** | Single: **`"I need water."`** <br>Combo with WHERE: *"Where can I find drinking water?"* |
| **`FOOD` / `EAT`** | **1 Hand** | Pinched hand shape (all 5 fingertips touching together). | **Tap the pinched fingertips against your lips/mouth twice.** | Single: **`"I want food."`** <br>Combo with I: *"I want to eat food."* |
| **`WANT`** | **1 Hand** | Hand open, fingers curved slightly into claws (palms up). | **Pull hand inward toward your chest while slightly curling fingers.** | Combo with WATER: *"I want some water, please."* |
| **`NEED`** | **1 Hand** | Index finger bent into a hook/crook (like a question mark). | **Drop wrist downward sharply in front of chest.** | Combo with MEDICINE: *"I need my medicine."* |
| **`GOOD`** | **1 Hand** | Right hand forms a clear **THUMBS UP** (thumb pointing up, 4 fingers curled into fist). | **Hold firmly at mid-chest level.** | Single: **`"I am doing good."`** |
| **`BAD`** | **1 Hand** | Right hand forms a clear **THUMBS DOWN** (thumb pointing down). | **Hold firmly at mid-chest level.** | Single: **`"Something is wrong."`** |
| **`HAPPY`** | **2 Hands** | Both hands flat and open, palms facing inward toward chest. | **Brush both open palms upward against chest repeatedly with a cheerful motion.** | Single: **`"I am feeling happy."`** |
| **`STOP`** | **1 Hand** | Right hand completely open and vertical, fingers pointing straight up to ceiling. | **Push open palm firmly outward toward the camera like a traffic police stop signal.** | Single: **`"Please stop."`** |

---

## 5. Time & Calendar Indicators

| Sign | Hands | Exact Hand Shape & Posture | Position & Orientation | English Translation Output |
| :--- | :---: | :--- | :--- | :--- |
| **`TODAY`** | **2 Hands** | **Option A:** Both hands form 'Y' shape (thumb and pinky extended, middle 3 curled). <br>**Option B:** Both open palms facing **DOWNWARD**. | **Drop both hands downward simultaneously in front of chest.** | Single: *"Today."* <br>Combo with HOT: *"It is hot today."* <br>Combo with COLD: *"It is cold today."* |
| **`TOMORROW`** | **1 Hand** | Right hand in fist with thumb extended. | **Touch thumb tip to your right cheek/jaw and flick it forward away from face.** | Combo with MEET: *"We will meet tomorrow."* |

---

## 🏆 Top 5 Power Combos for Your Live Demo to Sir

| Combo Sequence | Gestures to Perform in Order | Synthesized English Spoken Aloud |
| :--- | :--- | :--- |
| **1. The Introduction** | 1. `NICE` (slide right palm over left palm) <br>2. `MEET` (touch two upright index fingers) <br>3. `YOU` (point index at camera) | **`"Nice to meet you."`** |
| **2. The Well-being Check** | 1. `YOU` (point index forward) <br>2. `HOW` (roll cupped hands upward) | **`"How are you?"`** |
| **3. The Crucial Question** | 1. `YOU` (point index forward) <br>2. `WHERE` (raise BOTH hands open, palms facing UP) | **`"Where are you?"`** |
| **4. The Medical Emergency** | 1. `HELP` (rest right fist on left flat palm) <br>2. `EMERGENCY` (wave both fists near shoulders) | **`"Emergency! Please help me!"`** |
| **5. The Hospital Triage** | 1. `HOSPITAL` (cross index fingers `+`) <br>2. `WHERE` (raise both open palms UP) | **`"Where is the nearest hospital?"`** |
