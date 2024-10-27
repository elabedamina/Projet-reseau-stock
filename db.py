import socket
import sys
import psycopg2

# Function to connect the network server to the database
def connexion():
    try: 
        print("Connecting to the database...")
        connection = psycopg2.connect(
            # dbname="achiriaktham_tp_res_bdd",
            # user="achiriaktham",
            # password="MZpcA6zM9xh375x",
            # host="postgresql-achiriaktham.alwaysdata.net",
            dbname="test",
            user="postgres",
            password="postgres1234",
            host="localhost",
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

    # Execute a query to retrieve all tables in the 'public' schema
    # cur.execute("""
    #     SELECT table_name
    #     FROM information_schema.tables
    #     WHERE table_schema = 'public'
    # """)

    cur.execute("SELECT * FROM public.fournisseur;")
    
    tables = cur.fetchall()

    # Print each table name
    for table in tables:
        print("here's",table)

    # Close the cursor and connection
    cur.close()
    connection.close()
    print("Connection closed with the database.")

# Ensuring that main() is called only when this script is executed directly
if __name__ == "__main__":
    main()
