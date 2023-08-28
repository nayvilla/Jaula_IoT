
import time
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import BytesIO
import datetime
import mysql.connector

TOKEN = "BBFF-aApTu105jR9AaoIicOVY50nxput4PE"  # Put your TOKEN here
DEVICE_LABEL = "4c7525360454"  # Put your device label here 
VARIABLE_LABEL_1 = "humedad"  # Put your first variable label here
VARIABLE_LABEL_2 = "luminosidad"  # Put your second variable label here
VARIABLE_LABEL_3 = "temperatura"  # Put your second variable label here
VARIABLE_LABEL_4 = "nh3" 
VARIABLE_LABEL_5 = "turbidez" 
VARIABLE_LABEL_6 = "agua_u1" 
VARIABLE_LABEL_7 = "techo_u2" 
VARIABLE_LABEL_8 = "vitamina_u3" 
VARIABLE_LABEL_9 = "balanceado_u4" 
VARIABLE_LABEL_10 = "engorde_u5" 

# Configura los detalles de conexión a la base de datos
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'flask_login',
}

# Función para obtener los valores de las variables desde Ubidots
def get_variable_values(variable_label):
    # Crea los encabezados para las solicitudes HTTP
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{variable_label}/values/?page_size=1"
    headers = {"X-Auth-Token": TOKEN}

    # Realiza la solicitud HTTP GET
    response = requests.get(url=url, headers=headers)

    # Procesa los resultados
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            value = data['results'][0]['value']
            return value
        else:
            print(f"No se encontraron datos para la variable {variable_label}.")
    else:
        print(f"Error al obtener los datos de la variable {variable_label}. Código de estado: {response.status_code}")

def main():
    print("Obteniendo valores de las variables...")
    hum = []
    lum = []
    tem = []
    nh3 = []
    tur = []
    ul1 = []
    ul2 = []
    ul3 = []
    ul4 = []
    ul5 = []
    for i in range(5):
        humedad = get_variable_values(VARIABLE_LABEL_1)
        luminosidad = get_variable_values(VARIABLE_LABEL_2)
        temperatura = get_variable_values(VARIABLE_LABEL_3)
        nh3_valor = get_variable_values(VARIABLE_LABEL_4)
        turbidez = get_variable_values(VARIABLE_LABEL_5)
        u1 = get_variable_values(VARIABLE_LABEL_6)
        u2 = get_variable_values(VARIABLE_LABEL_7)
        u3 = get_variable_values(VARIABLE_LABEL_8)
        u4 = get_variable_values(VARIABLE_LABEL_9)
        u5 = get_variable_values(VARIABLE_LABEL_10)

        hum.append(humedad)
        lum.append(luminosidad)
        tem.append(temperatura)
        nh3.append(nh3_valor)
        tur.append(turbidez)
        ul1.append(u1)
        ul2.append(u2)
        ul3.append(u3)
        ul4.append(u4)
        ul5.append(u5) 
    if humedad is not None:
        print(f"Datos recibidos de forma correcta en Ubidots")
    # Genera el PDF con los valores obtenidos
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Encabezado y título
    header1 = Paragraph("Universidad Técnica de Ambato", styles['Title'])
    header2= Paragraph("FISEI", styles['Title'])
    header3 = Paragraph("Telecomunicaciones", styles['Title'])
    title = Paragraph("Cuyicultura", styles['Heading1'])

    # Párrafo
    paragraph = Paragraph("Reporte de los sensores de la cuyera", styles['Normal'])

    # Crear tabla con los valores de los sensores
    data = [
        ['Sensores', 'Valor 1', 'Valor 2', 'Valor 3', 'Valor 4', 'Valor 5'],
        ['Humedad (%)', str(hum[0]), str(hum[1]), str(hum[2]), str(hum[3]), str(hum[4])],
        ['Luminosidad (lux)', str(lum[0]), str(lum[1]), str(lum[2]), str(lum[3]), str(lum[4])],
        ['Temperatura (ºC)', str(tem[0]), str(tem[1]), str(tem[2]), str(tem[3]), str(tem[4])],
        ['NH3 (ppm)', str(hum[0]), str(hum[1]), str(hum[2]), str(hum[3]), str(hum[4])],
        ['Turbidez (NTU)', str(nh3[0]), str(nh3[1]), str(nh3[2]), str(nh3[3]), str(nh3[4])],
        ['Nivel de agua (cm)', str(ul1[0]), str(ul1[1]), str(ul1[2]), str(ul1[3]), str(ul1[4])],
        ['Nivel de techo (cm)', str(ul2[0]), str(ul2[1]), str(ul2[2]), str(ul2[3]), str(ul2[4])],
        ['Nivel vitamina (cm)', str(ul3[0]), str(ul3[1]), str(ul3[2]), str(ul3[3]), str(ul3[4])],
        ['Balanceado (cm)', str(ul4[0]), str(ul4[1]), str(ul4[2]), str(ul4[3]), str(ul4[4])],
        ['Engorde (cm)', str(ul5[0]), str(ul5[1]), str(ul5[2]), str(ul5[3]), str(ul5[4])]
    ]
    table = Table(data, colWidths=[100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.gray),  # Primera columna con color gris
        ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),  # Segunda columna con color gris super claro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Agregar una imagen después de la tabla
    image_path = "/home/rsa-key-20230722/tesis_pancho/Dashboard/src/static/img/cuy2.png"  # Replace with the path to your image
    image = Image(image_path, width=100, height=100)

    # Agregar el pie de página con la fecha y hora
    now = datetime.datetime.now()
    footer_text = f"Fecha y hora del reporte: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    footer = Paragraph(footer_text, styles['Normal'])

    # Agregar elementos al documento
    elements = [header1, header2, header3 , title, paragraph, Spacer(1, 20), table, Spacer(1, 30), image, Spacer(1, 160), footer]
    doc.build(elements)

    # Envía el PDF por correo electrónico
    buffer.seek(0)
    pdf_attachment = buffer.getvalue()
    send_email(pdf_attachment)

# Función para enviar el correo electrónico con el PDF adjunto
def send_email(pdf_attachment):
    # Configura tus credenciales de correo electrónico
    email_address = "franciscofreire220@gmail.com"  # Coloca tu dirección de correo electrónico
    email_password = "amnaipvresuhmwrx"  # Coloca tu contraseña
    smtp_server = "smtp.gmail.com"  # Cambia si utilizas un servidor de correo diferente
    smtp_port = 587  # Cambia si es necesario (587 es el puerto predeterminado para TLS)

    # Configura el servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_address, email_password)

    # Crea el mensaje de correo electrónico
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT email FROM user ORDER BY id DESC LIMIT 1;"
    cursor.execute(query)
    result = cursor.fetchone()
    last_email = result[0]
    print(last_email)    
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = last_email  # Cambia por la dirección de destino
    msg['Subject'] = "Reporte de Sensores"

    # Adjunta el PDF al mensaje
    attachment = MIMEApplication(pdf_attachment, _subtype="pdf")
    attachment.add_header('Content-Disposition', 'attachment', filename="reporte_sensores.pdf")
    msg.attach(attachment)

    # Envía el mensaje
    server.sendmail(email_address, last_email, msg.as_string())

    # Cierra la conexión SMTP
    server.quit()

if __name__ == '__main__':
    main()
