import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 2. Dual Modes Diagram
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

# Mode 1 Card
card1 = patches.FancyBboxPatch((0.5, 0.4), 5.2, 3.8, boxstyle='round,pad=0.15,rounding_size=0.2',
                               facecolor='#1e293b', edgecolor='#38bdf8', linewidth=2.5)
ax.add_patch(card1)
ax.text(3.1, 3.8, 'MODE 1: Assistive Translation HUD', ha='center', va='center',
        color='#38bdf8', fontsize=12, fontweight='bold')
mode1_text = (
    "• Real-Time Continuous Communication\n"
    "• Live 21-point MediaPipe hand skeleton overlay\n"
    "• 24 ISL gloss recognition at 30 FPS\n"
    "• Temporal debouncing (4 frames ~ 0.15s)\n"
    "• Syntactic grammar engine (SOV -> SVO English)\n"
    "• Threaded pyttsx3 voice audio playback\n"
    "• Real-time confidence gauge (tau = 0.50)"
)
ax.text(0.8, 2.1, mode1_text, ha='left', va='center', color='#e2e8f0', fontsize=9.5, linespacing=1.6)

# Mode 2 Card
card2 = patches.FancyBboxPatch((6.3, 0.4), 5.2, 3.8, boxstyle='round,pad=0.15,rounding_size=0.2',
                               facecolor='#1e293b', edgecolor='#10b981', linewidth=2.5)
ax.add_patch(card2)
ax.text(8.9, 3.8, 'MODE 2: Interactive ISL Tutor ([T])', ha='center', va='center',
        color='#10b981', fontsize=12, fontweight='bold')
mode2_text = (
    "• Automated Sign Language Literacy Training\n"
    "• Interactive step-by-step signing challenges\n"
    "• Real-time gesture pose validation & grading\n"
    "• Hold duration confirmation (4 stable frames)\n"
    "• Audio praise: 'Correct! Excellent job.'\n"
    "• Gamified scoring tracker (+10 pts per sign)\n"
    "• Bridges communication gap bidirectionally!"
)
ax.text(6.6, 2.1, mode2_text, ha='left', va='center', color='#e2e8f0', fontsize=9.5, linespacing=1.6)

# Switch prompt in middle
toggle_box = patches.FancyBboxPatch((4.3, 4.3), 3.4, 0.6, boxstyle='round,pad=0.08,rounding_size=0.15',
                                    facecolor='#334155', edgecolor='#f59e0b', linewidth=2.0)
ax.add_patch(toggle_box)
ax.text(6.0, 4.6, 'Press [T] to Toggle Live Modes', ha='center', va='center',
        color='#f59e0b', fontsize=10.5, fontweight='bold')

ax.set_xlim(0, 12.0)
ax.set_ylim(0, 5.2)
ax.axis('off')
plt.tight_layout()
plt.savefig('SignBridge/results/dual_modes_diagram.png', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print('Dual modes diagram generated!')

# 3. Gesture Cheatsheet & Disambiguation Diagram
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

# Title
ax.text(6.0, 4.8, 'Crucial ISL Sign Disambiguation: 1-Hand vs. 2-Hand Signs', ha='center', va='center',
        color='#38bdf8', fontsize=13, fontweight='bold')

# Card 1: WHAT vs WHERE
c1 = patches.FancyBboxPatch((0.5, 0.4), 5.2, 3.9, boxstyle='round,pad=0.12,rounding_size=0.18',
                            facecolor='#1e293b', edgecolor='#ef4444', linewidth=2.0)
ax.add_patch(c1)
ax.text(3.1, 3.9, 'The "What" vs. "Where" Confusion', ha='center', va='center',
        color='#f87171', fontsize=11.5, fontweight='bold')
what_vs_where = (
    "WHY 'What are you?' HAPPENED:\n"
    "• 'WHAT' is a 1-HANDED sign: One hand open,\n"
    "   palm facing camera or up slightly.\n"
    "• 'WHERE' is a 2-HANDED sign: BOTH hands raised,\n"
    "   palms open facing up side-by-side.\n\n"
    "CORRECT TECHNIQUE FOR 'Where are you?':\n"
    "1. Point index finger forward -> Registers 'YOU'\n"
    "2. Raise BOTH hands open facing up -> Registers 'WHERE'\n"
    "3. Result: 'Where are you?' spoken instantly!"
)
ax.text(0.8, 2.1, what_vs_where, ha='left', va='center', color='#f1f5f9', fontsize=9.2, linespacing=1.45)

# Card 2: Essential Sign Checklist
c2 = patches.FancyBboxPatch((6.3, 0.4), 5.2, 3.9, boxstyle='round,pad=0.12,rounding_size=0.18',
                            facecolor='#1e293b', edgecolor='#10b981', linewidth=2.0)
ax.add_patch(c2)
ax.text(8.9, 3.9, 'Essential Presentation Signs Checklist', ha='center', va='center',
        color='#34d399', fontsize=11.5, fontweight='bold')
signs_checklist = (
    "• YOU (1-Hand): Point right index finger at camera.\n"
    "• HELP (2-Hand): Rest RIGHT closed fist on flat LEFT palm.\n"
    "• GOOD (1-Hand): Right hand thumbs-up, palm sideways.\n"
    "• SICK (2-Hand): Touch forehead & stomach/chest.\n"
    "• HOSPITAL (2-Hand): Form a cross '+' with index fingers.\n"
    "• STOP (1-Hand): Open palm facing outwards flat.\n\n"
    "PRO TIP: Keep hands steady for 0.15s (4 frames) to\n"
    "trigger the majority-vote confirmation!"
)
ax.text(6.6, 2.1, signs_checklist, ha='left', va='center', color='#f1f5f9', fontsize=9.2, linespacing=1.45)

ax.set_xlim(0, 12.0)
ax.set_ylim(0, 5.2)
ax.axis('off')
plt.tight_layout()
plt.savefig('SignBridge/results/gesture_disambiguation.png', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print('Gesture disambiguation diagram generated!')
