import os
import re
import xml.etree.ElementTree as ET

def parse_svg(content: bytes) -> dict[str, list]:
    """
    Принимает содержимое SVG в виде байтов, распарсивает его и возвращает словарь с найденными объектами.
    """
    # Парсим XML из строки (предполагается, что SVG закодирован в UTF-8)
    tree = ET.ElementTree(ET.fromstring(content.decode('utf-8')))
    root = tree.getroot()
    
    objects = {
        'tables': [],
        'seats': []
    }

    # Определения соответствия цвета и уровня доступа
    seat_access_levels = {
        '#D9D9D9': 'GUEST',
        '#55C4FF': 'STANDARD',
        '#F8DB00': 'PRO'
    }

    counter = 1
    
    for elem in root.iter():
        if elem.tag.endswith('rect'):
            fill = elem.attrib.get('fill', '').strip()

            if fill in ['#D9D9D9', '#9D9797', '#55C4FF', '#F8DB00', '#FF8D71']:
                # Если цвет равен #9D9797, объект считается столом, иначе — сиденьем
                obj_type = 'table' if fill == '#9D9797' else 'seat'

                x = float(elem.attrib.get('x', 0))
                y = float(elem.attrib.get('y', 0))
                width = float(elem.attrib.get('width', 0))
                height = float(elem.attrib.get('height', 0))
                rx = float(elem.attrib.get('rx', 1))
                
                # Извлекаем угол поворота из атрибута transform, если он есть
                transform = elem.attrib.get('transform', '')
                rotation = 0.0
                if transform.startswith('rotate'):
                    match = re.search(r'rotate\(\s*([-\d.]+)', transform)
                    if match:
                        rotation = float(match.group(1))
                
                if obj_type == 'seat':
                    # Если цвет равен #FF8D71, то это AUDIENCE и уровень доступа берём для PRO
                    if fill == '#FF8D71':
                        seat_access_level = seat_access_levels['#F8DB00']
                        seat_type = 'AUDIENCE'
                    else:
                        seat_access_level = seat_access_levels[fill]
                        seat_type = 'OPENSPACE'
                    
                    objects['seats'].append({
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'rx': rx,
                        'rotation': rotation,
                        'seat_access_level': seat_access_level,
                        'seat_type': seat_type,
                        'seat_id': str(counter)
                    })

                    counter += 1
                else:
                    objects['tables'].append({
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'rx': rx,
                        'rotation': rotation
                    })
                    
    return objects