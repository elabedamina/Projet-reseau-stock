import socket
import sys
import psycopg2

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

def handle_client(cur, conn, client_socket):
    
    try :
   
        # Réception de l'id_employé
        employee_id = client_socket.recv(1024).decode('utf-8')
        print(f"Reçu id_employé: {employee_id}")
        
        # Vérifier l'employé dans la base de données
        cur.execute("SELECT * FROM employe WHERE id_employe = %s;",(employee_id,))
        employee = cur.fetchone()
    
        if employee: # the employee exists in the database
            client_socket.send("Identification réussie\n".encode('utf-8'))
        else:
            client_socket.send("Erreur : Employé introuvable\n".encode('utf-8'))
            return
        
        # Réception de l'id_stock
        stock_id = client_socket.recv(1024).decode('utf-8')
        print(f"Reçu id_stock: {stock_id} \n")
        
        # Vérifier le stock dans la base de données
        cur.execute("SELECT qte FROM stock WHERE id_stock = %s;",(stock_id,))
        stock = cur.fetchone()

        if stock:
            quantity = stock[0]
            client_socket.send(f"Stock trouvé, la quantité restante est : {quantity}\n".encode('utf-8'))

        else:
            client_socket.send("Erreur : Stock introuvable\n".encode('utf-8'))
            client_socket.close()
            return
        
        # Réception de la demande de modification de stock
        modification = client_socket.recv(1024).decode('utf-8')
        print(f"Reçu modification: {modification} \n")
        
        try:
            modification_value = int(modification)  # Attempt to convert to an integer
            if modification_value != 1 and modification_value != 2:
                client_socket.send("Erreur : Aucune operation ne correspond a votre demande !\n".encode('utf-8'))
                client_socket.close()
                return
            else :
                if modification_value == 1:
                    client_socket.send("Vous avez choisi l'operation entree\n".encode('utf-8'))
                elif modification_value == 2:
                    client_socket.send("Vous avez choisi l'operation sortie\n".encode('utf-8'))                    

        except ValueError:
            # Handle the case where conversion fails
            client_socket.send("Erreur : La valeur fournie n'est pas un nombre valide.\n".encode('utf-8'))
            client_socket.close()
            return
        
        qte_modifie = client_socket.recv(1024).decode('utf-8')
        print(f"Reçu quantite: {qte_modifie} \n")
        
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
            cur.execute("UPDATE stock SET qte = qte + %s WHERE id_stock = %s;", (qte_modifie_value, stock_id))
            conn.commit()

            tables = cur.execute("SELECT * FROM stock WHERE id_stock = 2;")
            tables = cur.fetchall()
            
            # Print each table name
            for table in tables:
                print("here's",table)

            client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
        else : # une sortie
            if (stock[0] <= 0) or (stock[0] - qte_modifie_value < 0):
                client_socket.send("Mise à jour du stock impossible, quantite insuffisante\n".encode('utf-8'))
            else:
                cur.execute("UPDATE stock SET qte = qte - %s WHERE id_stock = %s;",(qte_modifie_value,stock_id,))
                conn.commit()

                client_socket.send("Mise à jour du stock reussie\n".encode('utf-8'))
    
    except Exception as e :
    
        print(f"Erreur lors du traitement du client : {e}")
        client_socket.send("Erreur lors du traitement de votre demande.\n".encode('utf-8'))
    
    finally:
    
        client_socket.close()  # Ensure the socket is closed regardless of success or failure


def main():
    print("Starting the server...")

    # Connect to the database
    print("Connecting to the database...")
    connection = connexion()
    print("Connection with the database established.")
    cur = connection.cursor()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9999))
    server.listen(5)
    server.settimeout(60)  # Set a timeout for the server to wait for new connections

    print("Serveur en attente de connexion...")

    try:
        while True:
            try:
                client_socket, addr = server.accept()
                print(f"Connexion acceptée de {addr}")
                
                # Handle client operations
                handle_client(cur, connection, client_socket)
                
                print("En attente d'une nouvelle connexion...")

            except socket.timeout:
                print("Aucune connexion reçue dans le délai imparti. Fermeture du serveur...")
                break

    except KeyboardInterrupt:
        print("\nArrêt manuel du serveur...")
    
    finally:
        cur.close()
        connection.close()
        server.close()
        print("Connection closed with the database and server shut down.")

if __name__ == "__main__":
    main()