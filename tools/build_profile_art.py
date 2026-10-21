"""Compose self-contained SVG profile artwork from published interface images.

The laptop photograph is reused unchanged. A small SVG triangle mesh puts each
device in the same inward-facing perspective as its screen contents.
"""
from pathlib import Path
from html import escape
import base64
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
COPY = {
    'ru': ('Практичные программы', 'Приложения для macOS и Windows',
           'УЧЁБА · МЕДИА · КОПИИ · АВТОМАТИЗАЦИЯ', 'Попробовать PeakMP3 в браузере'),
    'de': ('Praktische Programme', 'Anwendungen für macOS und Windows',
           'LERNEN · MEDIEN · BACKUP · AUTOMATISIERUNG', 'PeakMP3 im Browser testen'),
    'en': ('Practical desktop tools', 'Applications for macOS & Windows',
           'STUDY · MEDIA · BACKUP · AUTOMATION', 'Try PeakMP3 in your browser'),
}


def image_data(name):
    return 'data:image/webp;base64,' + base64.b64encode(
        (ASSETS / 'banner-sources' / name).read_bytes()).decode('ascii')


def affine(source, target):
    (x, y), (x1, y1), (x2, y2) = source
    (u, v), (u1, v1), (u2, v2) = target
    dx, dy, ex, ey = x1-x, y1-y, x2-x, y2-y
    du, dv, eu, ev = u1-u, v1-v, u2-u, v2-v
    det = dx*ey-ex*dy
    a, c = (du*ey-eu*dy)/det, (dx*eu-ex*du)/det
    b, d = (dv*ey-ev*dy)/det, (dx*ev-ex*dv)/det
    return ' '.join(f'{n:.5f}' for n in (a, b, c, d, u-a*x-c*y, v-b*x-d*y))


def device_mesh(name, source_rect, corners):
    x, y, width, height = source_rect
    tl, tr, br, bl = corners

    def point(u, v):
        return tuple((1-u)*(1-v)*tl[k]+u*(1-v)*tr[k]+u*v*br[k]+(1-u)*v*bl[k]
                     for k in (0, 1))

    boundary=' '.join(f'{px},{py}' for px,py in corners)
    result = [f'<clipPath id="{name}-boundary"><polygon points="{boundary}"/></clipPath>',
              f'<g clip-path="url(#{name}-boundary)">']
    for row in range(4):
        for column in range(4):
            uv = [(column/4, row/4), ((column+1)/4, row/4),
                  ((column+1)/4, (row+1)/4), (column/4, (row+1)/4)]
            src = [(x+u*width, y+v*height) for u, v in uv]
            dst = [point(u, v) for u, v in uv]
            for half, indices in enumerate(((0, 1, 2), (0, 2, 3))):
                s, t = [src[i] for i in indices], [dst[i] for i in indices]
                identity = f'{name}-{row}-{column}-{half}'
                # Slight overlap avoids transparent hairlines between triangles.
                cx, cy = sum(p[0] for p in s)/3, sum(p[1] for p in s)/3
                polygon = ' '.join(f'{cx+(px-cx)*1.06:.4f},{cy+(py-cy)*1.06:.4f}'
                                   for px, py in s)
                result.append(f'<clipPath id="{identity}"><polygon points="{polygon}"/></clipPath>'
                              f'<g transform="matrix({affine(s,t)})"><use href="#{name}" '
                              f'clip-path="url(#{identity})"/></g>')
    return ''.join(result)+'</g>'


def banner(lang):
    title, subtitle, tags, _ = COPY[lang]
    laptops, peak, quick = (image_data(n) for n in
                            ('laptops.webp', f'peakmp3-{lang}.webp', f'quickanswer-{lang}.webp'))
    definitions = f'''<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#07172e"/><stop offset="1" stop-color="#245faa"/></linearGradient>
<clipPath id="round"><rect width="1400" height="360" rx="24"/></clipPath>
<image id="laptops" width="720" height="480" href="{laptops}"/>
<g id="mac"><use href="#laptops"/></g>
<g id="windows"><use href="#laptops"/><rect x="382" y="94" width="310" height="204" rx="3" fill="#101a2d"/>
<image x="388" y="98" width="128" height="196" preserveAspectRatio="xMidYMid meet" href="{peak}"/>
<image x="524" y="98" width="160" height="196" preserveAspectRatio="xMidYMid meet" href="{quick}"/></g>
</defs>'''
    mac = device_mesh('mac', (0, 70, 365, 355),
                      ((36, 90), (300, 70), (315, 330), (24, 323)))
    windows = device_mesh('windows', (365, 70, 355, 355),
                          ((1100, 70), (1364, 90), (1376, 323), (1085, 330)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="360" viewBox="0 0 1400 360" role="img" aria-label="popovantondev — {escape(title)}">
{definitions}<g clip-path="url(#round)"><rect width="1400" height="360" fill="url(#bg)"/>
<path d="M1100 0 870 360M1290 0 1060 360" stroke="#a7dcff" stroke-opacity=".08" stroke-width="64"/>
{mac}{windows}<g text-anchor="middle" font-family="Segoe UI,Arial,sans-serif">
<text x="700" y="73" fill="#88ccff" font-size="18" letter-spacing="3" font-weight="600">POPOVANTONDEV</text>
<text x="700" y="151" fill="white" font-size="42" font-weight="700">{escape(title)}</text>
<text x="700" y="200" fill="#dceaff" font-size="25">{escape(subtitle)}</text>
<path d="M667 232h66" stroke="#48d6d0" stroke-width="4"/>
<text x="700" y="284" fill="#9ed6ff" font-size="14" letter-spacing="1.1">{escape(tags)}</text>
</g></g></svg>'''


def main():
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    for lang, (_, _, _, label) in COPY.items():
        (ASSETS / f'profile-laptops-v3-{lang}.svg').write_text(banner(lang), encoding='utf-8')
        # Preserve the approved demo panel; remove only its bottom brown stripe.
        path = ASSETS / f'peakmp3-demo-{lang}.svg'
        root = ET.fromstring(path.read_text(encoding='utf-8'))
        for node in list(root):
            if node.tag.endswith('path') and node.get('d') == 'M25 502h1350':
                root.remove(node)
        for node in root.iter():
            if node.tag.endswith('image'):
                node.set('href', image_data(f'peakmp3-{lang}.webp'))
        path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')
        link = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="84" viewBox="0 0 1400 84" role="img" aria-label="{escape(label)}">
<rect x="1" y="20" width="38" height="38" rx="7" fill="#218bff"/>
<path d="M15 29 29 39 15 49Z" fill="white"/>
<text x="55" y="51" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="600" fill="#218bff">{escape(label)}</text></svg>'''
        (ASSETS / f'peakmp3-demo-link-{lang}.svg').write_text(link, encoding='utf-8')


if __name__ == '__main__':
    main()
