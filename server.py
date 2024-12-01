import socket
import sys
import psycopg2
import argparse
import time
import logging

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_log.txt'),
        logging.StreamHandler()
    ]
)

MAX_BUFFER_SIZE = 10  # maximum buffer size for client messages

def connexion():
    try: 
        connection = psycopg2.connect(
            dbname="achiriaktham_tp_res_bdd",
            user="achiriaktham",
            password="MZpcA6zM9xh375x",
            host="postgresql-achiriaktham.alwaysdata.net",
            port=5432
        )
        logging.info("Connexion à la base de données réussie.")
        return connection
    except psycopg2.Error as error:
        logging.error(f"Erreur lors de la connexion à la base de données: {error}")
        sys.exit(1)

def receive_data(client_socket):
    """Receives data from client, handling buffer overflow attempts."""
    try:
        data = client_socket.recv(1025).decode('utf-8')
        if len(data) > MAX_BUFFER_SIZE:
            raise ValueError("Buffer overflow attempt detected.")
        return data.strip()
    except (ValueError, socket.error) as e:
        logging.warning(f"Erreur de sécurité: {e}")
        client_socket.send("Erreur : Données envoyées dépassent la taille maximale autorisée.\n".encode('utf-8'))
        client_socket.close()
        return None

def is_db_connected(connection):
    """Function to check if the database connection is still active."""
    try:
        # Try executing a simple query to test if the connection is still active
        with connection.cursor() as cur:
            cur.execute("SELECT 1;")
        return True
    except psycopg2.OperationalError:
        return False

