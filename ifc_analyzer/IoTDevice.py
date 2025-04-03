from py2neo import Graph, Node, Relationship
import ifcopenshell

class IoTDevice:
    def __init__(self, device_id, device_type, properties=None):
        self.device_id = device_id
        self.device_type = device_type
        self.properties = properties if properties else {}

    def create_node(self, graph):
        """
        Crea un nodo IoTDevice nel database Neo4j.
        """
        print(f"Creazione del nodo IoTDevice con ID: {self.device_id}")

        # Creazione nodo IoTDevice
        iot_node = Node("IoTDevice", device_id=self.device_id, device_type=self.device_type)

        # Aggiunge proprietà extra
        for key, value in self.properties.items():
            iot_node[key] = value

        graph.create(iot_node)
        return iot_node

def add_iot_to_ifc_node(graph, ifc_file_path, target_node_id, iot_device):
    """
    Aggiunge un dispositivo IoT a un nodo IfcNode nel grafo Neo4j.
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

# Creazione del dispositivo IoT
iot_device = IoTDevice(device_id="MK-01", device_type="TemperatureSensor", properties={"temperature": 22.5, "unit": "C"})

# Aggiunta al grafo Neo4j
add_iot_to_ifc_node(graph, ifc_path, target_ifc_node_id, iot_device)
