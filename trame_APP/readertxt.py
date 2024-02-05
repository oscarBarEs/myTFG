import json
import re

data = {}
with open('Resources/info/Berruezo_p2_multiSimsRes.txt', 'r') as file:
    lines = iter(file.readlines())
    for line in lines:
        if line.strip() == "PARÁMETROS DE SIMULACIONES CON REENTRADA:":
            break
    datos = []
    for line in lines:
        
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

with open('output.json', 'w') as json_file:
    json.dump(datos, json_file)