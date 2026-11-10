/* CrashTop Help Center — small progressive enhancements. The site works without this file. */
(function () {
  'use strict';

  /* Guide filter on the home page: search box + topic tabs. Reads ?q= from the address. */
  var scope = document.querySelector('[data-filter]');
  if (scope) {
    var input = document.querySelector('[data-filter-input]');
    var tabs = Array.prototype.slice.call(scope.querySelectorAll('[data-filter-tab]'));
    var rows = Array.prototype.slice.call(scope.querySelectorAll('.row'));
    var empty = scope.querySelector('[data-filter-empty]');
    var cat = '';

    var apply = function () {
      var q = (input ? input.value : '').trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {
        var ok = (!cat || row.getAttribute('data-cat') === cat) &&
                 (!q || row.getAttribute('data-text').indexOf(q) !== -1);
        row.hidden = !ok;
        if (ok) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    };
    var pick = function (value) {
      cat = value;
      tabs.forEach(function (t) {
        var on = t.getAttribute('data-filter-tab') === value;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      apply();
    };

    tabs.forEach(function (t) {
      t.addEventListener('click', function () { pick(t.getAttribute('data-filter-tab')); });
    });
    if (input) {
      input.addEventListener('input', apply);
      var q = new URLSearchParams(location.search).get('q');
      if (q) {
        input.value = q;
        apply();
        var target = document.getElementById('guides');
        if (target) target.scrollIntoView();
      }
    }
    var reset = scope.querySelector('[data-filter-reset]');
    if (reset) reset.addEventListener('click', function () { if (input) input.value = ''; pick(''); });
  }

  /* Highlight the current section in the "On this page" list. */
  var toc = document.querySelector('[data-toc]');
  if (toc && 'IntersectionObserver' in window) {
    var links = {};
    Array.prototype.forEach.call(toc.querySelectorAll('a[href^="#"]'), function (a) {
      links[decodeURIComponent(a.getAttribute('href').slice(1))] = a;
    });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        Object.keys(links).forEach(function (id) { links[id].classList.remove('is-active'); });
        links[entry.target.id].classList.add('is-active');
      });
    }, { rootMargin: '0px 0px -70% 0px' });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el);
    });
  }

  /* "Did this answer your question?" */
  var fb = document.querySelector('[data-feedback]');
  if (fb) {
    var show = function (sel) { var el = fb.querySelector(sel); if (el) el.hidden = false; };
    var done = function (yes) {
      fb.querySelector('[data-feedback-q]').hidden = true;
      fb.querySelector('[data-feedback-btns]').hidden = true;
      show(yes ? '[data-feedback-yes-msg]' : '[data-feedback-no-msg]');
      if (!yes) show('[data-feedback-contact]');
    };
    fb.querySelector('[data-feedback-yes]').addEventListener('click', function () { done(true); });
    fb.querySelector('[data-feedback-no]').addEventListener('click', function () { done(false); });
  }
})();
