// Verify the Transportation view (2026-08-31).
//
// The shipped data has road_m_per_acre and bike_m_per_acre length-density
// columns, not vehicle lane counts or lane-kilometres. This check protects the
// UI contract: a top-level Transportation tab compares road km/km² with
// dedicated bike-route km/km², carries the caveat, toggles the matching network
// overlay, and keeps the old Money controls out of the way.
//   node tools/profiling/verify-transportation.js <url>     (from REPO ROOT)
const { chromium } = require('playwright');
const [url] = process.argv.slice(2);

(async () => {
  const browser = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--ignore-gpu-blocklist', '--enable-webgl'],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', e => console.log('PAGE EXCEPTION:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('PAGE ERROR:', m.text()); });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(4000);

  const click = sel => page.$eval(sel, b => b.click());
  let fail = 0;
  const check = (name, cond, extra) => {
    console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  ' + extra : ''}`);
    if (!cond) fail++;
  };
  const chrome = () => page.evaluate(() => ({
    view: state.view,
    metric: state.transportMetric,
    title: document.getElementById('title-h').textContent,
    blurb: document.getElementById('title-p').textContent,
    legendLabel: document.getElementById('legend-label').textContent,
    legendMin: document.getElementById('legend-min').textContent,
    legendMax: document.getElementById('legend-max').textContent,
    aside: document.querySelector('#legend .aside span:last-child').textContent,
    cats: document.getElementById('legend-cats').style.display !== 'none'
      ? document.getElementById('legend-cats').textContent.trim() : '',
    panelShown: getComputedStyle(document.getElementById('layers')).display !== 'none',
    transportShown: getComputedStyle(document.getElementById('transport')).display !== 'none',
    moneyPodShown: getComputedStyle(document.getElementById('toggle')).display !== 'none',
    servicesShown: getComputedStyle(document.getElementById('services')).display !== 'none',
    prismRowShown: getComputedStyle(document.getElementById('prism-row')).display !== 'none',
    activeTransport: [...document.querySelectorAll('#transport button')]
      .filter(b => getComputedStyle(b).display !== 'none' && b.classList.contains('active'))
      .map(b => b.dataset.transport),
    visibleTransport: [...document.querySelectorAll('#transport button')]
      .filter(b => getComputedStyle(b).display !== 'none')
      .map(b => b.textContent.trim()),
    layers: typeof overlay !== 'undefined' ? overlay._deck.props.layers.map(l => l.id) : [],
  }));

  await click('#views button[data-view="transportation"]');
  await page.waitForTimeout(4000); // roads lazy-fetch + rebuild
  const roads = await chrome();
  check('enters the Transportation view', roads.view === 'transportation', roads.view);
  check('defaults to road length density', roads.metric === 'roads', roads.metric);
  check('shows the Transportation controls', roads.panelShown && roads.transportShown);
  check('hides Money/Services/Prism controls', !roads.moneyPodShown && !roads.servicesShown && !roads.prismRowShown);
  check('offers Road km and Bike-route km toggles', roads.visibleTransport.join('|') === 'Road km|Bike-route km', roads.visibleTransport.join('|'));
  check('only Road km is active on entry', roads.activeTransport.join('|') === 'roads', roads.activeTransport.join('|'));
  check('road title names road kilometres per km²', /Road Kilometres per km²/i.test(roads.title), roads.title);
  check('road copy explicitly says not lane-kilometres', /not vehicle lane-kilometres/i.test(roads.blurb), roads.blurb.slice(0, 120));
  check('road legend is in km per km²', /Road kilometres per km²/i.test(roads.legendLabel), roads.legendLabel);
  check('road overlay is present', roads.layers.includes('roads-ground'), roads.layers.join('|'));
  check('bike overlay is absent in road mode', !roads.layers.includes('bike-lines'), roads.layers.join('|'));

  const roadMath = await page.evaluate(() => {
    const mode = transportMode();
    const kept = state.data.features.filter(f => !f.properties.is_set_aside && f.properties[mode.col] != null);
    const vals = kept.map(f => f.properties[mode.col]).sort((a, b) => a - b);
    const pos = (vals.length - 1) * 0.975, lo = Math.floor(pos);
    const q = vals[lo] + (vals[Math.ceil(pos)] - vals[lo]) * (pos - lo);
    const scale = svcScale(mode.col);
    const mid = kept[Math.floor(kept.length / 2)];
    const plane = overlay._deck.props.layers.find(l => l.id === 'transport-plane');
    const expected = rampColorAt(Math.min(1, mid.properties[mode.col] / scale.clamp));
    const access = roadsData.features.find(f => f.properties.t !== 'arterial');
    const art = roadsData.features.find(f => f.properties.t === 'arterial');
    return {
      clampMatchesP975: Math.abs(scale.clamp - q) < 1e-6,
      planeFillOk: plane.props.getFillColor(mid).join() === expected.join(),
      roadAccessColoured: overlay._deck.props.layers.find(l => l.id === 'roads-ground')
        .props.getLineColor(access).join() !== ARTERIAL_COLOR.join(),
      arterialNeutral: overlay._deck.props.layers.find(l => l.id === 'roads-ground')
        .props.getLineColor(art).join() === ARTERIAL_COLOR.join(),
      tooltip: tooltipFor({ object: mid }).html,
    };
  });
  check('road scale clamp is the data p97.5', roadMath.clampMatchesP975);
  check('road plane uses linear ramp colour', roadMath.planeFillOk);
  check('road access lines are coloured, arterials neutral', roadMath.roadAccessColoured && roadMath.arterialNeutral);
  check('road tooltip uses km/km² and caveats lane-km', /road km \/ km²/.test(roadMath.tooltip) && /not lane-km/i.test(roadMath.tooltip), roadMath.tooltip);

  await click('#transport button[data-transport="bike"]');
  await page.waitForTimeout(3500); // bike route lazy-fetch + rebuild
  const bike = await chrome();
  check('switches to bike-route length density', bike.metric === 'bike', bike.metric);
  check('only Bike-route km is active', bike.activeTransport.join('|') === 'bike', bike.activeTransport.join('|'));
  check('bike title names dedicated bike-route kilometres', /Dedicated Bike-Route Kilometres per km²/i.test(bike.title), bike.title);
  check('bike copy explicitly says route length is not lane-counted', /route length, not a lane-counted measure/i.test(bike.blurb), bike.blurb.slice(0, 160));
  check('bike legend is in km per km² and sqrt-labelled', /bike-route kilometres per km² \(sqrt colour\)/i.test(bike.legendLabel), bike.legendLabel);
  check('bike overlay is present', bike.layers.includes('bike-lines'), bike.layers.join('|'));
  check('road overlay is absent in bike mode', !bike.layers.includes('roads-ground'), bike.layers.join('|'));
  check('bike legend names the network overlay', /Dedicated bike-route network/i.test(bike.cats), bike.cats);

  const bikeMath = await page.evaluate(() => {
    const mode = transportMode();
    const kept = state.data.features.filter(f => !f.properties.is_set_aside && f.properties[mode.col] != null);
    const vals = kept.map(f => f.properties[mode.col]).sort((a, b) => a - b);
    const pos = (vals.length - 1) * 0.975, lo = Math.floor(pos);
    const q = vals[lo] + (vals[Math.ceil(pos)] - vals[lo]) * (pos - lo);
    const scale = svcScale(mode.col);
    const mid = kept.find(f => f.properties[mode.col] > 0) || kept[Math.floor(kept.length / 2)];
    const plane = overlay._deck.props.layers.find(l => l.id === 'transport-plane');
    const expected = rampColorAt(Math.sqrt(Math.min(1, mid.properties[mode.col] / scale.clamp)));
    return {
      clampMatchesP975: Math.abs(scale.clamp - q) < 1e-6,
      planeFillOk: plane.props.getFillColor(mid).join() === expected.join(),
      tooltip: tooltipFor({ object: mid }).html,
    };
  });
  check('bike scale clamp is the data p97.5', bikeMath.clampMatchesP975);
  check('bike plane uses sqrt ramp colour', bikeMath.planeFillOk);
  check('bike tooltip uses km/km² and caveats lane-counting', /dedicated bike-route km \/ km²/.test(bikeMath.tooltip) && /not lane-counted/i.test(bikeMath.tooltip), bikeMath.tooltip);

  await click('#transport button[data-transport="roads"]');
  await page.waitForTimeout(1500);
  const roundTrip = await chrome();
  check('Road km toggle works after a bike round-trip', roundTrip.metric === 'roads' && roundTrip.layers.includes('roads-ground'), roundTrip.layers.join('|'));

  console.log(fail ? `\n${fail} CHECK(S) FAILED` : '\nALL CHECKS PASSED');
  await browser.close();
  process.exit(fail ? 1 : 0);
})();
