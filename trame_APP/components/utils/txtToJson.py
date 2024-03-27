import json
import re 
import tempfile

def fetch_data(json_file):
    data = {}
    with tempfile.NamedTemporaryFile(suffix=json_file.name) as path:
        bytes = json_file.content

        with open(path.name, 'wb') as f:
            f.write(bytes)  

        with open(path.name, 'r') as file:
            lines = iter(file.readlines())
            for line in lines:
                if line.strip() == "PARÁMETROS DE SIMULACIONES CON REENTRADA:":
                    break
            datos = []
            print("lines",lines)
            for line in lines:
                print("line")
                parts = line.split('->')
                if(parts.__len__() > 2):
                    data = {}
                    subparts = parts[2].split(',')
                    for i, subpart in enumerate(subparts):
                        if ':' in subpart:
                            key, value = subpart.split(':')
                            data[key.strip()] = value.strip()
                        else:
                            split_subpart = re.split('(\d.*)', subpart, maxsplit=1)
                            if len(split_subpart) > 1:
                                key = split_subpart[0].strip()
                                value = split_subpart[1].strip()
                                data[key] = value
                    datos.append(data)
            print("hola",datos)
            return datos