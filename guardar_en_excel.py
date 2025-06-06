import serial
import openpyxl
import datetime
from openpyxl.utils.exceptions import InvalidFileException
import os


PUERTO = 'COM3'
BAUDIOS = 9600
archivo = os.path.join(os.path.dirname(__file__), "humedad_datos.xlsx")


try:
    arduino = serial.Serial(PUERTO, BAUDIOS)
    print(f"✅ Conectado a {PUERTO}")
except Exception as e:
    print(f"❌ Error al conectar con el puerto {PUERTO}:", e)
    exit()


try:
    libro = openpyxl.load_workbook(archivo)
    hoja = libro.active
except (FileNotFoundError, InvalidFileException):
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(["FechaHora", "Humedad (%)", "Estado"])
    libro.save(archivo)


while True:
    try:
        lectura = arduino.readline().decode().strip()
        if "," in lectura:
            porcentaje, estado = lectura.split(",", 1)
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hoja.append([ahora, int(porcentaje), estado.strip()])
            libro.save(archivo)
            print(f"📥 {ahora} → {porcentaje}% → {estado.strip()}")
    except Exception as e:
        print("❌ Error al guardar datos:", e)
