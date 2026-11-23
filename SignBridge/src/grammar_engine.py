"""
SignBridge Robust Grammar Engine (v3.0)
Converts Indian Sign Language (ISL) Gloss sequences into fluent, natural English sentences.
Includes:
- Intelligent token noise reduction and deduplication
- Ambiguity resolution (e.g. prioritizing intentional bimanual signs over transient unimanual glitches)
- Canonical conversational idiom matching (Greetings, Emergency, Medical, Wh-Inquiries)
- Context-Free Grammar (CFG) Subject-Object-Verb (SOV) to English SVO reconstruction
- Auxiliary/Copula verb ('is', 'are', 'am') and article injection
"""

from typing import List, Tuple

class ISLGrammarEngine:
    def __init__(self):
        # Direct canonical conversational patterns (High precision exact phrases)
        self.exact_phrase_map = {
            # --- 1. GREETINGS & INTRODUCTIONS ---
            ("NICE", "MEET", "YOU"): "Nice to meet you.",
            ("MEET", "YOU"): "Good to meet you.",
            ("YOU", "HOW"): "How are you?",
            ("HOW", "YOU"): "How are you?",
            ("I", "GOOD"): "I am doing good.",
            ("I", "HAPPY"): "I am feeling happy.",
            ("YOU", "NAME", "WHAT"): "What is your name?",
            ("NAME", "WHAT"): "What is your name?",
            ("I", "NAME"): "My name is...",
            ("PLEASE", "HELP"): "Could you please help me?",
            ("THANK YOU",): "Thank you very much.",
            ("THANK YOU", "YOU"): "Thank you so much.",
            ("GOOD",): "I am doing good.",

            # --- 2. LOCATION & INQUIRIES ---
            ("YOU", "WHERE"): "Where are you?",
            ("WHERE", "YOU"): "Where are you?",
            ("HOSPITAL", "WHERE"): "Where is the nearest hospital?",
            ("DOCTOR", "WHERE"): "Where can I find a doctor?",
            ("WATER", "WHERE"): "Where can I find drinking water?",
            ("FOOD", "WHERE"): "Where can I find food?",
            ("YOU", "WHAT"): "What are you doing?",
            ("WHAT", "YOU"): "What are you doing?",
            ("YOU", "WHEN"): "When will you come?",
            ("YOU", "WHY"): "Why are you doing that?",

            # --- 3. MEDICAL & EMERGENCY ---
            ("HELP",): "Please help me!",
            ("EMERGENCY",): "Emergency! Please help!",
            ("HELP", "EMERGENCY"): "Emergency! Please help me!",
            ("EMERGENCY", "HELP"): "Emergency! Please help me!",
            ("I", "SICK"): "I am feeling sick.",
            ("I", "FEVER"): "I have a high fever.",
            ("I", "PAIN"): "I am experiencing severe pain.",
            ("I", "TIRED"): "I am feeling very tired.",
            ("DOCTOR", "NEED"): "I need to see a doctor.",
            ("DOCTOR", "CALL"): "Please call a doctor immediately.",
            ("DOCTOR", "HELP"): "Doctor, please help me.",
            ("MEDICINE", "NEED"): "I need my medicine.",
            ("MEDICINE", "WANT"): "I need my medicine.",
            ("I", "HOSPITAL", "GO"): "I need to go to the hospital.",
            ("HOSPITAL", "GO"): "Please take me to the hospital.",

            # --- 4. DAILY LIFE & REQUESTS ---
            ("WATER", "WANT"): "I want some water, please.",
            ("WATER", "NEED"): "I need drinking water.",
            ("FOOD", "WANT"): "I would like some food.",
            ("I", "EAT"): "I want to eat food.",
            ("I", "SLEEP"): "I want to sleep.",
            ("STOP",): "Please stop.",
            ("TODAY", "HOT"): "It is hot today.",
            ("TODAY", "COLD"): "It is cold today.",
            ("TOMORROW", "MEET"): "We will meet tomorrow.",
            ("TOMORROW", "DOCTOR", "COME"): "The doctor will arrive tomorrow.",
        }

        # Multi-Lingual Regional Indian Translations (English, Hindi, Telugu, Tamil)
        self.multilingual_translations = {
            "Where are you?": {
                "HINDI": "आप कहाँ हैं? (Aap kahan hain?)",
                "TELUGU": "మీరు ఎక్కడ ఉన్నారు? (Meeru ekkada unnaru?)",
                "TAMIL": "நீங்கள் எங்கே இருக்கிறீர்கள்? (Neengal engae irukkireerkal?)"
            },
            "Please help me!": {
                "HINDI": "कृपया मेरी मदद करें! (Kripya meri madad karein!)",
                "TELUGU": "దయచేసి నాకు సహాయం చేయండి! (Dayachesi naaku sahaayam cheyandi!)",
                "TAMIL": "தயவுசெய்து எனக்கு உதவுங்கள்! (Thayavuseithu enakku uthavungal!)"
            },
            "Emergency! Please help!": {
                "HINDI": "आपातकाल! कृपया मदद करें! (Aapaatkaal! Kripya madad karein!)",
                "TELUGU": "అత్యవసరం! దయచేసి సహాయం చేయండి! (Atyavasaram! Dayachesi sahaayam cheyandi!)",
                "TAMIL": "அவசரம்! தயவுசெய்து உதவுங்கள்! (Avasaram! Thayavuseithu uthavungal!)"
            },
            "Emergency! Please help me!": {
                "HINDI": "आपातकाल! कृपया मदद करें! (Aapaatkaal! Kripya madad karein!)",
                "TELUGU": "అత్యవసరం! దయచేసి సహాయం చేయండి! (Atyavasaram! Dayachesi sahaayam cheyandi!)",
                "TAMIL": "அவசரம்! தயவுசெய்து உதவுங்கள்! (Avasaram! Thayavuseithu uthavungal!)"
            },
            "I have a high fever.": {
                "HINDI": "मुझे तेज़ बुखार है। (Mujhe tez bukhar hai.)",
                "TELUGU": "నాకు తీవ్రమైన జ్వరం ఉంది. (Naaku teevramaina jwaram undi.)",
                "TAMIL": "எனக்கு அதிக காய்ச்சல் உள்ளது. (Enakku adhiga kaaichal ullathu.)"
            },
            "I am experiencing severe pain.": {
                "HINDI": "मुझे बहुत दर्द हो रहा है। (Mujhe bahut dard ho raha hai.)",
                "TELUGU": "నాకు చాలా నొప్పిగా ఉంది. (Naaku chaala noppiga undi.)",
                "TAMIL": "எனக்கு கடுமையான வலி உள்ளது. (Enakku kadumaiyaana vali ullathu.)"
            },
            "I am feeling sick.": {
                "HINDI": "मेरी तबियत खराब है। (Meri tabiyat kharab hai.)",
                "TELUGU": "నాకు అనారోగ్యంగా ఉంది. (Naaku anaarogyamgaa undi.)",
                "TAMIL": "எனக்கு உடல்நிலை சரியில்லை. (Enakku udalnillai sariyillai.)"
            },
            "Where is the nearest hospital?": {
                "HINDI": "निकटतम अस्पताल कहाँ है? (Nikat-tam aspataal kahan hai?)",
                "TELUGU": "సమీప ఆసుపత్రి ఎక్కడ ఉంది? (Sameepa aasupatri ekkada undi?)",
                "TAMIL": "அருகிலுள்ள மருத்துவமனை எங்கே உள்ளது? (Arugilulla maruthuvamanai engae ullathu?)"
            },
            "Where can I find a doctor?": {
                "HINDI": "डॉक्टर कहाँ मिलेंगे? (Doctor kahan milenge?)",
                "TELUGU": "డాక్టర్ ఎక్కడ దొరుకుతారు? (Doctor ekkada dorukutaaru?)",
                "TAMIL": "மருத்துவர் எங்கே இருப்பார்? (Maruthuvar engae iruppaar?)"
            },
            "Please call a doctor immediately.": {
                "HINDI": "कृपया तुरंत डॉक्टर को बुलाएँ! (Kripya turant doctor ko bulaayein!)",
                "TELUGU": "దయచేసి వెంటనే డాక్టర్ని పిలవండి! (Dayachesi ventane doctor-ni pilavandi!)",
                "TAMIL": "தயவுசெய்து உடனே மருத்துவரை அழையுங்கள்! (Thayavuseithu udanae maruthuvarai azhaiyungal!)"
            },
            "I need my medicine.": {
                "HINDI": "मुझे अपनी दवाई चाहिए। (Mujhe apni dawai chahiye.)",
                "TELUGU": "నాకు నా మందులు కావాలి. (Naaku naa mandulu kaavali.)",
                "TAMIL": "எனக்கு மருந்து தேவை. (Enakku marunthu thevai.)"
            },
            "I want some water, please.": {
                "HINDI": "मुझे पानी चाहिए। (Mujhe paani chahiye.)",
                "TELUGU": "నాకు మంచి నీరు కావాలి. (Naaku manchi neeru kaavali.)",
                "TAMIL": "எனக்கு தண்ணீர் வேண்டும். (Enakku thanneer vendum.)"
            },
            "I need drinking water.": {
                "HINDI": "मुझे पीने का पानी चाहिए। (Mujhe peene ka paani chahiye.)",
                "TELUGU": "నాకు త్రాగునీరు కావాలి. (Naaku traaguneeru kaavali.)",
                "TAMIL": "எனக்கு குடிநீர் தேவை. (Enakku kudineer thevai.)"
            },
            "Nice to meet you.": {
                "HINDI": "आपसे मिलकर अच्छा लगा। (Aapse milkar achha laga.)",
                "TELUGU": "మిమ్మల్ని కలవడం సంతోషంగా ఉంది. (Mimmalni kalavadam santhoshamgaa undi.)",
                "TAMIL": "உங்களை சந்தித்ததில் மகிழ்ச்சி. (Ungalai santhithathil magizhchi.)"
            },
            "How are you?": {
                "HINDI": "आप कैसे हैं? (Aap kaise hain?)",
                "TELUGU": "మీరు ఎలా ఉన్నారు? (Meeru elaa unnaru?)",
                "TAMIL": "நீங்கள் எப்படி இருக்கிறீர்கள்? (Neengal eppadi irukkireerkal?)"
            },
            "What is your name?": {
                "HINDI": "आपका नाम क्या है? (Aapka naam kya hai?)",
                "TELUGU": "మీ పేరు ఏమిటి? (Mee peru emiti?)",
                "TAMIL": "உங்கள் பெயர் என்ன? (Ungal peyar enna?)"
            },
            "I am doing good.": {
                "HINDI": "मैं ठीक हूँ। (Main theek hoon.)",
                "TELUGU": "నేను బాగున్నాను. (Nenu baagunnaanu.)",
                "TAMIL": "நான் நலமாக இருக்கிறேன். (Naan nalamaaga irukkiren.)"
            },
            "Thank you very much.": {
                "HINDI": "बहुत बहुत धन्यवाद। (Bahut bahut dhanyavaad.)",
                "TELUGU": "చాలా ధన్యవాదాలు. (Chaala dhanyavaadaalu.)",
                "TAMIL": "மிக்க நன்றி. (Mikka nandri.)"
            },
            "Please stop.": {
                "HINDI": "कृपया रुकें। (Kripya rukein.)",
                "TELUGU": "దయచేసి ఆపండి. (Dayachesi aapandi.)",
                "TAMIL": "தயவுசெய்து நிறுத்துங்கள். (Thayavuseithu niruthungal.)"
            }
        }

    def get_regional_translation(self, english_text: str, target_lang: str) -> str:
        """Returns regional translation (Hindi/Telugu/Tamil) if available, otherwise English."""
        if target_lang == "ENGLISH" or not english_text:
            return english_text
        if english_text in self.multilingual_translations:
            return self.multilingual_translations[english_text].get(target_lang, english_text)
        return english_text

    def clean_gloss_stream(self, tokens: List[str]) -> List[str]:
        """
        Deduplicates consecutive identical signs and suppresses transient 1-frame glitches.
        For example: ['WHERE', 'WHERE'] -> ['WHERE']
        ['YOU', 'WHAT', 'WHERE'] -> ['YOU', 'WHERE'] if WHERE was the intentional target.
        """
        if not tokens:
            return []

        # 1. Remove consecutive duplicates
        deduped = []
        for t in tokens:
            tok = t.strip().upper()
            if not tok or tok in ["IDLE", "UNCERTAIN"]:
                continue
            if not deduped or deduped[-1] != tok:
                deduped.append(tok)

        if not deduped:
            return []

        # 2. Ambiguity resolution for WHAT vs WHERE:
        # If 'WHERE' and 'WHAT' both exist in a short sequence with 'YOU',
        # 'WHERE' is the deliberate two-handed gesture; remove the spurious 'WHAT' transition.
        if "WHERE" in deduped and "WHAT" in deduped:
            deduped = [tok for tok in deduped if tok != "WHAT"]

        # 3. Suppress spurious intermediate cold/fist detections during hand movement
        if len(deduped) >= 3:
            filtered = [deduped[0]]
            for i in range(1, len(deduped) - 1):
                prev_t = deduped[i - 1]
                curr_t = deduped[i]
                next_t = deduped[i + 1]
                # If COLD or WANT is sandwiched between two open-hand or pointing signs, it was an intermediate motion
                if curr_t in ["COLD", "WANT"] and prev_t in ["YOU", "I", "WHERE", "NICE"] and next_t in ["WHERE", "HOSPITAL", "HELP"]:
                    continue
                filtered.append(curr_t)
            filtered.append(deduped[-1])
            deduped = filtered

        return deduped

    def translate(self, gloss_tokens: List[str]) -> Tuple[str, str]:
        """
        Translates a list of recognized ISL gloss tokens into natural English.
        Returns:
            (natural_english_sentence, explanation_rule)
        """
        clean_tokens = self.clean_gloss_stream(gloss_tokens)
        if not clean_tokens:
            return "", "Empty gloss sequence"

        token_tuple = tuple(clean_tokens)

        # 1. Exact canonical sentence match
        if token_tuple in self.exact_phrase_map:
            return self.exact_phrase_map[token_tuple], "Canonical ISL phrase match"

        # Check sub-tuples from the end (most recent full clause)
        for sub_len in range(min(4, len(clean_tokens)), 1, -1):
            sub_tuple = tuple(clean_tokens[-sub_len:])
            if sub_tuple in self.exact_phrase_map:
                return self.exact_phrase_map[sub_tuple], f"Recent {sub_len}-sign canonical pattern"

        # 2. Single isolated sign representation
        if len(clean_tokens) == 1:
            word = clean_tokens[0]
            if word == "HELP":
                return "Please help me!", "Single word emergency sign"
            if word == "EMERGENCY":
                return "Emergency! Please assist!", "Single word emergency sign"
            if word in ["GOOD", "HAPPY"]:
                return "I am doing good.", "Affirmative state descriptor"
            if word == "BAD":
                return "Something is wrong.", "Negative state descriptor"
            if word == "SICK":
                return "I am feeling sick.", "Health descriptor"
            if word == "FEVER":
                return "I have a fever.", "Health descriptor"
            if word == "PAIN":
                return "I am in pain.", "Health descriptor"
            if word == "TIRED":
                return "I am feeling tired.", "Physical state descriptor"
            if word == "WATER":
                return "I need water.", "Request sign"
            if word == "FOOD":
                return "I want food.", "Request sign"
            if word == "STOP":
                return "Please stop.", "Command sign"
            if word == "THANK YOU":
                return "Thank you very much.", "Politeness sign"
            if word == "PLEASE":
                return "Please assist me.", "Politeness sign"
            if word == "WHERE":
                return "Where is it?", "Inquiry sign"
            if word == "WHAT":
                return "What is that?", "Inquiry sign"
            if word == "HOW":
                return "How is it?", "Inquiry sign"
            return word.capitalize() + ".", "Isolated sign representation"

        # 3. Two-Sign Rule-Based Syntactic Assembler
        if len(clean_tokens) == 2:
            w1, w2 = clean_tokens[0], clean_tokens[1]

            # Inquiries
            if w1 == "YOU" and w2 in ["WHERE", "WHAT", "WHEN", "WHY", "HOW"]:
                if w2 == "WHERE": return "Where are you?", "Subject + Question inversion"
                if w2 == "HOW": return "How are you?", "Greeting inquiry"
                if w2 == "WHAT": return "What are you doing?", "Subject + Question inversion"
                if w2 == "WHEN": return "When will you arrive?", "Subject + Question inversion"
                if w2 == "WHY": return "Why are you doing that?", "Subject + Question inversion"

            if w1 == "I" and w2 in ["SICK", "HAPPY", "GOOD", "COLD", "HOT", "TIRED", "PAIN", "FEVER"]:
                if w2 in ["PAIN", "FEVER"]:
                    return f"I have a {w2.lower()}.", "1st person health condition expression"
                return f"I am {w2.lower()}.", "1st person copula ('am') insertion"

            if w1 == "YOU" and w2 in ["SICK", "HAPPY", "GOOD", "TIRED"]:
                return f"Are you {w2.lower()}?", "2nd person interrogative copula insertion"

            if w1 in ["DOCTOR", "HOSPITAL", "WATER", "FOOD"] and w2 == "WHERE":
                prefix = "the " if w1 in ["DOCTOR", "HOSPITAL"] else ""
                return f"Where is {prefix}{w1.lower()}?", "Third-person inquiry inversion"

            if w1 in ["DOCTOR", "POLICE"] and w2 == "CALL":
                return f"Please call the {w1.lower()}!", "Imperative emergency call expansion"

            if w1 in ["WATER", "FOOD", "MEDICINE"] and w2 in ["WANT", "NEED"]:
                verb = "need" if w2 == "NEED" else "would like"
                return f"I {verb} {w1.lower()}, please.", "Desire / necessity injection"

            if w1 in ["TODAY", "TOMORROW"] and w2 in ["HOT", "COLD", "GOOD"]:
                tense = "is" if w1 == "TODAY" else "will be"
                return f"It {tense} {w2.lower()} {w1.lower()}.", "Time-topic dummy pronoun insertion"

        # 4. Multi-token Fallback Parser
        has_where = "WHERE" in clean_tokens
        has_how = "HOW" in clean_tokens
        has_what = "WHAT" in clean_tokens
        has_you = "YOU" in clean_tokens
        has_i = "I" in clean_tokens
        has_help = "HELP" in clean_tokens
        has_emergency = "EMERGENCY" in clean_tokens

        if has_you and has_where:
            return "Where are you?", "Extracted semantic intent: Location inquiry"
        if has_you and has_how:
            return "How are you?", "Extracted semantic intent: Well-being inquiry"
        if has_help or has_emergency:
            return "Emergency! Please help me!", "Extracted semantic intent: Emergency assistance"
        if has_i and "SICK" in clean_tokens:
            return "I am feeling sick.", "Extracted semantic intent: Medical health status"
        if has_i and "FEVER" in clean_tokens:
            return "I have a fever.", "Extracted semantic intent: Fever diagnosis"
        if has_i and "PAIN" in clean_tokens:
            return "I am in severe pain.", "Extracted semantic intent: Pain report"

        # General sentence fallback
        sentence_words = [t.capitalize() for t in clean_tokens]
        return " ".join(sentence_words) + ".", "Sequential gloss combination"
