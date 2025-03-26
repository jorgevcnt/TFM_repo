import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool 
import os
from fpdf import FPDF
from langchain_openai import AzureChatOpenAI
import json
from models.database import *
from sqlalchemy.orm import Session
from models.models import Proveedor
import imaplib
import email
from email.header import decode_header

KEY = os.getenv("KEY")
VERSION = os.getenv("VERSION")
MODELO = os.getenv("MODELO")
ENDPOINT = os.getenv("ENDPOINT")
MAIL_KEY = os.environ.get("MAIL_KEY")
MAIL = os.environ.get("MAIL")
MAIL_ENVIO = os.environ.get("MAIL_ENVIO")

llm = AzureChatOpenAI(
    api_key = KEY,
    api_version = VERSION,
    azure_endpoint = ENDPOINT,
    azure_deployment = MODELO,
    request_timeout = 15
    )

@tool
def enviar_correo(asunto: str, mensaje: str, filename: str =None):
    """
    Envía un correo electrónico utilizando SMTP con Gmail.
    
    Parámetros:
    - asunto: Asunto del correo.
    - mensaje: Cuerpo del mensaje.
    - filename: Archivo adjunto
    """
    try:
        # Configuración del servidor SMTP de Gmail
        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 587

        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = MAIL
        msg["To"] = MAIL_ENVIO # En entorno de producción, se enviará al destinatario asignado en la transición
        msg["Subject"] = asunto
        msg.attach(MIMEText(mensaje, "plain"))

        # Adjuntar PDF si se especifica
        if filename:
            with open(filename, "rb") as f:
                adjunto = MIMEApplication(f.read(), _subtype="pdf")
                adjunto.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(adjunto)


        # Conectar al servidor SMTP
        servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
        servidor.starttls()  # Seguridad con TLS
        servidor.login(MAIL, MAIL_KEY)  # Autenticación

        # Enviar el correo
        servidor.sendmail(MAIL, MAIL_ENVIO, msg.as_string())
        servidor.quit()

        print(f"✅ Correo enviado correctamente a {MAIL_ENVIO}")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

@tool
def generar_pdf_proveedor(filename, datos):
    """
    Genera un archivo PDF con los datos de un proveedor.
    
    Parámetros:
    - filename: Nombre del archivo PDF.
    - datos: Diccionario con los datos del proveedor.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='', size=12)

    pdf.cell(200, 10, "Informe de Nuevo Proveedor", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, f"Proveedor: {datos['nombre_proveedor']}", ln=True)
    pdf.cell(200, 10, f"ID Pedido: {datos['id_pedido']}", ln=True)
    pdf.cell(200, 10, f"Presupuesto: {datos['presupuesto']} {datos['id_moneda']}", ln=True)
    pdf.cell(200, 10, f"Tipo de Compra: {datos['tipo_compra']}", ln=True)

    pdf.output(filename)
    print(f"📄 PDF generado: {filename}")

@tool 
def insertar_proveedores(datos: str) -> str:
    """
    Inserta la informacion del proveedor en la base de datos.
    """
    session = Session(bind=engine)

    datos = json.loads(datos)

    # Comprobacion del que el proveedor no exista
    proveedor_existente = session.query(Proveedor).filter_by(email=datos["email"]).first()
    if proveedor_existente:
        session.close()
        return "El proveedor ya existe."
    nuevo_proveedor = Proveedor(
        nombre=datos["nombre"], 
        email=datos["email"], 
        contacto=datos["contacto"]
        )
    session.add(nuevo_proveedor)
    session.commit()
    session.close()

    return "Insertado correctamente."

@tool
def leer_bandeja_entrada():
    """
    Lee los últimos n correos de la bandeja de entrada.
    """

    # Conectarse al servidor
    n=3
    servidor="imap.gmail.com"
    mail = imaplib.IMAP4_SSL(servidor)
    mail.login(MAIL, MAIL_KEY)
    mail.select("inbox")

    # Buscar todos los correos
    _, mensajes = mail.search(None, "ALL")
    mensajes = mensajes[0].split()

    print(f"📥 Total de correos: {len(mensajes)}\n")

    for i in mensajes[-n:]:
        _, data = mail.fetch(i, "(RFC822)")
        mensaje = email.message_from_bytes(data[0][1])

        # Obtener asunto
        asunto, cod = decode_header(mensaje["Subject"])[0]
        if isinstance(asunto, bytes):
            asunto = asunto.decode(cod or "utf-8")

        # Obtener remitente
        de = mensaje.get("From")

        # Mostrar contenido
        cuerpo = ""
        if mensaje.is_multipart():
            for parte in mensaje.walk():
                tipo = parte.get_content_type()
                disp = str(parte.get("Content-Disposition"))
                if tipo == "text/plain" and "attachment" not in disp:
                    cuerpo = parte.get_payload(decode=True).decode()
                    break
        else:
            cuerpo = mensaje.get_payload(decode=True).decode()

        resumen = f"Asunto: {asunto}\nDe: {de}\nContenido: {cuerpo[:500]}"
    mail.logout()
    return resumen
