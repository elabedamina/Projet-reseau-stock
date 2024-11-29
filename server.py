import socket
import sys
import psycopg2
import configparser

MAX_BUFFER_SIZE = 1024  # Define a maximum buffer size for client messages

def connexion():
    try: 
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

def receive_data(client_socket):
    """Receives data from client, handling buffer overflow attempts."""
    try:
        data = client_socket.recv(MAX_BUFFER_SIZE).decode('utf-8')
        if len(data) > MAX_BUFFER_SIZE:
            raise ValueError("Buffer overflow attempt detected.")
        return data.strip()
    except (ValueError, socket.error) as e:
        print(f"Security error: {e}")
        client_socket.send("Erreur : Données envoyées dépassent la taille maximale autorisée.\n".encode('utf-8'))
        client_socket.close()
        return None



def handle_client(cur, conn, client_socket):
    
    try :  

        client_socket.settimeout(300000)  # Timeout after 5 mins of inactivity
   
        # Réception de l'id_employé
        employee_id = receive_data(client_socket)
        if not employee_id:
            print("Client has disconnected.")
            return
        
        print(f"--> Reçu id_employé: {employee_id}")
        
        # Vérifier l'employé dans la base de données
        cur.execute("SELECT * FROM employe WHERE id_employe = %s;",(employee_id,))
        employee = cur.fetchone()
    
        if employee: # the employee exists in the database
            client_socket.send("Identification réussie\n".encode('utf-8'))
        else:
            client_socket.send("Erreur : Employé introuvable\n".encode('utf-8'))
            return
        
        # Réception de l'id_stock
        stock_id = receive_data(client_socket)
        
        if not stock_id:
            print("--> Client has disconnected.")
            return
        
        print(f"--> Reçu id_stock: {stock_id}.")
        
        # Vérifier le stock dans la base de données
        cur.execute("SELECT qte FROM lotstockage WHERE id_stock = %s;",(stock_id,))
        stock = cur.fetchone()

        if stock:
            quantity = stock[0]
            client_socket.send(f"Stock trouvé, la quantité restante est : {quantity}\n".encode('utf-8'))

        else:
            client_socket.send("Erreur : Stock introuvable\n".encode('utf-8'))
            client_socket.close()
            return
        
        # Réception de la demande de modification de stock
        modification = receive_data(client_socket)
        
        if not modification:
            print("--> Client has disconnected.")
            return
        
        print(f"--> Reçu modification: {modification}.")
        
        try:
            modification_value = int(modification)  # Attempt to convert to an integer
            if modification_value != 1 and modification_value != 2:
                client_socket.send("Erreur : Aucune operation ne correspond a votre demande !\n".encode('utf-8'))
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
            client_socket.close()
            return
        
        qte_modifie = receive_data(client_socket)
        
        if not qte_modifie:
            print("--> Client has disconnected.")
            return
        
        print(f"--> Reçu quantite: {qte_modifie}")
        
        try:
            qte_modifie_value = int(qte_modifie)  # Attempt to convert to an integer

            if qte_modifie_value < 0:
                client_socket.send("Erreur : vous avez introduit un nombre négatif !\n".encode('utf-8'))
                client_socket.close()  
                return

        except ValueError: # Handle the case where conversion fails
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            client_socket.close() 
            return


        if int(modification) == 1 : # une entrée
            cur.execute("UPDATE lotstockage SET qte = qte + %s WHERE id_stock = %s;", (qte_modifie_value, stock_id))
            cur.execute(
                "INSERT INTO historiquemodification (motif, qte_modifie, id_employe, id_stock) VALUES ('entrée du stock', %s, %s, %s)",
                (qte_modifie_value, employee_id, stock_id)
            )
            conn.commit()
            client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
        else : # une sortie
            if (stock[0] <= 0) or (stock[0] - qte_modifie_value < 0):
                client_socket.send("Mise à jour du stock impossible, quantite insuffisante\n".encode('utf-8'))
            else:
                cur.execute("UPDATE lotstockage SET qte = qte - %s WHERE id_stock = %s;",(qte_modifie_value,stock_id,))
                cur.execute(
                "INSERT INTO historiquemodification (motif, qte_modifie, id_employe, id_stock) VALUES ('sortie du stock', %s, %s, %s)",
                (qte_modifie_value, employee_id, stock_id)
            )
                conn.commit()

                client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
    
    except socket.timeout:
        print("--> Client timed out due to inactivity.")
        client_socket.send("Connection timed out due to inactivity.\n".encode('utf-8'))
        
    except (ConnectionResetError, ConnectionAbortedError):
        print("--> Client connection was reset or aborted.")


    except Exception as e :
    
        print(f"--> Erreur lors du traitement du client : {e}")
        client_socket.send("Erreur lors du traitement de votre demande.\n".encode('utf-8'))
    
    finally:
    
        client_socket.close()  # Ensure the socket is closed regardless of success or failure

def main():
    # Charger la configuration
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    # Paramètres par défaut
    default_host = "127.0.0.1"
    default_port = 9999

    host = config.get("server", "host", fallback=default_host)
    port = config.getint("server", "port", fallback=default_port)
    
    print(f"1) Serveur démarrant sur {host}:{port}...")  
    print("2) Connecting to the database...")
    connection = connexion()
    
    print(">> Connection with the database established.")
    cur = connection.cursor()
    try :
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print("3) Serveur en attente de connexion...")

    except OSError as e:
        if e.errno == 98: 
            print("Erreur : Le port est déjà utilisé.")
        elif e.errno == 99: 
            print("Erreur : L'adresse IP spécifiée est invalide.")
        else:
            print(f"Erreur réseau inattendue : {e}")
        sys.exit(1)

    client_socket, addr = server.accept()
    print(f">> Connexion acceptée de {addr}")
    handle_client(cur, connection, client_socket) 
    cur.close() 
    connection.close() 
    print(">> Connection closed with the database.")

if __name__ == "__main__":
    main()
