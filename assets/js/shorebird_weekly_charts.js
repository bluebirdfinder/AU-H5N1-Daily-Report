/* 遷徙性濱鳥「每週觀測紀錄數」：資料來自 assets/js/shorebird_weekly.js（h5n1.py fetch_shorebird_weekly()）。
   計的是「被登錄的觀測紀錄數」，不是入境隻數；以去年／前年同週與「佔全鳥類紀錄比例」對照，並標示登錄延遲。
   資料缺失或 available:false 時整張卡片保持隱藏，不顯示假的 0。 */
(function () {
    function isEn() { return document.documentElement.lang === 'en' || /_en\.html/.test(location.pathname); }
    function T(en) {
        return en ? {
            cur: 'Records this year (faded = likely incomplete)', wk: 'Week of ', rec: 'records',
            sumLabel: 'Last 4 complete weeks', vsLast: 'same weeks last year', share: 'Share of all iNaturalist bird records',
            lateTitle: 'Measured late registration', noLate: 'Not measurable yet: needs a snapshot at least 6 days old (accumulates automatically).',
            flat: 'no baseline', src: { gbif: 'GBIF', ala: 'ALA' }
        } : {
            cur: '今年紀錄數（淡色＝可能尚未登錄完整）', wk: '週起 ', rec: '筆',
            sumLabel: '最近 4 個完整週', vsLast: '去年同週', share: '佔全鳥類 iNaturalist 紀錄比例',
            lateTitle: '實測登錄延遲', noLate: '尚無法實測：需要至少 6 天前的快照（排程會自動累積）。',
            flat: '無對照', src: { gbif: 'GBIF', ala: 'ALA' }
        };
    }
    function lab(s) { const p = s.split('-'); return parseInt(p[1], 10) + '/' + parseInt(p[2], 10); }
    function sum(a) { return a.reduce((x, v) => x + (v || 0), 0); }
    function pct(n, d) { return d > 0 ? (100 * n / d) : null; }
    function fmtP(v) { return v === null ? '—' : v.toFixed(v < 10 ? 2 : 1) + '%'; }

    function lateRegistration(D, name, t) {
        // 找最舊且距今 ≥ 6 天的快照，比較「當時已結束的週」之後又被補登多少
        const snaps = D.snapshots || {}, latestDate = (D.fetched_at_utc || '').slice(0, 10);
        if (!latestDate) return t.noLate;
        const limit = new Date(latestDate + 'T00:00:00Z').getTime() - 6 * 86400000;
        const olds = Object.keys(snaps).filter(k => new Date(k + 'T00:00:00Z').getTime() <= limit).sort();
        if (!olds.length || !snaps[olds[0]].counts || !snaps[olds[0]].counts[name]) return t.noLate;
        const o = snaps[olds[0]], cur = D.sources[name].shorebirds[D.week_starts[0].slice(0, 4)];
        let before = 0, added = 0;
        o.week_starts.forEach((ws, i) => {
            const end = new Date(ws + 'T00:00:00Z').getTime() + 6 * 86400000;
            if (end >= new Date(olds[0] + 'T00:00:00Z').getTime()) return; // 當時尚未結束的週不算
            const j = D.week_starts.indexOf(ws), a = o.counts[name][i], b = j >= 0 ? cur[j] : null;
            if (a == null || b == null) return;
            before += a; added += Math.max(0, b - a);
        });
        return olds[0] + ' → ' + latestDate + ': +' + added + ' ' + t.rec + (before ? ' (+' + (100 * added / before).toFixed(1) + '%)' : '');
    }

    function build(name, D, en) {
        const src = D.sources[name], t = T(en);
        const ctx = document.getElementById('shorebird-' + name + '-chart');
        if (!src || !ctx || typeof Chart === 'undefined') return false;
        const years = Object.keys(src.shorebirds).sort().reverse();  // 今年在前
        const thisY = years[0], inc = D.incomplete_last_n_weeks || 3, n = D.week_starts.length;
        const cur = src.shorebirds[thisY];
        const bg = cur.map((v, i) => i >= n - inc ? 'rgba(56,189,248,0.30)' : 'rgba(56,189,248,0.85)');
        const colors = ['#f59e0b', '#a78bfa'];
        const ds = [{ type: 'bar', label: thisY + ' ' + t.cur, data: cur, backgroundColor: bg, borderColor: '#38bdf8', borderWidth: 1, borderRadius: 3 }];
        years.slice(1).forEach((y, k) => ds.push({ type: 'line', label: y, data: src.shorebirds[y], borderColor: colors[k % 2], backgroundColor: colors[k % 2], borderWidth: 2, borderDash: k ? [2, 3] : [5, 3], pointRadius: 2, tension: 0.2, spanGaps: true }));
        if (ctx._sbChart) ctx._sbChart.destroy();
        ctx._sbChart = new Chart(ctx, {
            data: { labels: D.week_starts.map(lab), datasets: ds },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(51,65,85,0.3)' } }, y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(51,65,85,0.3)' } } },
                plugins: { legend: { labels: { color: '#94a3b8', font: { size: 10 } } }, tooltip: { callbacks: { title: it => t.wk + D.week_starts[it[0].dataIndex] } } }
            }
        });
        // 摘要：最近 4 個完整週 vs 去年同週，以及佔全鳥類比例（扣掉觀察力道）
        const last = n - inc, from = Math.max(0, last - 4), rng = a => a.slice(from, last);
        const y1 = years[1], thisSum = sum(rng(cur)), lastSum = y1 ? sum(rng(src.shorebirds[y1])) : 0;
        const shT = pct(thisSum, sum(rng(src.all_birds[thisY]))), shL = y1 ? pct(lastSum, sum(rng(src.all_birds[y1]))) : null;
        const ratio = lastSum > 0 ? Math.round(100 * thisSum / lastSum) + '%' : t.flat;
        const el = document.getElementById('shorebird-' + name + '-summary');
        if (el) el.textContent = t.src[name] + ' · ' + t.sumLabel + ' (' + D.week_starts[from] + '~): ' + thisSum + ' ' + t.rec +
            ' | ' + t.vsLast + ' ' + lastSum + ' (' + ratio + ') | ' + t.share + ' ' + fmtP(shT) + ' vs ' + fmtP(shL) +
            ' | ' + t.lateTitle + ': ' + lateRegistration(D, name, t);
        const wrap = document.getElementById('shorebird-' + name + '-wrap'); if (wrap) wrap.classList.remove('hidden');
        return true;
    }
    function render() {
        const D = window.shorebirdWeeklyEmbedded, en = isEn();
        if (!D || !D.available || !D.week_starts || !D.week_starts.length || !D.sources) return;
        let any = false;
        Object.keys(D.sources).forEach(function (nm) { try { any = build(nm, D, en) || any; } catch (e) { console.warn('shorebird ' + nm + ' skipped', e); } });
        if (!any) return;
        const card = document.getElementById('shorebird-weekly-card'); if (card) card.classList.remove('hidden');
        const f = document.getElementById('shorebird-fetched'); if (f) f.textContent = (D.fetched_at_utc || '').slice(0, 10);
    }
    window.addEventListener('load', function () { try { render(); } catch (e) { console.warn('shorebird weekly skipped', e); } });
})();
