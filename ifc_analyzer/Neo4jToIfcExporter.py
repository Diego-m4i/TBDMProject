from neo4j import GraphDatabase

class Neo4jToIfcExporter:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def fetch_labels_from_neo4j(self):
        """Recupera tutte le etichette dei nodi nel database Neo4j."""
        query = "CALL db.labels()"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["label"] for record in result]

    def fetch_data_for_label(self, label):
        """Recupera tutti i nodi per una determinata etichetta."""
        query = f"MATCH (n:{label}) RETURN n"
        with self.driver.session() as session:
            result = list(session.run(query))
            return result

    def fetch_relationships(self):
        """Recupera tutte le relazioni tra IfcNode e IoTDevice."""
        query = """
        MATCH (n:IfcNode)-[r:HAS_IOT_DEVICE]->(iot:IoTDevice)
        RETURN n.nid AS ifc_id, iot.device_id AS iot_id
        """
        with self.driver.session() as session:
            return list(session.run(query))

    def export_to_ifc(self):
        labels = self.fetch_labels_from_neo4j()

        # Raccolta dei dati da esportare in un dizionario per ordinare per 'nid'
        nodes_to_export = []

        for label in labels:
            print(f"Fetching data for label: {label}")
            data = self.fetch_data_for_label(label)

            for record in data:
                node = record["n"]
                print(f"Node data for label {label}: {dict(node)}")

                class_name = node.get("ClassName")
                nid = node.get("nid")
                if not class_name or not nid:  # Se ClassName o nid mancano, ignora il nodo
                    continue

                device_id = node.get("device_id")
                device_type = node.get("device_type")

                node_data = {
                    'nid': nid,
                    'class_name': class_name,
                    'node': node,
                    'device_id': device_id,
                    'device_type': device_type
                }

                nodes_to_export.append(node_data)

        # Ordinamento dei nodi per 'nid' in ordine crescente
        nodes_to_export.sort(key=lambda x: int(x['nid']))

        # Esportazione dei dati ordinati nel file IFC
        with open('../output/NewIfcOpenHouseGraph.ifc', 'w') as f:
            f.write('ISO-10303-21;\nHEADER;\n')
            f.write('FILE_DESCRIPTION((\'ViewDefinition [CoordinationView]\'),\'2;1\');\n')
            f.write("FILE_NAME('IfcExport.ifc','2024-04-03T12:00:00',(''),('',''),'IfcOpenShell','IfcOpenShell','');\n")
            f.write("FILE_SCHEMA(('IFC2X3'));\n")
            f.write('ENDSEC;\nDATA;\n')

            # Esportazione nodi ordinati
            for node_data in nodes_to_export:
                nid = node_data['nid']
                class_name = node_data['class_name']
                node = node_data['node']
                device_id = node_data['device_id']
                device_type = node_data['device_type']

                if class_name == "IfcCartesianPoint":
                    coordinates = node.get("Coordinates", "0.0,0.0").split(",")
                    f.write(f"# {nid}=IFCARTESIANPOINT({coordinates[0]},{coordinates[1]});\n")
                elif class_name == "IfcDirection":
                    direction = node.get("DirectionRatios", "0.0,0.0,0.0").split(",")
                    while len(direction) < 3:
                        direction.append("0.0")  # Aggiunge 0.0 ai valori mancanti per avere sempre tre componenti
                    f.write(f"# {nid}=IFCDIRECTION({direction[0]},{direction[1]},{direction[2]});\n")
                elif class_name == "IfcExtrudedAreaSolid":
                    f.write(f"# {nid}=IFCEXTRUDEDAREASOLID();\n")
                elif class_name == "IfcPolyline":
                    f.write(f"# {nid}=IFCPOLYLINE();\n")
                elif class_name == "IoTDevice" and device_id and device_type:
                    f.write(f"# {nid}=IOTDEVICE('{device_id}','{device_type}');\n")
                else:
                    f.write(f"# {nid}=IFCELEMENT($,$,'{class_name}');\n")

            # Esportazione delle relazioni IoTDevice-IfcNode
            relationships = self.fetch_relationships()
            for rel in relationships:
                ifc_id = rel["ifc_id"]
                iot_id = rel["iot_id"]
                f.write(f"# REL_{ifc_id}_{iot_id}=IFCRELASSOCIATES($,# {ifc_id},# {iot_id});\n")

            f.write('ENDSEC;\nEND-ISO-10303-21;\n')

if __name__ == "__main__":
    exporter = Neo4jToIfcExporter(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="diegodiego"
    )
    exporter.export_to_ifc()