"""Render the localized application catalog from existing release metadata (shared kit, category tabs)."""
import sys
from html import escape as e
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from kit_programs import CATEGORIES

KIT_VERSION=(Path(__file__).resolve().parents[1]/'assets'/'kit'/'KIT_VERSION').read_text(encoding='utf-8').strip()
CATALOG_REV='r6'  # raise when assets/catalog.css or catalog.js change, so browsers drop the old copies
GITHUB='https://github.com/popovantondev'
ORDER=('lernen','medien','werkzeuge','daten')
ALL_LABEL={'ru':'Все','de':'Alle','en':'All'}

COPY={
 'ru':dict(eyebrow='ПРИЛОЖЕНИЯ ДЛЯ MACOS И WINDOWS',title='Ваши задачи. Нужные инструменты.',intro='Учёба, медиа, резервные копии и повседневная работа. Выберите программу — загрузка и руководство рядом.',all='Все программы',search='Найти программу',placeholder='Название или задача…',requirements='Требования и ограничения',count='программ',empty='Ничего не найдено. Измените поиск, категорию или платформу.',github='Открыть GitHub',browse='Выбрать программу',footer='Проверяйте требования перед загрузкой. Preview — предварительная версия; «Исходники» означает отсутствие готового пакета.',platform='Платформа',nav='Основная навигация',skip='К содержимому',search_label='Поиск по программам',search_text='Поиск',kbd='Ctrl K',theme='Сменить тему',categories='Категории',legal='Правовая информация',impressum='Impressum',datenschutz='Datenschutz'),
 'de':dict(eyebrow='ANWENDUNGEN FÜR MACOS UND WINDOWS',title='Ihre Aufgaben. Die passenden Werkzeuge.',intro='Lernen, Medien, Backups und alltägliche Arbeit. Anwendung auswählen — Download und Anleitung sind direkt dabei.',all='Alle Anwendungen',search='Anwendung suchen',placeholder='Name oder Aufgabe…',requirements='Voraussetzungen und Grenzen',count='Anwendungen',empty='Keine Ergebnisse. Suche, Kategorie oder Plattform ändern.',github='GitHub öffnen',browse='Anwendung auswählen',footer='Voraussetzungen vor dem Download prüfen. Preview ist eine Vorabversion; „Quellcode“ bedeutet, dass kein fertiges Paket verfügbar ist.',platform='Plattform',nav='Hauptnavigation',skip='Zum Inhalt',search_label='Programme durchsuchen',search_text='Suchen',kbd='Strg K',theme='Farbschema wechseln',categories='Kategorien',legal='Rechtliches',impressum='Impressum',datenschutz='Datenschutz'),
 'en':dict(eyebrow='APPLICATIONS FOR MACOS AND WINDOWS',title='Your tasks. The right tools.',intro='Study, media, backups and everyday work. Choose an application — downloads and guides are right beside it.',all='All applications',search='Find an application',placeholder='Name or task…',requirements='Requirements and limitations',count='applications',empty='No matches. Change your search, category or platform.',github='Open GitHub',browse='Explore applications',footer='Check requirements before downloading. Preview is an early release; “Source” means there is no ready-to-run package.',platform='Platform',nav='Main navigation',skip='Skip to content',search_label='Search programs',search_text='Search',kbd='Ctrl K',theme='Switch colour scheme',categories='Categories',legal='Legal',impressum='Impressum',datenschutz='Datenschutz')}

PERMISSION_NOTICE={
 'ru':'Только с разрешения всех участников — для каждой встречи.',
 'de':'Nur mit Zustimmung aller Beteiligten — vor jeder Besprechung.',
 'en':'Only with every participant’s permission — for each meeting.'}

SITE='https://popovantondev.github.io/popovantondev/'
MARQUEE={
 'ru':dict(title='Все программы одной лентой',sub='{apps} для macOS и Windows. Наведите курсор или нажмите Tab — лента остановится.',label='Лента программ'),
 'de':dict(title='Alle Anwendungen in einer Laufschrift',sub='{apps} für macOS und Windows. Mit der Maus darüber oder per Tab — die Laufschrift hält an.',label='Laufschrift der Anwendungen'),
 'en':dict(title='All applications in one ticker',sub='{apps} for macOS and Windows. Hover or tab onto it and the ticker pauses.',label='Application ticker')}
