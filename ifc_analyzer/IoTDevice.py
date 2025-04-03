from py2neo import Graph, Node, Relationship
import ifcopenshell

class IoTDevice:
    def __init__(self, device_id, device_type, properties=None, class_name=None):
        """
        Inizializza il dispositivo IoT.

        :param device_id: ID del dispositivo IoT
        :param device_type: Tipo del dispositivo IoT
        :param properties: Proprietà aggiuntive per il dispositivo IoT (opzionale)
        :param class_name: Classe del dispositivo IoT (opzionale, predefinito è "IoTDevice")
        """
        self.device_id = device_id
        self.device_type = device_type
        self.properties = properties if properties else {}
        self.class_name = class_name if class_name else "IoTDevice"  # Default value is "IoTDevice"

    def create_node(self, graph):
        """
        Crea un nodo IoTDevice nel database Neo4j.

        :param graph: Connessione al database Neo4j
        :return: Il nodo IoTDevice creato
        """
        print(f"Creazione del nodo IoTDevice con ID: {self.device_id}")

        # Creazione nodo IoTDevice con la proprietà 'class_name'
        iot_node = Node("IoTDevice", device_id=self.device_id, device_type=self.device_type, class_name=self.class_name)

        # Aggiunge proprietà extra, se esistono
        for key, value in self.properties.items():
            iot_node[key] = value

        # Salvataggio del nodo nel grafo
        graph.create(iot_node)
        return iot_node


def add_iot_to_ifc_node(graph, ifc_file_path, target_node_id, iot_device):
    """
    Aggiunge un dispositivo IoT a un nodo IfcNode nel grafo Neo4j.

    :param graph: Connessione al database Neo4j
    :param ifc_file_path: Percorso del file IFC (non utilizzato nel codice corrente)
    :param target_node_id: ID del nodo IfcNode a cui collegare il dispositivo IoT
    :param iot_device: Oggetto IoTDevice da aggiungere al nodo IfcNode
    """
    print(f"Lettura file IFC: {ifc_file_path}")
    f = ifcopenshell.open(ifc_file_path)

    print(f"Verifica nodo IfcNode con ID: {target_node_id} nel grafo")
    node_exists = graph.evaluate("MATCH (n:IfcNode {nid: $nid}) RETURN n", nid=target_node_id)

    if not node_exists:
        print(f"ERRORE: Il nodo IfcNode con ID {target_node_id} non esiste in Neo4j.")
        return  # Esce se il nodo non esiste

    # Creazione del nodo IoTDevice
    iot_node = iot_device.create_node(graph)

    print(f"Collegamento del dispositivo IoT {iot_device.device_id} al nodo IfcNode {target_node_id}")

    # Crea la relazione tra IfcNode e IoTDevice
    query = """
    MATCH (n:IfcNode {nid: $node_id}), (iot:IoTDevice {device_id: $device_id})
    CREATE (n)-[:HAS_IOT_DEVICE]->(iot)
    """
    graph.run(query, node_id=target_node_id, device_id=iot_device.device_id)

    print(f"✅ Dispositivo IoT {iot_device.device_id} collegato con successo a IfcNode {target_node_id}!")


# Connessione a Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "diegodiego"))

# Percorso del file IFC
ifc_path = "../ifc_files/IfcOpenHouse_original.ifc"

# ID del nodo IfcNode a cui collegare il dispositivo IoT
target_ifc_node_id = 2319

# Creazione del dispositivo IoT con ClassName
iot_device = IoTDevice(device_id="MK-03", device_type="TemperatureSensor", properties={"temperature": 22.5, "unit": "C"}, class_name="TemperatureSensor")

# Aggiunta al grafo Neo4j
add_iot_to_ifc_node(graph, ifc_path, target_ifc_node_id, iot_device)
