#!/usr/bin/env python3
"""Parse dropshipping.ua XML feed -> static JSON files for the shop."""

import json, os, re, sys, urllib.request
from xml.etree.ElementTree import parse, fromstring

OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
FEED_URL = os.environ.get('FEED_URL', '')
XML_PATH = 'C:/tmp/feed3533.xml'

GROUPS = [
    {'id': 'santekhnika', 'name': 'Сантехніка', 'icon': 'droplet',
     'cats': [1034, 1035, 1036, 1037, 1038, 1113, 1330]},
    {'id': 'nasosy', 'name': 'Насосне обладнання', 'icon': 'settings',
     'cats': [1039, 1040, 1041, 1042, 1043, 1044, 1045]},
    {'id': 'zahyst', 'name': 'Засоби захисту', 'icon': 'shield',
     'cats': [1050, 1051, 1052, 1053, 1054, 1055, 1056]},
    {'id': 'farby', 'name': 'Фарби та матеріали', 'icon': 'brush',
     'cats': [1058, 1059, 1060, 1061, 1062, 1111, 8699, 8700, 8701, 8702]},
    {'id': 'pidlogovi', 'name': 'Підлогові покриття', 'icon': 'grid',
     'cats': [5076, 5077, 5078, 5079, 5080, 5081, 5082, 5083, 5088, 5089, 5090, 6595, 6596, 6598]},
    {'id': 'elektryka', 'name': 'Електрика', 'icon': 'zap',
     'cats': [12116, 12117, 12118, 12119, 12120, 12121, 12122, 16775, 16776, 16777]},
    {'id': 'zvarka', 'name': 'Зварювання та інструменти', 'icon': 'tool',
     'cats': [1332, 1343, 1347, 1571, 1818, 9151, 21461]},
]


CAT_NAMES_UK = {
    1034: 'Проточні водонагрівачі',
    1035: 'Змішувачі для ванни',
    1036: 'Змішувачі для кухні',
    1037: 'Змішувачі для раковини',
    1038: 'Змішувачі для душу',
    1039: 'Насосні станції',
    1040: 'Мотопомпи',
    1041: 'Насоси поверхневі',
    1042: 'Насоси занурювальні',
    1043: 'Насоси циркуляційні',
    1044: 'Насоси дренажні',
    1045: 'Насоси фонтанні',
    1050: 'Захисні окуляри',
    1051: 'Захисні рукавиці',
    1052: 'Респіратори',
    1053: 'Захисні навушники',
    1054: 'Наколінники',
    1055: 'Малярні комбінезони',
    1056: 'Сигнальні жилети',
    1058: 'Емалі',
    1059: 'Лаки',
    1060: 'Ґрунтовки',
    1061: 'Герметики',
    1062: 'Монтажна піна',
    1111: 'Клеї',
    1113: 'Змішувачі для біде',
    1330: 'Комплектуючі для сантехніки',
    1332: 'Апарати безповітряного фарбування',
    1343: 'Магнітні фіксатори',
    1347: 'Маски зварника',
    1571: 'Будівельні пилососи',
    1818: 'Зварювальні контакти та затискачі',
    5076: 'Самоклейні 3D панелі',
    5077: 'ПВХ панелі',
    5078: 'РЕТ плитка',
    5079: 'Алюмінієва плитка',
    5080: 'Вінілова плитка',
    5081: 'ПВХ плитка',
    5082: 'Поліуретанова плитка',
    5083: 'Композитна плитка WPC',
    5088: 'Підлогові покриття-пазли',
    5089: 'Плитка-килимок',
    5090: 'Самоклейний плінтус і молдинг',
    6595: 'SPC-ламінат',
    6596: 'Вінілове та ПВХ покриття',
    6598: 'Вологопоглинаючі килимки',
    8699: 'Шпаклівки та штукатурки',
    8700: 'Будівельні фарби',
    8701: 'Захисні просочення та антисептики',
    8702: 'Розчинники та дезінфектори',
    9151: 'Тримачі електродів',
    12116: 'Вимикачі',
    12117: 'Електричні розетки',
    12118: 'LED освітлення (стрічки)',
    12119: 'Вбудовані світильники',
    12120: 'Блоки живлення для LED',
    12121: 'Вбудовані терморегулятори',
    12122: 'Вбудовані датчики руху',
    16775: 'Автоматичні вимикачі, ПЗВ',
    16776: 'Інвертори',
    16777: 'Розподільні блоки',
    21461: 'Зварювальні апарати',
}


