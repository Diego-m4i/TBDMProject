import os
import json
import ifcopenshell

class IfcAnalyzer:
    def __init__(self, ifc_file_path, output_dir):
        """
        Inizializza l'analizzatore con il percorso del file IFC e la directory di output.
        """
        self.ifc_file_path = ifc_file_path
        self.output_dir = output_dir
        self.walls = []
        self.spatial_structures = []

    def analyze(self):
        """
        Analizza il file IFC per estrarre informazioni su muri e strutture spaziali.
        """
        ifc_file = ifcopenshell.open(self.ifc_file_path)

        # Analizza le entità IfcWallStandardCase
        for entity in ifc_file:
            if entity.is_a('IfcWallStandardCase'):
                wall_data = {
                    'id': entity.id(),
                    'name': entity.Name,
                    'overall_width': getattr(entity, 'OverallWidth', None),
                    'overall_height': getattr(entity, 'OverallHeight', None),
                    'material': self.get_material(entity)
                }
                self.walls.append(wall_data)

            # Analizza le relazioni IfcRelContainedInSpatialStructure
            elif entity.is_a('IfcRelContainedInSpatialStructure'):
                spatial_data = {
                    'id': entity.id(),
                    'relating_structure': entity.RelatingStructure.Name if entity.RelatingStructure else None,
                    'related_elements': [e.Name for e in entity.RelatedElements]
                }
                self.spatial_structures.append(spatial_data)

    def get_material(self, wall_entity):
        """
        Estrae il materiale associato a un muro, se presente.
        """
        if hasattr(wall_entity, 'HasAssociations'):
            for assoc in wall_entity.HasAssociations:
                if assoc.is_a('IfcRelAssociatesMaterial'):
                    material = assoc.RelatingMaterial
                    if material and material.is_a('IfcMaterial'):
                        return material.Name
        return None

    def get_walls(self):
        """
        Restituisce la lista dei muri analizzati.
        """
        return self.walls

    def get_spatial_structures(self):
        """
        Restituisce la lista delle strutture spaziali analizzate.
        """
        return self.spatial_structures

    def export_to_json(self):
        """
        Esporta le proprietà estratte in un file JSON nella directory di output.
        """
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                print(f"Directory '{self.output_dir}' creata con successo.")
            except Exception as e:
                print(f"Errore nella creazione della directory '{self.output_dir}': {e}")
                return

        output_json_path = os.path.join(self.output_dir, "NUOVO.json")
        data = {
            'walls': self.walls,
            'spatial_structures': self.spatial_structures
        }
        try:
            with open(output_json_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Dati esportati con successo in '{output_json_path}'.")
        except Exception as e:
            print(f"Errore durante l'esportazione dei dati in '{output_json_path}': {e}")

def main():
    # Percorso al file IFC
    ifc_file_path = r"C:\Users\marin\UNIVERSITÁ\TBDM\IFC-Neo4j-converter\ifc_files\IfcOpenHouse_original.ifc"
    # Directory di output per il file JSON
    output_dir = r"C:\Users\marin\UNIVERSITÁ\TBDM\IFC-Neo4j-converter\output"

    # Verifica se il file IFC esiste
    if not os.path.exists(ifc_file_path):
        print(f"Errore: Il file IFC '{ifc_file_path}' non esiste.")
        return

    # Crea un'istanza della classe IfcAnalyzer
    analyzer = IfcAnalyzer(ifc_file_path, output_dir)

    # Estrai le proprietà dal file IFC
    analyzer.analyze()

    # Esporta le proprietà in un file JSON
    analyzer.export_to_json()

if __name__ == "__main__":
    main()
