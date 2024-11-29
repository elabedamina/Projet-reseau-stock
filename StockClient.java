import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.Properties;

public class StockClient {

    public static void main(String[] args) {

        Properties properties = new Properties();

        // Charger les paramètres par défaut
        String defaultHost = "127.0.0.1";
        int defaultPort = 9999;

        try (InputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
        } catch (IOException ex) {
            System.out.println("Fichier de configuration introuvable, utilisation des paramètres par défaut.");
        }

        String serverAddress = properties.getProperty("server.host", defaultHost);
        int port = Integer.parseInt(properties.getProperty("server.port", String.valueOf(defaultPort)));


        System.out.println("1) Starting the client...");
        System.out.println("Connexion au serveur " + serverAddress + " sur le port " + port);

        try (Socket socket = new Socket(serverAddress, port)) {

            System.out.println("Connecté au serveur.");
            Scanner scanner = new Scanner(System.in);

            // Set up input and output streams for communication
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            // Inactivity timeout checker (100 seconds)
            Thread timeoutThread = new Thread(() -> {
                try {
                    Thread.sleep(300000); // 5 mins
                    System.out.println("\n>> Inactivity timeout reached. Closing client.");
                    socket.close(); // Close the socket to trigger any read/write operation to fail
                    System.exit(0); // Exit the application
                } catch (InterruptedException | IOException e) {
                    // If interrupted, the main thread is active, so no action is needed
                }
            });
            timeoutThread.setDaemon(true); // Daemonize the timeout thread so it doesn't block JVM exit
            timeoutThread.start();


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

        } catch (SocketTimeoutException e) {
            System.out.println("Erreur : Temps d'attente dépassé. Le serveur ne répond pas.");
        } catch (UnknownHostException e) {
            System.out.println("Erreur : Le nom de domaine ou l'adresse IP du serveur est introuvable. Vérifiez l'adresse : " + e.getMessage());
        } catch (ConnectException e) {
            System.out.println("Erreur : Impossible de se connecter au serveur. Le port " + port + " est peut-être fermé ou le serveur est hors ligne.");
        }  catch (IllegalArgumentException e) {
            System.out.println("Erreur : Paramètres invalides (port ou adresse incorrects) : " + e.getMessage());
        } catch (IOException e) {
            System.err.println("--> Erreur de connexion: " + e.getMessage());
        } finally {
            System.out.println("Client fermé.");
        }
    }
}

