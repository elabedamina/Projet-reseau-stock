import java.io.*;
import java.net.*;
import java.util.Scanner;

public class StockClient {

    public static void main(String[] args) {
        String serverAddress = "127.0.0.1"; // Server IP address
        int port = 9999; // Server port
        System.out.println("1) Starting the client...");

        try (Socket socket = new Socket(serverAddress, port)) {
            Scanner scanner = new Scanner(System.in);

            // Set up input and output streams for communication
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            // Send employee_id
            System.out.print(">> Veuillez introduire votre id_employé: ");
            String employee_id = scanner.nextLine(); 
            System.out.println("> Envoi de l'id_employé: " + employee_id + " au serveur...");
            out.println(employee_id);
            String serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                System.out.println("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                System.out.println("--> Fermeture du client.");
                return; // Exit if there is an error or disconnection
            }
            System.out.println("--> Réponse du serveur: " + serverResponse );

            // Send stock_id
            System.out.print(">> Veuillez introduire l'id_stock: ");
            String stock_id = scanner.nextLine();
            System.out.println("> Envoi de l'id_stock: " + stock_id + " au serveur...");
            out.println(stock_id);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                System.out.println("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                System.out.println("--> Fermeture du client...");
                return;
            }
            System.out.println("--> Réponse du serveur: " + serverResponse);

            // Send modification request
            System.out.println(">> Choisissez\n  --1-- : Pour une entrée du stock.\n  --2-- : Pour une sortie du stock. \nVotre choix : ");
            String modification = scanner.nextLine();
            System.out.println("> Envoi de la modification: " + modification + " au serveur...");
            out.println(modification);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                System.out.println("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                System.out.println("--> Fermeture du client...");
                return;
            }
            System.out.println("--> Réponse du serveur: " + serverResponse);

            // Send quantity
            System.out.println(">> Veuillez introduire la quantité à ajouter/enlever du stock : ");
            String quantite = scanner.nextLine();
            System.out.println("> Envoi de la quantité: " + quantite + " au serveur...");
            out.println(quantite);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                System.out.println("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                System.out.println("--> Fermeture du client...");
                return;
            }
            System.out.println("--> Réponse du serveur: " + serverResponse);

            // Close the scanner after completing operations
            scanner.close();
            System.out.println(">> Client closed.");
            System.out.println("----------------------------FIN---------------------------------");

        } catch (IOException e) {
            System.err.println("--> Erreur de connexion: " + e.getMessage());
        }
    }
}
