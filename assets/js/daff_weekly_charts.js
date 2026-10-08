/* 以 DAFF 官方逐筆事件檔（window.daffWeeklyEmbedded）繪製週趨勢圖：全澳週曲線與 NSW 週趨勢。
   以「採樣日所在週（週一起算）」彙整；採樣日為 #N/A 的紀錄不歸週；最近兩週標為「登記未完整」。 */
(function () {
    function T(lang) {
        return lang === 'en' ? {
            weekly: 'Weekly positive events (by sampling week; faded = incomplete)', cum: 'Cumulative (dated events only)',
            incomplete: 'Latest 2 weeks (registration incomplete)', wk: 'Week of ',
            yl: '▲ Weekly events', yr: '▲ Cumulative'
        } : {
            weekly: '週確診事件（依採樣週；淡色＝登記未完整）', cum: '累計（僅含有採樣日者）',
            incomplete: '最近兩週（登記未完整）', wk: '週起 ',
            yl: '▲ 週增事件', yr: '▲ 累計事件'
        };
    }
    function label(start) { const p = start.split('-'); return parseInt(p[1], 10) + '/' + parseInt(p[2], 10); }
    function build(canvasId, lang, pick, color) {
        const D = window.daffWeeklyEmbedded;
        const ctx = document.getElementById(canvasId);
        if (!D || !ctx || !D.weeks || !D.weeks.length || typeof Chart === 'undefined') return false;
        const t = T(lang);
        const vals = D.weeks.map(pick);
        let run = 0; const cum = vals.map(v => (run += v));
        const inc = D.incomplete_from;
        const bg = D.weeks.map(w => (inc && w.start >= inc) ? color + '55' : color);
        if (ctx._daffChart) ctx._daffChart.destroy();
        ctx._daffChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: D.weeks.map(w => label(w.start)),
                datasets: [
                    { type: 'bar', label: t.weekly, data: vals, backgroundColor: bg, borderColor: color, borderWidth: 1, borderRadius: 4, yAxisID: 'y' },
                    { type: 'line', label: t.cum, data: cum, borderColor: '#10b981', backgroundColor: '#10b981', borderWidth: 2.5, pointRadius: 3, tension: 0.2, yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(51,65,85,0.3)' } },
                    y: { position: 'left', beginAtZero: true, title: { display: true, text: t.yl, color: color, font: { size: 10 } }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(51,65,85,0.3)' } },
                    y1: { position: 'right', beginAtZero: true, title: { display: true, text: t.yr, color: '#10b981', font: { size: 10 } }, ticks: { color: '#10b981' }, grid: { drawOnChartArea: false } }
                },
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
                    tooltip: { callbacks: { title: items => t.wk + D.weeks[items[0].dataIndex].start } }
                }
            }
        });
        return true;
    }
    function note(id, lang, extra) {
        const D = window.daffWeeklyEmbedded, el = document.getElementById(id);
        if (!D || !el) return;
        const incl = D.weeks.filter(w => D.incomplete_from && w.start >= D.incomplete_from).map(w => w.start);
        el.textContent = lang === 'en'
            ? `Source: DAFF official per-event file (${D.fetched_at_utc ? D.fetched_at_utc.slice(0, 10) : ''}). ${D.dated_events} of ${D.total_events} events have a sampling date; ${D.undated_events} have none and are not placed in any week. Faded bars (weeks of ${incl.join(', ')}) are incomplete because of registration lag and are usually revised upward. ${extra || ''}`
            : `資料來源：DAFF 官方逐筆事件檔（${D.fetched_at_utc ? D.fetched_at_utc.slice(0, 10) : ''}）。全澳 ${D.total_events} 起中有採樣日者 ${D.dated_events} 起，另 ${D.undated_events} 起官方未填採樣日，未歸入任何一週。淡色柱（${incl.join('、')} 起的兩週）因各州登記延遲尚未完整，事後通常會被補增，不代表疫情趨緩。${extra || ''}`;
    }
    window.DaffWeekly = {
        renderNational: function (canvasId, lang) {
            const ok = build(canvasId, lang, w => w.total, '#ef4444');
            if (ok) note('daff-weekly-note', lang);
            return ok;
        },
        renderNsw: function (canvasId, lang) {
            const ok = build(canvasId, lang, w => (w.by_state && w.by_state.NSW) || 0, '#f59e0b');
            if (ok) {
                const D = window.daffWeeklyEmbedded;
                const n = D.weeks.reduce((a, w) => a + ((w.by_state && w.by_state.NSW) || 0), 0);
                const card = document.getElementById('nsw-trend-card'); if (card) card.classList.remove('hidden');
                const tot = document.getElementById('nsw-trend-total'); if (tot) tot.textContent = n;
                note('nsw-trend-note', lang);
            }
            return ok;
        }
    };

    // 「資料截至」標示：政策卡片是人工維護的文字，超過 14 天未更新就標示可能過期，避免悄悄過期
    function markAsOf() {
        const en = document.documentElement.lang === 'en' || /_en\.html/.test(location.pathname);
        document.querySelectorAll('[data-asof]').forEach(function (el) {
            const d = new Date(el.getAttribute('data-asof') + 'T00:00:00Z');
            if (isNaN(d.getTime())) return;
            const days = Math.floor((Date.now() - d.getTime()) / 86400000);
            const stale = days > 14;
            const b = document.createElement('div');
            b.className = 'text-[10px] font-mono mt-1 ' + (stale ? 'text-amber-300' : 'text-slate-500');
            b.textContent = en
                ? (stale ? '⚠️ Text last updated ' + el.getAttribute('data-asof') + ' (' + days + ' days ago, may be out of date; inferred from version history)' : 'Text last updated ' + el.getAttribute('data-asof'))
                : (stale ? '⚠️ 資料截至 ' + el.getAttribute('data-asof') + '（已 ' + days + ' 天未更新，可能已過期；依版本紀錄推定）' : '資料截至 ' + el.getAttribute('data-asof'));
            el.appendChild(b);
        });
    }
    window.addEventListener('load', function () {
        try { markAsOf(); } catch (e) { console.warn('asof skipped', e); }
        try { window.DaffWeekly.renderNsw('nswTrendChart', document.documentElement.lang === 'en' || /_en\.html/.test(location.pathname) ? 'en' : 'zh'); } catch (e) { console.warn('nsw weekly skipped', e); }
    });
})();
