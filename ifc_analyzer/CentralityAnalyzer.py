import pandas as pd
from neo4j import GraphDatabase

class CentralityAnalyzer:
    def __init__(self, uri, user, password, graph_name):
        """
        Inizializza la connessione a Neo4j.

        :param uri: URI della connessione Neo4j (es. bolt://localhost:7687)
        :param user: Nome utente per Neo4j
        :param password: Password per Neo4j
        :param graph_name: Nome del grafo su Neo4j
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.graph_name = graph_name
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def get_centrality_data(self, limit=10):
        """
        Calcola la centralità di intermediazione (Betweenness Centrality) e restituisce i nodi
        con i punteggi di centralità più elevati.

        :param limit: Numero massimo di nodi da restituire (default 10)
        :return: Pandas DataFrame con i nodi e i loro punteggi di centralità
        """
        query = f"""
        CALL gds.betweenness.stream('{self.graph_name}')
        YIELD nodeId, score
        MATCH (n) WHERE id(n) = nodeId
        RETURN n.elementId AS id, n.ClassName AS class, score AS centrality
        ORDER BY score DESC
        LIMIT {limit};
        """

        with self.driver.session() as session:
            result = session.run(query)
            # Restituisci i risultati come un DataFrame
            return pd.DataFrame([dict(record) for record in result])

    def export_centrality_data(self, file_path="centrality_results.csv", limit=10):
        """
        Calcola e esporta i dati di centralità in un file CSV.

        :param file_path: Percorso del file CSV dove esportare i risultati
        :param limit: Numero massimo di nodi da restituire (default 10)
        """
        df = self.get_centrality_data(limit)
        df.to_csv(file_path, index=False)
        print(f"Data esportati in {file_path}")

    def close(self):
        """
        Chiude la connessione a Neo4j.
        """
        self.driver.close()


# Utilizzo della classe CentralityAnalyzer
if __name__ == "__main__":
    # Impostazioni di connessione
    uri = "bolt://localhost:7687"  # URL di connessione a Neo4j
    user = "neo4j"  # Nome utente per Neo4j
    password = "diegodiego"  # Password per Neo4j
    graph_name = "IfcOpenHouseGraph"  # Nome del grafo in Neo4j

    # Creazione dell'istanza della classe
    analyzer = CentralityAnalyzer(uri, user, password, graph_name)

    # Ottenere i 10 nodi con la centralità più alta
    centrality_data = analyzer.get_centrality_data(limit=10)
    print(centrality_data)

    # Esportare i risultati in un file CSV
    analyzer.export_centrality_data(file_path="../output/centrality_results.csv", limit=10)

    # Chiudere la connessione
    analyzer.close()
