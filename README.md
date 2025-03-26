# TBDMProject

This project facilitates the conversion of Industry Foundation Classes (IFC) files into a Neo4j graph database, 
enabling enhanced analysis and visualization of building information models (BIM).

## Requirements

- Python Version: 3.8.0
- Libraries
  1. **_IfcOpenShell_**-python 0.6.0 for Python 3.8 64-bit Windows
  2. **_py2neo_**
  3. **_Neo4j Graph Data Science (GDS) Library_**: facilitates the execution of advanced graph algorithms and machine learning workflows within the Neo4j environment.
- Graph Database:
  - Neo4j

## Installation
1. Clone the Repository:
    ```
    git clone https://github.com/Nobuho/IFC-Neo4j-converter.git
    ```
2. Install Required Libraries:
- **IfcOpenShell-python**: Download the appropriate version for Python 3.8 64-bit Windows from https://ifcopenshell.org/downloads.html
- **py2neo**: Install via pip:
   ```
   pip install py2neo
   ```
- **graphdatascience**: Install via pip:
   ```
   pip install graphdatascience

   ```
  This client enables seamless integration with the Neo4j Graph Data Science (GDS) library, allowing for advanced graph algorithms and machine learning workflows directly from Python.


## Setting Up Neo4j with Docker Compose
To deploy a Neo4j instance using Docker Compose:
1. Create a docker-compose.yml File:
   ```
   services:
   neo4j:
   image: neo4j:5.18
   container_name: neo4j_container
   restart: unless-stopped
   environment:
   NEO4J_AUTH: neo4j/diegodiego
   NEO4J_dbms_memory_pagecache_size: 1G
   NEO4J_dbms_memory_heap_initial__size: 512m
   NEO4J_dbms_memory_heap_max__size: 1G
   NEO4JLABS_PLUGINS: '["graph-data-science"]'
   NEO4J_dbms_security_procedures_unrestricted: "gds.*"
   NEO4J_dbms_security_procedures_allowlist: "gds.*"
   ports:
   - "7474:7474"
   - "7687:7687"
   volumes:
   - neo4j_data:/data
   - neo4j_logs:/logs
   - neo4j_conf:/var/lib/neo4j/conf
   - neo4j_plugins:/plugins

   volumes:
   neo4j_data:
   neo4j_logs:
   neo4j_conf:
   neo4j_plugins:
   ```

2. Deploy Neo4j:
In the directory containing the docker-compose.yml file, exe

```
docker-compose up -d
```


## Usage

1. Start the Neo4j Database
2. input Neo4j database username and password
    ```
    graph = Graph(auth=('neo4j', 'diegodiego'))
    ```
3. To inserte IFC file, run classes into package "ifc_neo4j_converter"
4. To analyze the graph create before, run classes into the package "ifc_analyzer"
5. **Class CentralityAnalyzer**.
   The betweenness centrality analysis measures how often a node lies along the shortest paths between other nodes in the graph. A node with a high score is a key point for connecting entities.
   
    ####     Requirements
    Do query cyber:

    ```
   CALL gds.graph.project(
   'IfcOpenHouseGraph',  // Nome del grafo
   '*', // Tutti i nodi
   '*'  // Tutte le relazioni
   );
    ```

6. The package "output" is used to archive output files, created by analyze classes.

## Notes

- **Performance**: The time required for node and edge creation in Neo4j depends on the size of the IFC file. Larger files will take more time to process.

- **Compatibility**: Ensure that all software versions are compatible. The specified versions in this document have been tested.

- **Security**: The NEO4J_AUTH environment variable in the docker-compose.yml file sets the default username and password for Neo4j. It's advisable to change these credentials for production environments.

- **Documentation**: For comprehensive guidance on using the GDS Python client, refer to the official documentation https://neo4j.com/docs/graph-data-science-client/current/.