import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.logging.*;

public class StockClient {

    // Define logger
    private static final Logger logger = Logger.getLogger(StockClient.class.getName());

    public static void main(String[] args) {
        // Default port value
        String defaultServerAddress = "127.0.0.1";
        int defaultPort = 9999;

        // Check if arguments are provided
        String serverAddress = defaultServerAddress;  // Default server address
        int port = defaultPort;  // Default port

        // If arguments are provided
        if (args.length == 2) {
            serverAddress = args[0];  // First argument: server address
            try {
                port = Integer.parseInt(args[1]);  // Second argument: port number
            } catch (NumberFormatException e) {
                logger.severe("Erreur : Le port doit être un entier valide.");
                return;
            }
        }

        logger.info("1) Starting the client...");
        logger.info("Connexion au serveur " + serverAddress + " sur le port " + port);

        try (Socket socket = new Socket(serverAddress, port)) {

            // Set a timeout of 1 minute (60000 milliseconds)
            socket.setSoTimeout(60000);

            logger.info("Connecté au serveur.");
            Scanner scanner = new Scanner(System.in);

            // Set up input and output streams for communication
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            
            // Get employee_id, ensure it's an integer
            String employee_id = getValidIntegerInput(scanner, "id_employé");

            logger.info("> Envoi de l'id_employé: " + employee_id + " au serveur...");
            out.println(employee_id);
            String serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                logger.warning("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                return; // Exit if there is an error or disconnection
            }
            logger.info("--> Réponse du serveur: " + serverResponse);

            // Get stock_id, ensure it's an integer
            String stock_id = getValidIntegerInput(scanner, "id_stock");

            logger.info("> Envoi de l'id_stock: " + stock_id + " au serveur...");
            out.println(stock_id);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                logger.warning("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                return;
            }
            logger.info("--> Réponse du serveur: " + serverResponse);

            // Get modification choice (1 or 2)
            System.out.println(">> Choisissez\n  --1-- : Pour une entrée du stock.\n  --2-- : Pour une sortie du stock. \nVotre choix : ");
            String modification = scanner.nextLine();

            logger.info("> Envoi de la modification: " + modification + " au serveur...");
            out.println(modification);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                logger.warning("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                return;
            }
            logger.info("--> Réponse du serveur: " + serverResponse);

            // Get quantity, ensure it's an integer
            String quantity = getValidIntegerInput(scanner, "quantité");

            logger.info("> Envoi de la quantité: " + quantity + " au serveur...");
            out.println(quantity);
            serverResponse = in.readLine();

            if (serverResponse == null || serverResponse.contains("Erreur")) {
                logger.warning("--> Réponse du serveur: " + (serverResponse != null ? serverResponse : "Server closed the connection") + "\n");
                return;
            }
            logger.info("--> Réponse du serveur: " + serverResponse);

            // Close the scanner after completing operations
            scanner.close();
            logger.info("Fermeture de la connexion...");
            socket.close();  // fermer la socket et terminer la communication TCP
            logger.info("Connexion fermée.");
            logger.info(">> Client fermé.");
            logger.info("----------------------------FIN---------------------------------");

        } catch (SocketTimeoutException e) {
            logger.severe("Erreur : Temps d'attente dépassé. Le serveur ne répond pas.");
        } catch (UnknownHostException e) {
            logger.severe("Erreur : Le nom de domaine ou l'adresse IP du serveur est introuvable. Vérifiez l'adresse : " + e.getMessage());
        } catch (ConnectException e) {
            logger.severe("Erreur : Impossible de se connecter au serveur. Le port " + port + " est peut-être fermé ou le serveur est hors ligne.");
        } catch (SocketException e) {
            if (e.getMessage().contains("Address already in use")) {
                logger.severe("Erreur : Le port est déjà utilisé. Vérifiez si une autre application utilise le même port.");
            }
        } catch (IllegalArgumentException e) {
            logger.severe("Erreur : Paramètres invalides (port ou adresse incorrects) : " + e.getMessage());
        } catch (IOException e) {
            logger.severe("Erreur de connexion: " + e.getMessage());
        } finally {
            logger.info("Client fermé.");
        }
    }

    // Method to get a valid integer input
    private static String getValidIntegerInput(Scanner scanner, String prompt) {
        String input = "";
        while (true) {
            System.out.print(">> Veuillez introduire " + prompt + " (doit être un entier) : ");
            input = scanner.nextLine();
            try {
                Integer.parseInt(input);
                return input;  // Return the valid integer input
            } catch (NumberFormatException e) {
                logger.warning("Erreur : " + prompt + " doit être un entier valide.");
            }
        }
    }
}