def handle_client(cur, conn, client_socket):
    
    try :  

        client_socket.settimeout(60)  # Timeout after 1 min of inactivity

        # Réception de l'id_employé
        employee_id = receive_data(client_socket)
        if not employee_id:
            logging.info("Le client s'est déconnecté.")
            return
       
        try:
            employee_id_value = int(employee_id)  # Attempt to convert to an integer
        except ValueError:
            # Handle the case where conversion fails
            logging.warning("La valeur fournie pour l'ID employé n'est pas un nombre valide.")
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            client_socket.close()
            return
       
        logging.info(f"--> Reçu id_employé: {employee_id_value}")

        if not is_db_connected(conn):
            logging.error("Perte de connexion à la bd.")
            client_socket.send("Erreur : Perte de connexion à la bd.\n".encode('utf-8'))
            return
         
        # Vérifier l'employé dans la base de données
       
        cur.execute("SELECT * FROM employe WHERE id_employe = %s;",(employee_id_value,))
        employee = cur.fetchone()
    
        if employee: # the employee exists in the database
            client_socket.send("Identification réussie\n".encode('utf-8'))
        else:
            logging.warning(f"Employé introuvable avec id_employé: {employee_id_value}")  
            client_socket.send("Erreur : Employé introuvable\n".encode('utf-8'))
            return
        
        # Réception de l'id_stock
        stock_id = receive_data(client_socket)
        
        if not stock_id:
            logging.info("Le client s'est déconnecté.")
            return
        
        try:
            stock_id_value = int(stock_id)  # Attempt to convert to an integer
        except ValueError:
            # Handle the case where conversion fails
            logging.warning("La valeur fournie pour l'ID stock n'est pas un nombre valide.")
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            client_socket.close()
            return
        
        logging.info(f"--> Reçu id_stock: {stock_id_value}.")
        
        if not is_db_connected(conn):
            logging.error("Perte de connexion à la bd.")
            client_socket.send("Erreur : Perte de connexion à la bd.\n".encode('utf-8'))
            return
         
        # Vérifier le stock dans la base de données
        cur.execute("SELECT qte FROM lotstockage WHERE id_stock = %s;",(stock_id_value,))
        stock = cur.fetchone()

        if stock:
            quantity = stock[0]
            client_socket.send(f"Stock trouvé, la quantité restante est : {quantity}\n".encode('utf-8'))

        else:
            logging.warning(f"Stock introuvable pour id_stock: {stock_id_value}")
            client_socket.send("Erreur : Stock introuvable\n".encode('utf-8'))
            client_socket.close()
            return
        
        # Réception de la demande de modification de stock
        modification = receive_data(client_socket)
        
        if not modification:
            logging.info("Le client s'est déconnecté.")
            return
        
        logging.info(f"Reçu modification: {modification}.")

        try:
            modification_value = int(modification)  # Attempt to convert to an integer
            if modification_value != 1 and modification_value != 2:
                client_socket.send("Erreur : Aucune operation ne correspond a votre demande !\n".encode('utf-8'))
                logging.warning("Opération invalide choisie.")
                client_socket.close()
                return
            else :
                if modification_value == 1:
                    client_socket.send("> Vous avez choisi l'operation entree\n".encode('utf-8'))
                elif modification_value == 2:
                    client_socket.send("> Vous avez choisi l'operation sortie\n".encode('utf-8'))                    

        except ValueError:
            # Handle the case where conversion fails
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            logging.warning("La valeur fournie pour la modification n'est pas valide.")
            client_socket.close()
            return
        
        qte_modifie = receive_data(client_socket)
        
        if not qte_modifie:
            logging.info("Le client s'est déconnecté.")
            return
        
        logging.info(f"Reçu quantité à modifier: {qte_modifie}")

        try:
            qte_modifie_value = int(qte_modifie)  # Attempt to convert to an integer

            if qte_modifie_value < 0:
                client_socket.send("Erreur : vous avez introduit un nombre négatif !\n".encode('utf-8'))
                logging.warning("La valeur fournie pour la modification n'est pas valide.")                
                client_socket.close()  
                return

        except ValueError: # Handle the case where conversion fails
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            logging.warning("La valeur fournie pour la modification n'est pas valide.")

            client_socket.close() 
            return

        if not is_db_connected(conn):
            logging.error("Perte de connexion à la bd.")
            client_socket.send("Erreur : Perte de connexion à la bd.\n".encode('utf-8'))
            return

        if int(modification) == 1 : # une entrée
            cur.execute("UPDATE lotstockage SET qte = qte + %s WHERE id_stock = %s;", (qte_modifie_value, stock_id))
            cur.execute(
                "INSERT INTO historiquemodification (motif, qte_modifie, id_employe, id_stock) VALUES ('entrée du stock', %s, %s, %s)",
                (qte_modifie_value, employee_id, stock_id)
            )
            conn.commit()
            logging.info("Mise à jour du stock réussie")
            client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
        else : # une sortie
            if (stock[0] <= 0) or (stock[0] - qte_modifie_value < 0):
                logging.info("Mise à jour du stock impossible")
                client_socket.send("Mise à jour du stock impossible, quantite insuffisante\n".encode('utf-8'))
            else:
                cur.execute("UPDATE lotstockage SET qte = qte - %s WHERE id_stock = %s;",(qte_modifie_value,stock_id,))
                cur.execute(
                "INSERT INTO historiquemodification (motif, qte_modifie, id_employe, id_stock) VALUES ('sortie du stock', %s, %s, %s)",
                (qte_modifie_value, employee_id, stock_id)
            )
                conn.commit()
                logging.info("Mise à jour du stock réussie")
                client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
    
    except socket.timeout:
        logging.warning("Le client a dépassé le délai d'attente.")
        client_socket.send("Connection timed out due to inactivity.\n".encode('utf-8'))
        
    except (ConnectionResetError, ConnectionAbortedError):
        logging.warning("La connexion client a été réinitialisée ou abandonnée.")

    except Exception as e :
        logging.error(f"Erreur lors du traitement du client: {e}")
        client_socket.send("Erreur lors du traitement de votre demande.\n".encode('utf-8'))
    
    finally:
        logging.info("Fermeture de la connexion avec le client.")
        client_socket.close()  # Ensure the socket is closed regardless of success or failure

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Start the stock management server.")
    parser.add_argument('--host', type=str, default="127.0.0.1", help="IP address of the server (default: 127.0.0.1).")
    parser.add_argument('--port', type=int, default=9999, help="Port number of the server (default: 9999).")
    args = parser.parse_args()

    # Use the provided host and port
    host = args.host
    port = args.port
    
    logging.info(f"Serveur démarrant sur {host}:{port}...") 
    
    print("> Connecting to the database...")
    connection = connexion()
    
    print(">> Connection with the database established.")
    cur = connection.cursor()
    try :
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        server.settimeout(60)  # Set a 1-minute timeout for accepting connections

        print("> Serveur en attente de connexion...")
        client_socket, addr = server.accept()
        print(f">> Connexion acceptée de {addr}")
        handle_client(cur, connection, client_socket) 

        server.close()
        print(">> Server socket closed.")

    except OSError as e:
        if e.winerror == 10013: 
            logging.error("Erreur : Le port est déjà utilisé.")
        elif e.winerror == 10049: 
            logging.error("Erreur : L'adresse IP spécifiée est invalide.")
        else:
            logging.error(f"Erreur réseau inattendue : {e}")
        sys.exit(1)

    
    
    finally:
        cur.close() 
        connection.close() 
        logging.info(">> Connexion fermé avec la base de données")
        

if __name__ == "__main__":
    main()
