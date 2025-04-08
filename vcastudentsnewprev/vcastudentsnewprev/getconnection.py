import mysql.connector
import json
import os 






class Getconnection:
    def getconnection():
        cred_path = os.path.join(os.path.dirname(__file__), 'config', '.gcpcredentials.json')
        with open(cred_path, 'r') as config_file:
            config = json.load(config_file)
        db_config = config.get('database', {})

        connection = mysql.connector.connect(
            host=db_config.get('host', ''),
            user=db_config.get('user', ''),
            password=db_config.get('password', ''),
            database=db_config.get('database', '')
        )

        # Create a cursor object to execute SQL queries
        
        return connection