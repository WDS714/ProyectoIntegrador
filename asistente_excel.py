from gpt4all import GPT4All
import pandas as pd
import os


modelo_nombre = "Llama-3.2-3B-Instruct-Q4_0.gguf"
modelo_ruta = os.path.join(os.path.expanduser("~"), "gpt4all", "resources", modelo_nombre)
model = GPT4All(modelo_ruta)


archivo_excel = "humedad_datos.xlsx"

try:
    df = pd.read_excel(archivo_excel)
except Exception as e:
    print(f"❌ Error al leer '{archivo_excel}':", e)
    exit()


datos_texto = df.tail(20).to_string(index=False)


instruccion = f"""Eres un asistente agrícola experto en humedad de suelo para cultivos de tomate.
Estos son algunos registros recientes:

{datos_texto}

Responde en español cualquier análisis o interpretación relacionada con estos datos:
"""


print(" IA lista. Escribe tu pregunta (o 'salir' para terminar)")

while True:
    pregunta = input("\nTú: ").strip()
    if pregunta.lower() in ["salir", "exit", "quit"]:
        break

    prompt_completo = instruccion + "\n" + pregunta
    with model.chat_session():
        respuesta = model.generate(prompt_completo, max_tokens=300)
    print("\nIA:", respuesta.strip())