def strip_html(text):
    if not text:
        return ''
    return re.sub(r'<[^>]+>', ' ', text).strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print('Parsing XML...')
    if FEED_URL:
        print(f'Downloading from {FEED_URL}')
        with urllib.request.urlopen(FEED_URL, timeout=60) as r:
            root = fromstring(r.read())
        shop = root.find('shop')
    else:
        tree = parse(XML_PATH)
        shop = tree.getroot().find('shop')

    cat_map = {}
    for c in shop.find('categories').findall('category'):
        cid = int(c.get('id'))
        cat_map[cid] = CAT_NAMES_UK.get(cid, c.text)

    offers_by_cat = {}
    all_vendors = set()

    for o in shop.find('offers').findall('offer'):
        cat_id = int(o.findtext('categoryId') or 0)
        vendor = o.findtext('vendor') or ''
        if vendor:
            all_vendors.add(vendor)
        product = {
            'id': o.get('id'),
            'available': o.get('available') == 'true',
            'name': o.findtext('name') or '',
            'price': float(o.findtext('price') or 0),
            'vendor': vendor,
            'vendorCode': o.findtext('vendorCode') or '',
            'categoryId': cat_id,
            'pictures': [p.text for p in o.findall('picture') if p.text],
            'description': strip_html(o.findtext('description') or ''),
            'params': [
                {'name': p.get('name'), 'value': p.text}
                for p in o.findall('param')
                if p.text and p.get('name') and len(p.get('name').strip()) > 2 and not p.get('name').strip().isdigit()
            ],
        }
        offers_by_cat.setdefault(cat_id, []).append(product)

    # Write per-category JSON files
    for cat_id, products in offers_by_cat.items():
        path = os.path.join(OUT_DIR, f'cat_{cat_id}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, separators=(',', ':'))
    print(f'Written {len(offers_by_cat)} category files')

    # Build groups with metadata
    groups_out = []
    for g in GROUPS:
        cats_out = []
        total = 0
        cover = None
        for cid in g['cats']:
            prods = offers_by_cat.get(cid, [])
            count = sum(1 for p in prods if p['available'])
            if count > 0:
                cats_out.append({'id': cid, 'name': cat_map.get(cid, ''), 'count': count})
                total += count
            if not cover:
                for p in prods:
                    if p['available'] and p['pictures']:
                        cover = p['pictures'][0]
                        break
        if cats_out:
            groups_out.append({
                'id': g['id'],
                'name': g['name'],
                'icon': g['icon'],
                'cats': cats_out,
                'total': total,
                'cover': cover,
            })

    # Featured: first available product with photo per category
    featured = []
    seen_cats = set()
    for cat_id, products in offers_by_cat.items():
        for p in products:
            if p['available'] and p['pictures'] and cat_id not in seen_cats:
                featured.append(p)
                seen_cats.add(cat_id)
                break
    featured = sorted(featured, key=lambda x: x['price'], reverse=True)[:24]

    total_prods = sum(len(v) for v in offers_by_cat.values())
    avail_prods = sum(sum(1 for p in v if p['available']) for v in offers_by_cat.values())

    catalog = {
        'groups': groups_out,
        'allCats': [{'id': k, 'name': v} for k, v in sorted(cat_map.items())],
        'vendors': sorted(list(all_vendors)),
        'stats': {
            'total': total_prods,
            'available': avail_prods,
            'categories': len(cat_map),
            'groups': len(groups_out),
        },
    }

    with open(os.path.join(OUT_DIR, 'catalog.json'), 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, separators=(',', ':'))

    with open(os.path.join(OUT_DIR, 'featured.json'), 'w', encoding='utf-8') as f:
        json.dump(featured, f, ensure_ascii=False, separators=(',', ':'))

    print(f'catalog.json: {len(groups_out)} groups, {total_prods} products ({avail_prods} available)')
    print(f'featured.json: {len(featured)} products')
    print('Done!')


if __name__ == '__main__':
    main()
