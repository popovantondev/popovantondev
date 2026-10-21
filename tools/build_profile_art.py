"""Compose self-contained SVG banners from hinged 3D laptop renders.

Run render_profile_devices.cjs first when interface images change.
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


def banner(lang):
    title, subtitle, tags, _ = COPY[lang]
    mac_data=image_data('mac-spatial.webp')
    windows_data=image_data(f'windows-spatial-{lang}.webp')
    definitions='''<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#07172e"/><stop offset="1" stop-color="#245faa"/></linearGradient><clipPath id="round"><rect width="1400" height="360" rx="24"/></clipPath></defs>'''
    mac=f'<image x="0" y="0" width="340" height="360" href="{mac_data}"/>'
    windows=f'<image x="1060" y="0" width="340" height="360" href="{windows_data}"/>'
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
        (ASSETS / f'profile-laptops-v5-{lang}.svg').write_text(banner(lang), encoding='utf-8')
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
