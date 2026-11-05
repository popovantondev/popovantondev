"""Render the localized application catalog from existing release metadata (shared kit, category tabs)."""
import sys
from html import escape as e
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from kit_programs import CATEGORIES

KIT_VERSION=(Path(__file__).resolve().parents[1]/'assets'/'kit'/'KIT_VERSION').read_text(encoding='utf-8').strip()
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
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(c['intro'])}"><meta name="theme-color" content="#f3f6fb" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0c131b" media="(prefers-color-scheme: dark)"><title>popovantondev — {e(labels[l]['catalog'])}</title><script src="assets/kit/kit-theme.js"></script><link rel="stylesheet" href="assets/kit/kit.css?v={KIT_VERSION}"><link rel="stylesheet" href="assets/catalog.css?v=kit-{KIT_VERSION}"><script src="assets/kit/programs.js?v={KIT_VERSION}" defer></script><script src="assets/kit/kit.js?v={KIT_VERSION}" defer></script><script src="assets/catalog.js?v=kit-{KIT_VERSION}" defer></script></head>
<body class="ppk-page"><a class="ppk-skip" href="#catalog">{e(c['skip'])}</a>
<div class="ppk-nav-wrap" id="ppk-nav-wrap"><nav class="ppk-nav" aria-label="{e(c['nav'])}"><a class="ppk-brand" href="{("index.html" if l=="de" else "index-"+l+".html")}"><span>popovantondev</span></a><span class="ppk-spacer"></span><button class="ppk-search-btn" type="button" data-ppk-open-search aria-label="{e(c['search_label'])}"><span>{e(c['search_text'])}</span><kbd>{e(c['kbd'])}</kbd></button><div class="ppk-langs">{nav}</div><button class="ppk-icon-btn ppk-theme-btn" type="button" data-ppk-theme aria-label="{e(c['theme'])}"></button><a class="ppk-icon-btn ppk-gh-btn" href="{GITHUB}" aria-label="GitHub"></a></nav></div>
<main class="ppk-shell" id="main"><section class="hero hero-studio"><div class="studio-art" aria-hidden="true"><div class="scene"><img class="photograph" src="assets/studio/studio-desktops.webp" width="2048" height="768" alt="" aria-hidden="true"><div class="desktop mac-desktop" style="transform:matrix3d(0.362478164855,0.00268640514118,0,2.11527963873e-05,-0.00544406398359,0.354618133095,0,-2.39855755711e-05,0,0,1,0,91,127,0,1)" aria-hidden="true"><img class="app translator" src="assets/studio/translate-{l}.webp" alt=""><div class="sender-window"><div class="titlebar"><span class="traffic"><i></i><i></i><i></i></span>Telegram Media Sender</div><img src="assets/studio/sender-{l}.webp" alt=""></div></div><div class="desktop windows-desktop" style="transform:matrix3d(0.307737845066,-0.00272982638239,0,-1.96390387222e-05,-0.0464419135057,0.323316632667,0,-2.52904813132e-05,0,0,1,0,1407,139,0,1)" aria-hidden="true"><img class="app peak" src="assets/studio/peak-{l}.webp" alt=""><img class="app quick" src="assets/studio/quick-{l}.webp" alt=""></div></div></div><div class="hero-copy"><p class="eyebrow">{e(c['eyebrow'])}</p><h1>{title}</h1><p class="lead">{e(c['intro'])}</p><div class="hero-actions"><a class="primary" href="#catalog">{e(c['browse'])} <span aria-hidden="true">↘</span></a><a href="{GITHUB}">{e(c['github'])} <span aria-hidden="true">↗</span></a></div><div class="hero-meta"><span>{n} {e(c['count'])}</span><span>macOS / Windows</span><span>RU / DE / EN</span></div></div></section>
<a class="peak-demo-feature" href="https://popovantondev.github.io/PeakMP3/{"index.html" if l=="de" else "index-"+l+".html"}#demo"><img src="assets/peakmp3-demo-{l}.svg" width="1400" height="520" alt="PeakMP3 — {dict(ru='Попробовать в браузере',de='Im Browser testen',en='Try in browser')[l]}" loading="lazy"></a>
<section id="catalog" class="ppk-section" aria-labelledby="catalog-title"><div class="catalog-top"><div><p class="eyebrow">{e(c['platform'])} · macOS / Windows</p><h2 id="catalog-title">{e(c['all'])}</h2></div><span class="result-count" id="result-count" aria-live="polite">{n} / {n}</span></div>
<div class="catalog-controls" hidden><div class="ppk-tabs" role="tablist" aria-label="{e(c['categories'])}">{tabs}</div><div class="catalog-filters"><div class="filters" role="group" aria-label="{e(c['platform'])}"><button type="button" data-filter="all" aria-pressed="true">{e(ALL_LABEL[l])}</button><button type="button" data-filter="macos" aria-pressed="false">macOS</button><button type="button" data-filter="windows" aria-pressed="false">Windows</button></div><label class="search"><span class="ppk-sr-only">{e(c['search'])}</span><input id="project-search" type="search" placeholder="{e(c['placeholder'])}" autocomplete="off"></label></div></div>
<div class="projects" id="projects" role="tabpanel" aria-labelledby="tab-all">{''.join(cards)}</div><p class="empty" id="empty" hidden>{e(c['empty'])}</p><p class="ppk-sub catalog-note">{e(c['footer'])}</p></section></main>
<footer class="ppk-footer"><span>© 2026 Anton Popov · popovantondev</span><nav aria-label="{e(c['legal'])}"><a href="impressum.html">{e(c['impressum'])}</a><a href="datenschutz.html">{e(c['datenschutz'])}</a><a href="{GITHUB}">GitHub</a></nav></footer></body></html>
'''
