import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool 
import os
from fpdf import FPDF

MAIL_KEY = os.environ.get("MAIL_KEY")
MAIL = os.environ.get("MAIL")

@tool
def enviar_correo(destinatario, asunto, mensaje, remitente=MAIL, clave= MAIL_KEY):
    """
    Envía un correo electrónico utilizando SMTP con Gmail.
    
    Parámetros:
    - destinatario: Email del destinatario.
    - asunto: Asunto del correo.
    - mensaje: Cuerpo del mensaje.
    - remitente: (Opcional) Tu dirección de correo de Gmail.
    """
    try:
        # Configuración del servidor SMTP de Gmail
        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 587

        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = remitente
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(mensaje, "plain"))

        # Conectar al servidor SMTP
        servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
        servidor.starttls()  # Seguridad con TLS
        servidor.login(remitente, clave)  # Autenticación

        # Enviar el correo
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()

        print(f"✅ Correo enviado correctamente a {destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

# Ejemplo de uso
enviar_correo(
    destinatario="jorgevicentejuan@gmail.com",
    asunto="Prueba de correo",
    mensaje="Hola, esto es un correo de prueba enviado desde Python."
)


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