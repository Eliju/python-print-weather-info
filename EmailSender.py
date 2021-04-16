import smtplib
import ssl
from email.mime.text import MIMEText
import email.utils
import main


def send_email(city_name, weather):
    config_dict = main.get_configs('CamundaAPIConfig.properties')
    smtp_server = config_dict.get('smtp_server')
    port = config_dict.get('port')
    sender_email = config_dict.get('sender_email')
    receiver_email = config_dict.get('receiver_email')
    password = config_dict.get('password')

    subject = "Weather"
    weather_message = """City: """ + city_name + """
    Weather:
    """ + weather
    message = """This message is sent from Python.
    
    """ + weather_message
    msg = MIMEText(message, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Message-ID"] = email.utils.make_msgid(idstring="weather")
    send_to = [receiver_email]
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email.split(","), msg.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
