/* Quiet motion for the about pages: staggered reveal of card groups and a highlighted jump link while scrolling.
   Only IntersectionObserver and class/attribute changes (no scroll handlers); static when the visitor prefers reduced motion. */
(function () {
  'use strict';
  var doc = document;
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 0. The hero loops (drifting rays, glint) pause while the hero is off screen, so scrolling the long page stays light.
  var hero = doc.querySelector('.ab-hero');
  if (hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      doc.documentElement.classList.toggle('ab-hero-off', !entries[0].isIntersecting);
    }, { threshold: 0 }).observe(hero);
  }

  // 1. Jump links: mark the section that sits in the middle band of the viewport.
  var links = Array.prototype.slice.call(doc.querySelectorAll('.ab-jump a[href^="#"]'));
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var sections = Object.keys(byId).map(function (id) { return doc.getElementById(id); }).filter(Boolean);
  function mark(id) {
    links.forEach(function (a) {
      if (a === byId[id]) { a.setAttribute('aria-current', 'location'); } else { a.removeAttribute('aria-current'); }
    });
  }
  if ('IntersectionObserver' in window && sections.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (entry.isIntersecting) { mark(entry.target.id); } });
    }, { rootMargin: '-35% 0px -60% 0px', threshold: 0 });
    sections.forEach(function (s) { spy.observe(s); });
    // The last section is short: once the footer shows up the visitor has reached the end of the page.
    var footer = doc.querySelector('.ppk-footer');
    if (footer) {
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { mark(sections[sections.length - 1].id); }
      }, { threshold: 0 }).observe(footer);
    }
  }

  // 2. Cards of one group come in one after another (delay is dropped after the first appearance so hover stays instant).
  if (reduced || !('IntersectionObserver' in window)) { return; }
  var groups = doc.querySelectorAll('.cases');
  Array.prototype.forEach.call(groups, function (group) {
    Array.prototype.forEach.call(group.children, function (item, i) {
      item.style.setProperty('--ab-i', String(i % 2));
      item.addEventListener('transitionend', function done(ev) {
        if (ev.propertyName === 'opacity') { item.style.removeProperty('--ab-i'); item.removeEventListener('transitionend', done); }
      });
    });
  });
})();
