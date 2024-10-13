import java.io.*;
import java.net.*;

public class StockClient {

    public static void main(String[] args) {
        String serverAddress = "127.0.0.1"; // L'adresse IP du serveur
        int port = 9999; // Le port du serveur

        try (Socket socket = new Socket(serverAddress, port)) {
            // Configuration des flux d'entrée et de sortie
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            // Envoi de l'id_employé
            String employee_id = "123"; // Changer cet id pour tester d'autres cas
            System.out.println("Envoi de l'id_employé: " + employee_id);
            out.println(employee_id);
            System.out.println("Réponse du serveur: " + in.readLine()+"\n");

            // Envoi de l'id_stock
            String stock_id = "456"; // Changer cet id pour tester d'autres cas
            System.out.println("Envoi de l'id_stock: " + stock_id);
            out.println(stock_id);
            System.out.println("Réponse du serveur: " + in.readLine() +"\n");

            // Envoi de la demande de modification
            String modification = "789,10"; // Opération ID et Quantité
            System.out.println("Envoi de la modification: " + modification);
            out.println(modification);
            System.out.println("Réponse du serveur: " + in.readLine()+"\n");

        } catch (IOException e) {
            System.err.println("Erreur de connexion: " + e.getMessage());
        }
    }
}
