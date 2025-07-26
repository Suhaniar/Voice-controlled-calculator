
import streamlit as st
import speech_recognition as sr
import pyttsx3
import re
import threading


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        pass


import operator

def multiline(command):
    import operator

    command = command.lower()
    command = command.replace("into", " multiply ")
    command = command.replace("x", " multiply ")
    command = command.replace("multiplied by", " multiply ")
    command = command.replace("multiply by", " multiply ")
    command = command.replace("/", " divide ")
    command = command.replace("+", " add ")
    command = command.replace("-", " subtract ")
    command = command.replace("divided by", " divide ")
    command = command.replace("square root", " sqrt ")
    command = command.replace("cube root", " cbrt ")

    steps = command.split("then")

    op_map = {
        "add": operator.add,
        "subtract": operator.sub,
        "multiply": operator.mul,
        "divide": operator.truediv
    }

    unary_ops = {
        "square": lambda x: x ** 2,
        "cube": lambda x: x ** 3,
        "sqrt": lambda x: round(x ** 0.5, 4),
        "cbrt": lambda x: round(x ** (1 / 3), 4)
    }

    stepwise_output = []
    last_result = None

    for step in steps:
        tokens = step.strip().split()
        values = []
        ops = []

        for word in tokens:
            if word in op_map:
                ops.append(word)
            elif word in unary_ops:
                ops.append(word)
            elif re.match(r'^-?\d+\.?\d*$', word):
                values.append(float(word) if '.' in word else int(word))

        if last_result is not None and len(values) == len(ops):
            values = [last_result] + values

        if not values:
            stepwise_output.append(f"Step: '{step}' => Result: Invalid input")
            continue

        try:
            if ops and ops[0] in unary_ops:
                result = unary_ops[ops[0]](values[0])
            else:
                result = values[0]
                for i in range(len(ops)):
                    result = op_map[ops[i]](result, values[i + 1])
            stepwise_output.append(f"Step: '{step}' => Result: {round(result,2)}")
            last_result = round(result,2)
        except Exception as e:
            stepwise_output.append(f"Step: '{step}' => Result: Error - {e}")
            last_result = "Error"

    return stepwise_output, last_result

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source,timeout=5,phrase_time_limit=10)
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Network error."


def word_to_number(command):
    word_to_num = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
        "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
        "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50",
        "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
        "hundred": "100", "thousand": "1000"
    }

    tokens = command.split()
    converted = []

    for word in tokens:
        if word in word_to_num:
            converted.append(word_to_num[word])
        else:
            converted.append(word)

    return " ".join(converted)

# ---- Streamlit UI ----
st.set_page_config(page_title="🎤 Voice Calculator", page_icon="🎙️")

st.markdown("""
    <h1 style='text-align: center; color: #4B8BBE;'>🎤 Voice-Based Calculator</h1>
    <p style='text-align: center; font-size: 18px;'>Speak any math expression and get the result instantly.</p>
    <hr>
""", unsafe_allow_html=True)


if "greeted" not in st.session_state:
    st.session_state.greeted = True
    threading.Thread(target=speak, args=("Hey, how may I help you?",)).start()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎙️ Start Listening", use_container_width=True):
        with st.spinner("🎧 Listening... Please speak your query."):
            user_text = listen_command()

        st.subheader("🗣️ You said:")
        st.info(user_text)

        if "sorry" not in user_text.lower():
            with st.spinner("🧮 Calculating..."):
                steps, final_result = multiline(user_text)

            st.markdown("### 📘 Step-by-step Calculation:")
            for s in steps:
                st.text(s)

            st.markdown(f"<h3 style='color: green;'>✅ Final Result: {round(final_result,2)}</h3>", unsafe_allow_html=True)
            threading.Thread(target=speak, args=(f"The final result is {round(final_result,2)}",)).start()
        else:
            st.error("❌ Could not understand your command. Please try again.")