def apps_count(n,l):
 """'20 приложений' / '20 Anwendungen' / '20 applications': the number always comes from the catalog, never typed by hand."""
 if l=='ru':
  word='приложение' if n%10==1 and n%100!=11 else 'приложения' if 2<=n%10<=4 and not 12<=n%100<=14 else 'приложений'
 elif l=='de':word='Anwendung' if n==1 else 'Anwendungen'
 else:word='application' if n==1 else 'applications'
 return f'{n} {word}'

def marquee_sub(l,n):
 return MARQUEE[l]['sub'].format(apps=apps_count(n,l))

OG={
 'ru':dict(locale='ru_RU',alt='Студийный баннер popovantondev: программы для macOS и Windows на двух рабочих столах'),
 'de':dict(locale='de_DE',alt='Studio-Banner von popovantondev: Anwendungen für macOS und Windows auf zwei Schreibtischen'),
 'en':dict(locale='en_US',alt='popovantondev studio banner: applications for macOS and Windows on two desks')}

def marquee(d,l,actions):
 """Two opposite tickers; every track holds the programs twice (second copy hidden from assistive tech and the tab order)."""
 items=[]
 for p in d['projects']:
  site=next(url for kind,label,url in actions(p,l) if kind=='website')
  items.append((p,site,d['catalog_icons'][p['repo']]))
 half=(len(items)+1)//2
 def card(p,site,icon,copy):
  extra=' tabindex="-1"' if copy else ''
  return f'<a class="marquee-card" href="{e(site)}"{extra}><span class="marquee-shot"><img src="{e(icon)}" width="64" height="64" alt="" decoding="async" loading="lazy"></span><span class="marquee-meta"><b>{e(p["name"])}</b><small>{e(p["platform"])}</small></span></a>'
 def track(rows,cls):
  one=''.join(card(*r,False) for r in rows);two=''.join(card(*r,True) for r in rows)
  return f'<div class="marquee {cls}"><div class="marquee-track"><div class="marquee-set">{one}</div><div class="marquee-set" aria-hidden="true">{two}</div></div></div>'
 return track(items[:half],'marquee-forward')+track(items[half:],'marquee-reverse')

def head_meta(c,l,labels):
 o=OG[l];url=SITE+('index.html' if l=='de' else f'index-{l}.html');image=f'{SITE}assets/profile-studio-{l}.png'
 title=f'popovantondev — {labels[l]["catalog"]}'
 pairs=[('property','og:title',title),('property','og:description',c['intro']),('property','og:url',url),('property','og:type','website'),('property','og:locale',o['locale']),('property','og:image',image),('property','og:image:width','2048'),('property','og:image:height','768'),('property','og:image:alt',o['alt']),('name','twitter:card','summary_large_image')]
 return ''.join(f'<meta {k}="{n}" content="{e(v)}">' for k,n,v in pairs)

