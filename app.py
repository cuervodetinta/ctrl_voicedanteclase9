import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client,userdata,result):             
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(f"<p class='custom-text'>{message_received}</p>", unsafe_allow_html=True)

broker="157.230.214.127"
port=1883
client1= paho.Client("GIT-HUBC")
client1.on_message = on_message

st.markdown(
    """
    <style>
        .stApp {
            background-color: #ffe6f0;
            text-align: center;
        }
        .custom-text, .stMarkdown, .stText, .stSubheader, .stTitle {
            color: #b30059;
            text-align: center;
        }
        .stButton>button {
            background-color: #b30059;
            color: white;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #800040;
        }
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

col1, col2 = st.columns([1, 1])

with col1:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, use_column_width=True)

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p class='custom-text'>Toca el Botón y habla</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

stt_button = Button(label="🎙️ Inicio", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        text_result = result.get("GET_TEXT")
        st.write(f"<p class='custom-text'>{text_result}</p>", unsafe_allow_html=True)
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":text_result.strip()})
        ret= client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
