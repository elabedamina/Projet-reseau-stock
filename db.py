import socket
import sys
import psycopg2

# Function to connect the network server to the database
def connexion():
    try: 
        print("Connecting to the database...")
        connection = psycopg2.connect(
            dbname="achiriaktham_tp_res_bdd",
            user="achiriaktham",
            password="MZpcA6zM9xh375x",
            host="postgresql-achiriaktham.alwaysdata.net",
            
            port=5432
        )
        return connection
    except psycopg2.Error as error:
        print("Error connecting to the database:", error) 
        sys.exit(1)

def main():
    print("Starting main function...")
    connection = connexion()
    cur = connection.cursor()

    # # Execute a query to retrieve all tables in the 'public' schema
    # # cur.execute("""
    # #     SELECT table_name
    # #     FROM information_schema.tables
    # #     WHERE table_schema = 'public'
    # # """)

    # tables = cur.execute("SELECT * FROM stock WHERE id_stock = 2;")
    # tables = cur.fetchall()
    
    # # Print each table name
    # for table in tables:
    #     print("here's",table)


    import socket

# Connection details
    server_address = "127.0.0.1"
    server_port = 9999

    # Create a message longer than 1024 bytes (e.g., 1025 'A's)
    overflow_message = "A" * 1025

    # Connect to the server and send the message
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        print("Connected to server.")

        # Send the overflow message
        client_socket.sendall(overflow_message.encode('utf-8'))
        print("Overflow message sent.")

        # Attempt to receive the server's response
        response = client_socket.recv(1024).decode('utf-8')
        print("Server response:", response)

    finally:
        client_socket.close()
        print("Connection closed.")


    cur.close()
    connection.close()
    print("Connection closed with the database.")

# Ensuring that main() is called only when this script is executed directly
if __name__ == "__main__":
    main()
