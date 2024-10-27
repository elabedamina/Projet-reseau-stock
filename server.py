import socket
import sys
import psycopg2


def handle_client(client_socket):
    # Réception de l'id_employé
    employee_id = client_socket.recv(1024).decode('utf-8')
    print(f"Reçu id_employé: {employee_id}")
    
    # Vérifier l'employé dans la base de données (ici on simule une vérification simple)
    if int(employee_id) == 123:
        client_socket.send("Identification reussie\n".encode('utf-8'))
    else:
        client_socket.send("Erreur : Employé introuvable".encode('utf-8'))
        client_socket.close()
        return
    
    # Réception de l'id_stock
    stock_id = client_socket.recv(1024).decode('utf-8')
    print(f"Reçu id_stock: {stock_id} \n")
    
    # Vérifier le stock (on simule une vérification)
    if int(stock_id) == 456:
        client_socket.send("Stock trouve \n".encode('utf-8'))
    else:
        client_socket.send("Erreur : Stock introuvable".encode('utf-8'))
        client_socket.close()
        return
    
    # Réception de la demande de modification de stock
    modification_data = client_socket.recv(1024).decode('utf-8')
    print(f"Reçu modification: {modification_data} \n")
    
    modification_data = client_socket.recv(1024).decode('utf-8')
    print(f"Reçu quantite: {modification_data} \n")
    
    # Simulation d'une mise à jour de stock
    if int(modification_data) > 0:
        client_socket.send("Mise à jour reussie".encode('utf-8'))
    else:
        client_socket.send("Erreur : Stock insuffisant".encode('utf-8'))

    # Fermeture de la connexion
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9999))
    server.listen(5)
    print("Serveur en attente de connexion...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connexion acceptée de {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
