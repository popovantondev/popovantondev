"""Render the localized application catalog from existing release metadata."""
from html import escape as e

COPY={
 'ru':dict(eyebrow='ПРИЛОЖЕНИЯ ДЛЯ MACOS И WINDOWS',title='Ваши задачи. Нужные инструменты.',intro='Учёба, медиа, резервные копии и повседневная работа. Выберите программу — загрузка и руководство рядом.',all='Все программы',search='Найти программу',placeholder='Название или задача…',requirements='Требования и ограничения',count='программ',empty='Ничего не найдено. Измените поиск или платформу.',github='Открыть GitHub',browse='Выбрать программу',footer='Проверяйте требования перед загрузкой. Preview — предварительная версия; «Исходники» означает отсутствие готового пакета.',platform='Платформа'),
 'de':dict(eyebrow='ANWENDUNGEN FÜR MACOS UND WINDOWS',title='Ihre Aufgaben. Die passenden Werkzeuge.',intro='Lernen, Medien, Backups und alltägliche Arbeit. Anwendung auswählen — Download und Anleitung sind direkt dabei.',all='Alle Anwendungen',search='Anwendung suchen',placeholder='Name oder Aufgabe…',requirements='Voraussetzungen und Grenzen',count='Anwendungen',empty='Keine Ergebnisse. Suche oder Plattform ändern.',github='GitHub öffnen',browse='Anwendung auswählen',footer='Voraussetzungen vor dem Download prüfen. Preview ist eine Vorabversion; „Quellcode“ bedeutet, dass kein fertiges Paket verfügbar ist.',platform='Plattform'),
 'en':dict(eyebrow='APPLICATIONS FOR MACOS AND WINDOWS',title='Your tasks. The right tools.',intro='Study, media, backups and everyday work. Choose an application — downloads and guides are right beside it.',all='All applications',search='Find an application',placeholder='Name or task…',requirements='Requirements and limitations',count='applications',empty='No matches. Change your search or platform.',github='Open GitHub',browse='Explore applications',footer='Check requirements before downloading. Preview is an early release; “Source” means there is no ready-to-run package.',platform='Platform')}

def render(d,l,labels,status,actions):
 c=COPY[l]; nav=''.join(f'<a href="{("index.html" if x=="en" else "index-"+x+".html")}" lang="{x}" hreflang="{x}"'+(' aria-current="page"' if x==l else '')+f'>{dict(ru="RU",de="DE",en="EN")[x]}</a>' for x in ('ru','de','en'))
 cards=[]
 for p in d['projects']:
  os='macos' if 'macOS' in p['platform'] else 'windows'
  icon=d['catalog_icons'][p['repo']]
  cards.append(f'''<article class="project" id="{e(p['repo'])}" data-platform="{os}">
<div class="project-heading"><img class="project-icon" src="{e(icon)}" width="64" height="64" alt="" decoding="async" loading="lazy"><span class="platform">{e(p['platform'])}</span></div>
<h2><a href="{e(p['source_url'])}">{e(p['name'])}</a></h2><span class="status {p['status']}">{e(status(p,l))}</span>
<p class="description">{e(p['description'][l])}</p>
<details class="requirements"><summary>{e(c['requirements'])}</summary><p>{e(p['requirements'][l])}</p></details>
<div class="actions">{''.join(f'<a href="{e(url)}">{e(label)}</a>' for label,url in actions(p,l))}</div></article>''')
 n=len(d['projects'])
 return f'''<!doctype html>
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(c['intro'])}"><meta name="theme-color" content="#f6f7fb"><title>popovantondev — {e(labels[l]['catalog'])}</title><link rel="stylesheet" href="assets/catalog.css"><script src="assets/catalog.js" defer></script></head>
<body><div class="shell"><header class="top"><a class="brand" href="https://github.com/popovantondev"><span class="brand-mark">P</span>popovantondev</a><nav aria-label="Language">{nav}</nav></header>
<main><section class="hero"><div class="hero-copy"><p class="eyebrow">{e(c['eyebrow'])}</p><h1>{e(c['title'])}</h1><p class="lead">{e(c['intro'])}</p><div class="hero-actions"><a class="primary" href="#catalog">{e(c['browse'])} <span aria-hidden="true">↘</span></a><a href="https://github.com/popovantondev">{e(c['github'])} <span aria-hidden="true">↗</span></a></div><div class="hero-meta"><span>{n} {e(c['count'])}</span><span>macOS / Windows</span><span>RU / DE / EN</span></div></div>
<div class="hero-art"><img src="assets/profile-laptops-compact.png" width="800" height="600" alt="{e(labels[l]['catalog'])} — macOS &amp; Windows"></div></section>
<section id="catalog" aria-labelledby="catalog-title"><div class="catalog-top"><div><p class="eyebrow">{e(c['platform'])} · macOS / Windows</p><h2 id="catalog-title">{e(c['all'])}</h2></div><span class="result-count" id="result-count" aria-live="polite">{n} / {n}</span></div>
<div class="catalog-controls" hidden><div class="filters" role="group" aria-label="{e(c['platform'])}"><button type="button" data-filter="all" aria-pressed="true">{e(c['all'])}</button><button type="button" data-filter="macos" aria-pressed="false">macOS</button><button type="button" data-filter="windows" aria-pressed="false">Windows</button></div><label class="search"><span class="sr-only">{e(c['search'])}</span><input id="project-search" type="search" placeholder="{e(c['placeholder'])}" autocomplete="off"></label></div>
<div class="projects">{''.join(cards)}</div><p class="empty" id="empty" hidden>{e(c['empty'])}</p></section></main>
<footer><a href="https://github.com/popovantondev">popovantondev <span aria-hidden="true">↗</span></a><p>{e(c['footer'])}</p><span>RU · DE · EN</span></footer></div></body></html>
'''
