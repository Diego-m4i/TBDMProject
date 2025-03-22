from flask import Flask, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

# Connessione al database Neo4j
uri = "bolt://localhost:7687"  # Cambia se necessario
username = "neo4j"
password = "diegodiego"  # Usa la tua password Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

# Funzione per eseguire la query Cypher
def run_cypher_query(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return [record.data() for record in result]

@app.route('/run-cypher', methods=['POST'])
def run_query():
    data = request.get_json()  # Ottieni il corpo della richiesta JSON
    cypher_query = data.get('query')  # Estrai la query Cypher
    if not cypher_query:
        return jsonify({"error": "Query Cypher mancante!"}), 400

    try:
        result = run_cypher_query(cypher_query)  # Esegui la query
        return jsonify(result)  # Ritorna i risultati in formato JSON
    except Exception as e:
        # In caso di errore nell'eseguire la query
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