def render(d,l,labels,status,actions,notes=()):
 """notes: sentences about programs that ship inside another installer (shown as a note under that program)."""
 c=COPY[l]
 nav=''.join(f'<a href="{("index.html" if x=="de" else "index-"+x+".html")}" lang="{x}" hreflang="{x}"'+(' aria-current="page"' if x==l else '')+f'>{dict(ru="RU",de="DE",en="EN")[x]}</a>' for x in ('ru','de','en'))
 title=' '.join('<span>'+e(part)+'</span>' for part in {'ru':['Ваши задачи.','Нужные инструменты.'],'de':['Ihre Aufgaben.','Die passenden Werkzeuge.'],'en':['Your tasks.','The right tools.']}[l])
 shared={}
 for p in d['projects']:
  if p.get('shared_distribution'):shared[p['repo']]=next((n for n in notes if n.startswith(p['name'])),'')
 cards=[]
 for p in d['projects']:
  os='macos' if 'macOS' in p['platform'] else 'windows'
  icon=d['catalog_icons'][p['repo']]
  category=d['catalog_categories'][p['repo']]
  stack=d['catalog_stacks'][p['repo']]
  keywords=' '.join([CATEGORIES[category][l],stack])
  notice=f'<p class="collection-notice">{e(PERMISSION_NOTICE[l])}</p>' if p['repo']=='SaveLecture' else ''
  if shared.get(p['repo']):notice+=f'<p class="collection-notice">{e(shared[p["repo"]])}</p>'
  links=actions(p,l)
  site=next(url for kind,label,url in links if kind=='website')
  demo=next(((label,url) for kind,label,url in links if kind=='demo'),None)
  demo_link=f'<a class="try-demo" href="{e(demo[1])}">{e(demo[0])} <span aria-hidden="true">↗</span></a>' if demo else ''
  primary='download' if any(kind=='download' for kind,_,_ in links) else 'website'
  buttons=[]
  for kind,label,url in links:
   if kind=='demo':continue
   cls='ppk-btn'+(' ppk-btn-primary' if kind==primary else '')+(' ppk-btn-gh' if kind=='source' else '')+(' support-link' if kind=='bug' else '')
   buttons.append(f'<a class="{cls}" href="{e(url)}">{e(label)}</a>')
  cards.append(f'''<article class="project" id="{e(p['repo'])}" data-platform="{os}" data-category="{category}" data-keywords="{e(keywords)}">
<div class="project-heading"><span class="project-badge"><img class="project-icon" src="{e(icon)}" width="64" height="64" alt="" decoding="async" loading="lazy"></span><span class="platform">{e(p['platform'])}</span></div>
<div class="project-title-row"><h2><a href="{e(site)}">{e(p['name'])}</a></h2>{demo_link}</div><p class="project-meta"><span class="status {p['status']}">{e(status(p,l))}</span><span class="ppk-chip"><i class="ppk-dot"></i>{e(stack)}</span></p>
<p class="description">{e(p['description'][l])}</p>{notice}
<details class="requirements"><summary>{e(c['requirements'])}</summary><p>{e(p['requirements'][l])}</p></details>
<div class="actions">{''.join(buttons)}</div></article>''')
 n=len(d['projects'])
 tabs=''.join(f'<button type="button" role="tab" id="tab-{key}" aria-selected="{"true" if key=="all" else "false"}" aria-controls="projects" data-category="{key}">{e(label)}</button>' for key,label in [('all',ALL_LABEL[l])]+[(k,CATEGORIES[k][l]) for k in ORDER])
 return f'''<!doctype html>
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(c['intro'])}"><meta name="theme-color" content="#f3f6fb" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0c131b" media="(prefers-color-scheme: dark)">{head_meta(c,l,labels)}<title>popovantondev — {e(labels[l]['catalog'])}</title><link rel="icon" href="data:,"><script src="assets/kit/kit-theme.js"></script><link rel="stylesheet" href="assets/kit/kit.css?v={KIT_VERSION}"><link rel="stylesheet" href="assets/catalog.css?v=kit-{KIT_VERSION}-{CATALOG_REV}"><script src="assets/kit/programs.js?v={KIT_VERSION}" defer></script><script src="assets/kit/kit.js?v={KIT_VERSION}" defer></script><script src="assets/catalog.js?v=kit-{KIT_VERSION}-{CATALOG_REV}" defer></script></head>
<body class="ppk-page"><a class="ppk-skip" href="#catalog">{e(c['skip'])}</a>
<div class="ppk-nav-wrap" id="ppk-nav-wrap"><nav class="ppk-nav" aria-label="{e(c['nav'])}"><a class="ppk-brand" href="{("index.html" if l=="de" else "index-"+l+".html")}"><span>popovantondev</span></a><span class="ppk-spacer"></span><button class="ppk-search-btn" type="button" data-ppk-open-search aria-label="{e(c['search_label'])}"><span>{e(c['search_text'])}</span><kbd>{e(c['kbd'])}</kbd></button><div class="ppk-langs">{nav}</div><button class="ppk-icon-btn ppk-theme-btn" type="button" data-ppk-theme aria-label="{e(c['theme'])}"></button><a class="ppk-icon-btn ppk-gh-btn" href="{GITHUB}" aria-label="GitHub"></a></nav></div>
<main class="ppk-shell" id="main"><section class="hero hero-studio"><div class="studio-art" aria-hidden="true"><div class="scene"><img class="photograph" src="assets/studio/studio-desktops.webp" width="2048" height="768" alt="" aria-hidden="true"><div class="desktop mac-desktop" style="transform:matrix3d(0.362478164855,0.00268640514118,0,2.11527963873e-05,-0.00544406398359,0.354618133095,0,-2.39855755711e-05,0,0,1,0,91,127,0,1)" aria-hidden="true"><img class="app translator" src="assets/studio/translate-{l}.webp" width="1160" height="756" alt=""><div class="sender-window"><div class="titlebar"><span class="traffic"><i></i><i></i><i></i></span>Telegram Media Sender</div><img src="assets/studio/sender-{l}.webp" width="1040" height="702" alt=""></div></div><div class="desktop windows-desktop" style="transform:matrix3d(0.307737845066,-0.00272982638239,0,-1.96390387222e-05,-0.0464419135057,0.323316632667,0,-2.52904813132e-05,0,0,1,0,1407,139,0,1)" aria-hidden="true"><img class="app peak" src="assets/studio/peak-{l}.webp" width="700" height="1163" alt=""><img class="app quick" src="assets/studio/quick-{l}.webp" width="420" height="586" alt=""></div></div></div><div class="hero-copy"><p class="eyebrow">{e(c['eyebrow'])}</p><h1>{title}</h1><p class="lead">{e(c['intro'])}</p><div class="hero-actions"><a class="primary" href="#catalog">{e(c['browse'])} <span aria-hidden="true">↘</span></a><a href="{GITHUB}">{e(c['github'])} <span aria-hidden="true">↗</span></a></div><div class="hero-meta"><span>{n} {e(c['count'])}</span><span>macOS / Windows</span><span>RU / DE / EN</span></div></div></section>
<div class="demo-feature-row"><a class="peak-demo-feature" href="https://popovantondev.github.io/PeakMP3/{"index.html" if l=="de" else "index-"+l+".html"}#demo"><img src="assets/peakmp3-demo-{l}.svg" width="1400" height="520" alt="PeakMP3 — {dict(ru='Попробовать в браузере',de='Im Browser testen',en='Try in browser')[l]}" loading="lazy"></a><a class="peak-demo-feature piano-demo-feature" href="https://popovantondev.github.io/VirtualPianoArranger/play-{l}.html"><img src="assets/piano-demo-{l}.svg" width="1400" height="520" alt="Virtual Piano Arranger — {dict(ru='Играть в браузере',de='Im Browser spielen',en='Play in the browser')[l]}" loading="lazy"></a></div>
<section id="marquee" class="ppk-section marquee-section" aria-labelledby="marquee-title"><h2 id="marquee-title">{e(MARQUEE[l]['title'])}</h2><p class="ppk-sub">{e(marquee_sub(l,n))}</p>{marquee(d,l,actions)}</section>
<section id="catalog" class="ppk-section" aria-labelledby="catalog-title"><div class="catalog-top"><div><p class="eyebrow">{e(c['platform'])} · macOS / Windows</p><h2 id="catalog-title">{e(c['all'])}</h2></div><span class="result-count" id="result-count" aria-live="polite">{n} / {n}</span></div>
<div class="catalog-controls" hidden><div class="ppk-tabs" role="tablist" aria-label="{e(c['categories'])}">{tabs}</div><div class="catalog-filters"><div class="filters" role="group" aria-label="{e(c['platform'])}"><button type="button" data-filter="all" aria-pressed="true">{e(ALL_LABEL[l])}</button><button type="button" data-filter="macos" aria-pressed="false">macOS</button><button type="button" data-filter="windows" aria-pressed="false">Windows</button></div><label class="search"><span class="ppk-sr-only">{e(c['search'])}</span><input id="project-search" type="search" placeholder="{e(c['placeholder'])}" autocomplete="off"></label></div></div>
<div class="projects" id="projects" role="tabpanel" aria-labelledby="tab-all">{''.join(cards)}</div><p class="empty" id="empty" hidden>{e(c['empty'])}</p><p class="ppk-sub catalog-note">{e(c['footer'])}</p></section></main>
<footer class="ppk-footer"><span>© 2026 Anton Popov · popovantondev</span><nav aria-label="{e(c['legal'])}"><a href="impressum.html">{e(c['impressum'])}</a><a href="datenschutz.html">{e(c['datenschutz'])}</a><a href="{GITHUB}">GitHub</a></nav></footer></body></html>
'''
