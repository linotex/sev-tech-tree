"""
SEV Tech Tree — game data parser
Parses TechAreas.txt, Components.txt, Facilities.txt from Space Empires V.

Usage:
    python3 scripts/parse_data.py [lang]

    lang  — output language code (default: uk). Output goes to:
              resources/tech_tree_{lang}.json
              resources/components_{lang}.json
              resources/facilities_{lang}.json

The game files must be present in:
    __game/data/TechAreas.txt
    __game/data/Components.txt
    __game/data/Facilities.txt
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
GAME_DATA = ROOT / '__game' / 'data'
OUT = ROOT / 'resources'

LANG = sys.argv[1] if len(sys.argv) > 1 else 'uk'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_game_file(filename: str) -> str:
    path = GAME_DATA / filename
    with open(path, 'r', encoding='utf-16-le') as f:
        return f.read()


def parse_blocks(content: str, name_key: str = 'Название') -> list[dict[str, str]]:
    """
    Split file content into blocks, one per entry.
    Each block is a dict { field_key: value } parsed from lines like:
        FieldName      := Value
    A new block starts whenever a line whose left side (stripped) equals name_key.
    """
    lines = content.split('\n')
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in lines:
        if ':=' not in line:
            continue
        left, _, right = line.partition(':=')
        key = left.strip()
        value = right.strip()

        if key == name_key:
            if current is not None:
                blocks.append(current)
            current = {}

        if current is not None and key:
            # Numbered keys like "Тип способности 1" — keep as-is
            current[key] = value

    if current:
        blocks.append(current)

    return blocks


def get_req_from_formula(formula: str) -> tuple[str, int] | None:
    """
    Extract (tech_name, min_level) from requirement formula.
    Handles:
        Get_Empire_Tech_Level("Name") >= 1
        Get_Empire_Tech_Level("Name") >= (1 + ([%Level%] - 1))
    """
    m = re.search(r'Get_Empire_Tech_Level\("([^"]+)"\)\s*>=\s*\(?(\d+)', formula)
    if m:
        return m.group(1), int(m.group(2))
    return None


# ---------------------------------------------------------------------------
# TechAreas parser
# ---------------------------------------------------------------------------

def parse_tech_areas() -> list[dict]:
    content = read_game_file('TechAreas.txt')
    raw_blocks = parse_blocks(content, name_key='Название')

    # Resolve group/category from header comments isn't reliable —
    # use the existing logic: group = first tech's group field or infer from file order.
    # TechAreas.txt has "Группа" field per tech.

    techs = []
    for b in raw_blocks:
        name = b.get('Название', '').strip()
        if not name:
            continue

        group = b.get('Группа', '').strip()
        category = b.get('Категория', group).strip() or group
        max_level = int(b.get('Максимальный уровень', 1))
        cost = int(b.get('Стоимость уровня', 0))
        start_level = int(b.get('Начальный уровень', 0))
        is_unique = b.get('Уникальная или расовая технология', 'ЛОЖНО').strip().upper() == 'ВЕРНО'

        # Requirements
        req_count = int(b.get('Количество требований', 0))
        requirements = []
        for i in range(1, req_count + 1):
            formula = b.get(f'Формула требований {i}', '')
            result = get_req_from_formula(formula)
            if result:
                tech_name, level = result
                requirements.append({'tech': tech_name, 'level': level})

        techs.append({
            'name': name,
            'group': group,
            'category': category,
            'maxLevel': max_level,
            'costPerLevel': cost,
            'startLevel': start_level,
            'isUnique': is_unique,
            'requirements': requirements,
        })

    return techs


# ---------------------------------------------------------------------------
# Components parser
# ---------------------------------------------------------------------------

def parse_abilities(b: dict, count_key: str = 'Количество способностей') -> list[dict]:
    count = int(b.get(count_key, 0))
    abilities = []
    for i in range(1, count + 1):
        atype = b.get(f'Тип способности {i}', '').strip()
        desc  = b.get(f'Описание способности {i}', '').strip()
        a1    = b.get(f'Способность {i} - Формула количества 1', '0').strip()
        a2    = b.get(f'Способность {i} - Формула количества 2', '0').strip()
        if atype:
            abilities.append({'type': atype, 'description': desc, 'amount1': a1, 'amount2': a2})
    return abilities


def parse_requirements(b: dict) -> list[dict]:
    count = int(b.get('Количество требований', 0))
    reqs = []
    for i in range(1, count + 1):
        formula = b.get(f'Формула требований {i}', '')
        result = get_req_from_formula(formula)
        if result:
            tech_name, level = result
            reqs.append({'tech': tech_name, 'level': level})
    return reqs


def parse_components() -> list[dict]:
    content = read_game_file('Components.txt')
    raw_blocks = parse_blocks(content, name_key='Название')

    components = []
    for b in raw_blocks:
        name = b.get('Название', '').strip()
        if not name:
            continue

        weapon_type = b.get('Тип оружия', 'Нет').strip()
        weapon = None
        if weapon_type and weapon_type != 'Нет':
            weapon = {
                'type': weapon_type,
                'delivery': b.get('Тип доставки оружия', '').strip(),
                'damageType': b.get('Тип повреждений вооружения', '').strip().strip('"'),
                'minDamageFormula': b.get(
                    'Космическое вооружение - Формула модификатора мин. повреждений', '').strip(),
                'maxDamageFormula': b.get(
                    'Космическое вооружение - Формула модификатора макс. повреждений', '').strip(),
            }

        components.append({
            'name': name,
            'description': b.get('Описание', '').strip(),
            'group': b.get('Общая группа', '').strip(),
            'imageNum': int(b.get('Номер изображения', 0)),
            'maxLevel': int(b.get('Максимальный уровень', 1)),
            'formulas': {
                'size':          b.get('Формула занимаемого в тоннаже места', '0').strip(),
                'structure':     b.get('Формула структуры груза', '0').strip(),
                'minerals':      b.get('Формула стоимости минералов', '0').strip(),
                'organics':      b.get('Формула стоимости органики', '0').strip(),
                'radioactives':  b.get('Формула стоимости радиоактивных элементов', '0').strip(),
                'fuel':          b.get('Формула использованного количества топлива', '0').strip(),
                'ammo':          b.get('Формула использованного количества боеприпасов', '0').strip(),
            },
            'abilities': parse_abilities(b),
            'requirements': parse_requirements(b),
            **(({'weapon': weapon}) if weapon else {}),
        })

    return components


# ---------------------------------------------------------------------------
# Facilities parser
# ---------------------------------------------------------------------------

def parse_facilities() -> list[dict]:
    content = read_game_file('Facilities.txt')
    raw_blocks = parse_blocks(content, name_key='Название')

    facilities = []
    for b in raw_blocks:
        name = b.get('Название', '').strip()
        if not name:
            continue
        # Skip intel-class duplicate name fields that come up as solo entries
        if not b.get('Группа объекта') and not b.get('Описание'):
            continue

        facilities.append({
            'name': name,
            'description': b.get('Описание', '').strip(),
            'group': b.get('Группа объекта', '').strip(),
            'imageNum': int(b.get('Номер изображения', 0)),
            'maxLevel': int(b.get('Максимальный уровень', 1)),
            'formulas': {
                'size':         b.get('Формула занимаемого в тоннаже места', '0').strip(),
                'structure':    b.get('Формула структуры груза', '0').strip(),
                'minerals':     b.get('Формула стоимости минералов', '0').strip(),
                'organics':     b.get('Формула стоимости органики', '0').strip(),
                'radioactives': b.get('Формула стоимости радиоактивных элементов', '0').strip(),
            },
            'abilities': parse_abilities(b),
            'requirements': parse_requirements(b),
        })

    return facilities


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_json(data: list, filename: str):
    path = OUT / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'  wrote {len(data):>4} entries → {path.relative_to(ROOT)}')


if __name__ == '__main__':
    print(f'Parsing game data → lang={LANG}')

    print('TechAreas...')
    techs = parse_tech_areas()
    write_json(techs, f'tech_tree_{LANG}.json')

    print('Components...')
    comps = parse_components()
    write_json(comps, f'components_{LANG}.json')

    print('Facilities...')
    facs = parse_facilities()
    write_json(facs, f'facilities_{LANG}.json')

    print('Done.')
