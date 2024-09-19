import smtplib

def test_smtp_connection(host, port):
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        server.quit()
        print(f"Successfully connected to {host} on port {port}.")
    except Exception as e:
        print(f"Failed to connect to {host} on port {port}. Error: {e}")

test_smtp_connection('smtp.gmail.com', 587)
