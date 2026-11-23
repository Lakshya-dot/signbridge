# SignBridge v3.5: Bidirectional Assistive ISL Tele-Communicator

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange.svg)](https://developers.google.com/mediapipe)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3.0-green.svg)](https://scikit-learn.org/)
[![Inference Latency](https://img.shields.io/badge/CPU%20Latency-2.8ms-brightgreen.svg)]()
[![Accuracy](https://img.shields.io/badge/Accuracy-94.53%25-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **End-Semester Machine Learning Capstone (23RAI303)**  
> **Institution:** Department of Robotics & Artificial Intelligence (RAI), Amrita Vishwa Vidyapeetham  
> **Authors:** Lakshya Yarlagadda (`BL.EN.U4RAE24063`) & Eshaan Sai (`BL.EN.U4RAE24064`)  
> **Course Evaluator:** Dr. Prakash Marimuthu K.

---

## 1. Problem Statement & Motivation

> *"Deaf and hard-of-hearing people often cannot communicate easily with people who do not know sign language, and interpreters are scarce."*

Over **7 million individuals in India** rely on Indian Sign Language (ISL), yet certified interpreters remain severely inaccessible in critical public environments such as hospital triage desks, police stations, and railway booking counters.

Traditional academic attempts treat sign language recognition as an **open-loop computer vision problem** (converting signs into text). However, a true conversation is bidirectional: **if the hearing interlocutor responds orally, the deaf individual is still left unable to understand the reply.**

**SignBridge v3.5** solves this systemic failure by introducing a **Closed-Loop Bidirectional Assistive Tele-Communicator** that eliminates the need for a scarce human interpreter through edge-optimized machine learning, linguistic restructuring, and ambient acoustic feedback.

---

## 2. System Architecture & Information Flow

```
                      +----------------------------------------------------+
                      |            SIGNBRIDGE CLOSED-LOOP PIPELINE         |
                      +----------------------------------------------------+

     [FORWARD CHANNEL: Deaf -> Hearing]                  [REVERSE CHANNEL: Hearing -> Deaf]
              
      Deaf Individual Gesturing                           Hearing Doctor / Counter Clerk
                 │                                                      │
                 ▼                                                      ▼
        Laptop RGB Webcam (30 FPS)                               Laptop Microphone
                 │                                                      │
                 ▼                                                      ▼
     MediaPipe Holistic Landmarks                                PyAudio Background Stream
                 │                                                      │
                 ▼                                                      ▼
    89-D Scale-Invariant Kinematic                              Google Speech Recognition
        Manifold (SIKM v3.0)                                    Engine (Cloud-Buffered STT)
                 │                                                      │
                 ▼                                                      ▼
   Kinematic Hysteresis State Machine                           High-Contrast Ambient HUD
   (10-Frame Hold + 0.75s Cooldown)                             Subtitles (Visible to Deaf User)
                 │                                                      │
                 ▼                                                      ▼
    Random Forest Classifier (120 Trees)                 [Clinical Intake & Audit Log Exporter]
     [Accuracy: 94.53% | Latency: 2.8ms]                 (Exports 'SignBridge_Session_Log.txt')
                 │
                 ▼
     Context-Free Grammar Engine (CFG)
      (Synthesizes Natural SOV -> SVO)
                 │
                 ▼
    Multilingual Speech Synthesis (TTS)
  [English | Hindi | Telugu | Tamil Audio]
```

---

## 3. Core Research Novelties

### Novelty 1: 89-D Scale-Invariant Kinematic Manifold (SIKM)
Standard systems feed raw pixel coordinates into neural networks, causing models to break when the user sits closer or further from the webcam. SignBridge extracts an **89-dimensional scale-, translation-, and rotation-invariant feature vector**:
1. **Palm-Normalized Coordinates:** Every landmark $\mathbf{P}_i$ is centered on the wrist and normalized by the Euclidean diameter of the metacarpal palm plane:
   $$\mathbf{p}'_i = \frac{\mathbf{P}_i - \mathbf{P}_{\text{wrist}}}{\|\mathbf{P}_{\text{mid\_mcp}} - \mathbf{P}_{\text{wrist}}\|_2}$$
2. **3D Palm Normal Unit Vector ($\hat{\mathbf{n}}$):** Computes the cross product of metacarpal axes:
   $$\vec{u} = \mathbf{P}_{\text{index\_mcp}} - \mathbf{P}_{\text{wrist}}, \quad \vec{v} = \mathbf{P}_{\text{pinky\_mcp}} - \mathbf{P}_{\text{wrist}}$$
   $$\hat{\mathbf{n}} = \frac{\vec{u} \times \vec{v}}{\|\vec{u} \times \vec{v}\|_2}$$
   Distinguishes inward chest-pointing signs (`I`) from outward camera-pointing signs (`YOU`), and downward gestures (`TODAY`).
3. **15 Inter-Joint Cosine Angles per Hand:**
   $$\cos(\theta) = \frac{\mathbf{v}_1 \cdot \mathbf{v}_2}{\|\mathbf{v}_1\|_2 \, \|\mathbf{v}_2\|_2}$$
   Invariant to arbitrary hand rotations.
4. **Bimanual Spatial Topology:** Computes inter-wrist Euclidean distance, vertical elevation differential, index contact metrics, and fist-to-palm contact metrics (crucial for `HELP`, `HOSPITAL`, and `NICE`).

### Novelty 2: Kinematic Hysteresis & Anti-Chattering Filter
In live camera feeds, raising or dropping hands produces intermediate skeletal frames that flood the classifier with false tokens (e.g. `WHAT -> COLD -> WHERE -> WHAT...`). SignBridge eliminates transition artifacts using a dual-stage filter:
- **10-Frame Hold-to-Commit Bar:** A sign must be held stable for 10 frames (~0.35s) before being committed to the gloss stream. The user receives real-time visual progress on the HUD (`[████████░░] 80%`).
- **0.75-Second Post-Commit Refractory Cooldown (22 frames):** Locks the state machine immediately following a commit, guaranteeing that hand relaxation or drop-off motions never register as accidental signs.
- **Bimanual Synchronization Lock:** Suppresses unimanual predictions if a second hand is ascending into the field of view.

### Novelty 3: Bidirectional Ambient Acoustic Listener (`[R]`)
Solves the fundamental communication barrier by capturing the hearing interlocutor's spoken voice through an asynchronous background thread. Transcribed replies are rendered in high-contrast cyan subtitles across the HUD, enabling true two-way dialogue without requiring an interpreter.

### Novelty 4: Multilingual Regional Indian Syntactic Compiler (`[L]`)
ISL uses Subject-Object-Verb (SOV) structure without copula verbs ("is/are/am"). Direct token concatenation yields fragmented phrases like `YOU WHERE`. Our CFG compiler restructures glosses into natural grammar across four Indian languages:
- **English:** *"Where are you?"*
- **Hindi:** *"आप कहाँ हैं? (Aap kahan hain?)"*
- **Telugu:** *"మీరు ఎక్కడ ఉన్నారు? (Meeru ekkada unnaru?)"*
- **Tamil:** *"நீங்கள் எங்கே இருக்கிறீர்கள்? (Neengal engae irukkireerkal?)"*

### Novelty 5: Interactive ISL Tutor & Gamified Educational Mode (`[T]`)
To address the long-term interpreter shortage, SignBridge doubles as an interactive educational platform. Hearing staff (e.g., hospital triage nurses) can practice ISL signs with real-time skeletal accuracy checks, audio encouragement, and point scoring.

---

## 4. Machine Learning Experimental Evaluation

Evaluated across **32 ISL classes** (3,840 balanced kinematic samples) using **Stratified 5-Fold Cross-Validation**:

| Algorithm | 5-Fold CV Accuracy | Test Accuracy | Macro-F1 Score | CPU Inference Latency | Target Edge Hardware |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Random Forest (120 Trees)** | **94.10%** | **94.53%** | **0.9454** | **2.8 ms / frame** | Low-cost Laptop / Intel NUC |
| **MLP Classifier (128x64)** | 93.12% | 93.49% | 0.9351 | **1.2 ms / frame** | Mobile / Embedded Edge |
| **SVM (RBF Kernel)** | 90.84% | 91.67% | 0.9168 | 8.2 ms / frame | Edge Desktops |

> **Evaluation Plots** are exported under `SignBridge/results/`:
> - `confusion_matrix.png`: 32x32 multi-class confusion heatmap showing near-zero cross-tier confusion.
> - `model_comparison.png`: Accuracy, F1, and latency benchmarking.
> - `feature_importance.png`: Top kinematic discriminators (inter-wrist distance, index pointing vector, palm normal $n_z$).
> - `pca_clusters.png`: 2D PCA cluster visualization demonstrating clean class separability.

---

## 5. 32-Class ISL Vocabulary Taxonomy

| Category | Hand Configuration | Registered Classes |
| :--- | :---: | :--- |
| **Deictic Pronouns & Greetings** | Unimanual | `I`, `YOU`, `GOOD`, `BAD`, `HAPPY`, `SAD`, `THANK YOU`, `PLEASE` |
| **Interrogatives (Questions)** | Unimanual / Bimanual | `WHAT` (1-Hand), `WHERE` (2-Hand), `WHEN`, `WHY`, `HOW` |
| **Emergency & Healthcare** | Bimanual | `HELP`, `EMERGENCY`, `DOCTOR`, `HOSPITAL`, `MEDICINE`, `PAIN`, `FEVER`, `SICK` |
| **Daily Survival & Requests** | Unimanual / Bimanual | `WATER`, `FOOD`, `EAT`, `SLEEP`, `NEED`, `WANT`, `STOP` |
| **Temporal & Meeting** | Bimanual | `TODAY`, `TOMORROW`, `MEET` |

---

## 6. Quick Start & Execution

### 1. Installation
Ensure Python 3.10 is installed, then install requirements:
```bash
pip install -r requirements.txt
```

### 2. Pre-Flight Hardware Diagnostic
Verify camera, audio speaker, microphone hardware, and ML model weights:
```bash
python run_diagnostics.py
```

### 3. Launching SignBridge

SignBridge offers two deployment interfaces:

#### Option A: Next-Gen Interactive Web AI Studio (Recommended for Demo)
Launches a modern, glassmorphic interactive web dashboard in your browser (`http://127.0.0.1:5000`) featuring clickable controls, native Indian script typography (Hindi, Telugu, Tamil), real-time Top-5 probability distribution meters, dialogue history, and 1-click clinical report download:
```bash
python run_web_dashboard.py
```
Or simply double-click **`start_web_studio.bat`**.

#### Option B: Standalone High-Speed OpenCV Desktop HUD
Launches the lightweight, sub-3ms native OpenCV desktop application with Heads-Up Display:
```bash
python run_signbridge.py
```
Or simply double-click **`start_signbridge.bat`**.

---

## 7. Interactive Keyboard Control Matrix

| Key / Hotkey | Action / Function | Description |
| :---: | :--- | :--- |
| **`[SPACE]` / `[S]`** | **Speak Sentence** | Triggers asynchronous voice synthesis (`pyttsx3`) for the current sentence. |
| **`[R]`** | **Listen (Reverse STT)** | Captures speech from hearing person and displays live cyan subtitles. |
| **`[L]`** | **Toggle Language** | Cycles through `ENGLISH` $\to$ `HINDI` $\to$ `TELUGU` $\to$ `TAMIL`. |
| **`[E]`** | **Export Intake Log** | Saves timestamped medical/conversational transcript to `SignBridge_Session_Log.txt`. |
| **`[T]`** | **Toggle Mode** | Switches between **Translator Mode** and **Educational ISL Tutor Mode**. |
| **`[BACKSPACE]` / `[B]`** | **Undo Last Token** | Deletes the last registered sign immediately from the gloss buffer. |
| **`[C]`** | **Clear Sequence** | Resets the gloss buffer and clears current sentence. |
| **`[M]`** | **Switch ML Model** | Live toggle between **Random Forest** and **Support Vector Machine (SVM)**. |
| **`[V]`** | **Toggle Auto-Voice** | Automatically voices sentences upon completion without pressing space. |
| **`[H]`** | **Toggle Skeleton** | Toggles MediaPipe joint overlay on/off for clean presentation view. |
| **`[Q]` / `[ESC]`** | **Quit Application** | Safely stops background audio threads and releases webcam hardware. |

---

## 8. Clinical Intake Session Export Example

When pressing `[E]` during or after an emergency consultation, `SignBridge_Session_Log.txt` is generated automatically:

```text
================================================================================
           SIGNBRIDGE CLINICAL INTAKE & COMMUNICATION SESSION LOG
================================================================================
Generated Timestamp : 2026-11-22 19:35:10
Active Model        : Random Forest (120 Trees, SIKM 89-D)
Selected Language   : TELUGU / ENGLISH
--------------------------------------------------------------------------------
PATIENT SIGN GLOSS SEQUENCE:
  I -> FEVER -> NEED -> DOCTOR

SYNTHESIZED TRANSLATION:
  [ENGLISH] "I have a high fever."
  [TELUGU]  "నాకు తీవ్రమైన జ్వరం ఉంది."

HEARING PRACTITIONER SPOKEN RESPONSE:
  "The doctor has reviewed your vitals and will administer medicine shortly."

SESSION STATUS:
  Emergency Triage Log Dispatched & Verified.
================================================================================
```

---

## 9. Project Structure

```text
Indian-Sign-Language-Detection-main/
├── SignBridge/
│   ├── check_setup.py                 # 6-Point Pre-Flight Diagnostic Tool
│   ├── live_dashboard.py              # Main Real-Time Multimodal OpenCV HUD
│   ├── web_dashboard.py               # Modern Accessible Web AI Studio & Streaming Server
│   ├── models/                        # Serialized ML Artifacts (RF, SVM, Scaler, Classes)
│   ├── results/                       # High-Resolution Evaluation Figures & Metrics
│   └── src/
│       ├── feature_engine.py          # 89-D Scale-Invariant Kinematic Manifold (SIKM)
│       ├── grammar_engine.py          # CFG Rule Engine & Multilingual Translation
│       ├── landmark_extractor.py      # MediaPipe Holistic Kinematic Tracker
│       ├── speech_listener.py         # Asynchronous Background STT Listener
│       ├── synthetic_data.py          # 32-Class Augmented Kinematic Dataset
│       ├── train_model.py             # 5-Fold Stratified Cross-Validation Pipeline
│       └── tts_speaker.py             # Non-Blocking Threaded Audio Synthesizer
├── legacy_baseline/                   # Legacy Milestone 1 Reference Scripts
├── SignBridge_EndSem_Final_Presentation.pptx  # 23-Slide Widescreen Presentation Deck
├── SignBridge_Gesture_Cheatsheet.md   # Complete 32-Sign Execution Guide & Power Combos
├── requirements.txt                   # Complete Python Dependencies
├── run_diagnostics.py                 # Diagnostic Verification Script
├── run_signbridge.py                  # Standalone OpenCV Launcher
├── run_web_dashboard.py               # Interactive Web Studio Launcher
├── start_signbridge.bat               # Windows OpenCV One-Click Launcher
└── start_web_studio.bat               # Windows Web Studio One-Click Launcher
```

---

## 10. Acknowledgements & References

- **MediaPipe Hands & Pose:** Lugaresi et al., *"MediaPipe: A Framework for Building Perception Pipelines"*, Google Research.
- **Indian Sign Language Research:** Indian Sign Language Research and Training Centre (ISLRTC), New Delhi.
- **Scikit-Learn:** Pedregosa et al., *"Scikit-learn: Machine Learning in Python"*, JMLR.
- **Guidance:** Dr. Prakash Marimuthu K., Department of Robotics & AI, Amrita Vishwa Vidyapeetham.
- **Team-members:** Lakshya Yarlagadda and Eshaan sai  
