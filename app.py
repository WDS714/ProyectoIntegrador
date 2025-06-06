from flask import Flask, request, jsonify, render_template_string, send_file
import pandas as pd
from gpt4all import GPT4All
import threading
import serial
import openpyxl
import datetime
from openpyxl.utils.exceptions import InvalidFileException

PUERTO = 'COM3'
BAUDIOS = 9600
ARCHIVO_EXCEL = "humedad_datos.xlsx"
MODELO_PATH = r"C:\Users\tsmit\gpt4all\resources\Llama-3.2-3B-Instruct-Q4_0.gguf"

def guardar_datos_sensor():
    try:
        arduino = serial.Serial(PUERTO, BAUDIOS)
        print(f"✅ Conectado a {PUERTO}")
        try:
            libro = openpyxl.load_workbook(ARCHIVO_EXCEL)
            hoja = libro.active
        except (FileNotFoundError, InvalidFileException):
            libro = openpyxl.Workbook()
            hoja = libro.active
            hoja.append(["FechaHora", "Humedad (%)", "Estado"])
        while True:
            lectura = arduino.readline().decode().strip()
            if "," in lectura:
                porcentaje, estado = lectura.split(",")
                ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hoja.append([ahora, int(porcentaje), estado])
                libro.save(ARCHIVO_EXCEL)
                print(f"📥 {ahora} → {porcentaje}% → {estado}")
    except Exception as e:
        print(f"❌ Error al conectar con el puerto {PUERTO}:", e)

hilo_sensor = threading.Thread(target=guardar_datos_sensor, daemon=True)
hilo_sensor.start()

model = GPT4All(MODELO_PATH)

def cargar_datos():
    try:
        return pd.read_excel(ARCHIVO_EXCEL)
    except Exception as e:
        print("❌ Error al leer el archivo de humedad:", e)
        return pd.DataFrame()

app = Flask(__name__, template_folder='.')

@app.route("/")
def index():
    datos = cargar_datos()
    estado_actual = "Sin datos"
    if not datos.empty:
        ultimo = datos.tail(1)
        porcentaje = ultimo["Humedad (%)"].values[0]
        estado = ultimo["Estado"].values[0]
        estado_actual = f"{porcentaje}% - {estado}"
    return render_template_string(open("index.html", encoding="utf-8").read(), estado=estado_actual)

@app.route("/preguntar", methods=["POST"])
def preguntar():
    datos = cargar_datos()
    mensaje = request.json.get("mensaje", "")
    if datos.empty:
        return jsonify({"respuesta": "No se pudieron cargar los datos de humedad 😢."})
    resumen = datos.tail(10).to_string(index=False)
    prompt = f"""Eres un asistente agrícola experto en cultivos de tomate. 
Estos son los datos recientes de humedad del suelo:

{resumen}

Responde lo siguiente: {mensaje}
"""
    respuesta = model.generate(prompt, max_tokens=200)
    return jsonify({"respuesta": respuesta.strip()})

@app.route("/style.css")
def style():
    return send_file("style.css")

if __name__ == "__main__":
    app.run(debug=True)
