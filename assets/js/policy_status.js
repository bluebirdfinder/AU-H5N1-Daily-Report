/* 各州家禽圈養令現況：首頁政策卡（report_template*.html）與風險評估頁（risk_assessment*.html）共用。
 * 更新政策時只改下面的資料，並同步 asof（官方原文最後取得日）；不要再改各頁面的寫死文字。
 * 這是人工維護的資料檔，h5n1.py 不會覆寫它。 */
window.policyStatusEmbedded = {
  "updated": "2026-11-25",
  "note": "各州家禽圈養令現況。首頁政策卡與風險評估頁共用此檔，更新時只改這裡；asof＝官方原文最後取得日（超過 14 天頁面會顯示 ⚠️）。",
  "items": [
    {
      "state": "VIC",
      "tone": "amber",
      "asof": "2026-10-08",
      "zh": {
        "title": "維州 (VIC) · 家禽圍養令狀態待官方確認",
        "short": "狀態待官方確認：最後確認期限 2026-10-16，專屬頁面已無法讀取，請勿視為現行規定。",
        "body": "先前公告的「管制令 (Control Order)」圍養要求（南部各地方政府區含大墨爾本、50 隻以上家禽）<strong class=\"text-amber-300\">最後確認的有效期限為 2026 年 10 月 16 日</strong>。2026-11-18 自動抓取時，該管制令專屬頁面已回應「Page not found」，維州主頁的管制令清單也只剩疫苗與野生動物屍體處理兩項。<strong class=\"text-amber-300\">圈養令目前是否仍有效、已解除或已併入他頁，尚無官方原文佐證，請勿視為現行規定。</strong>",
        "note": "同頁官方聲明（2026-10-08 取得）：澳洲目前尚無家禽或牲畜的 H5 檢出。（來源：Agriculture Victoria；待官方確認後更新本卡）"
      },
      "en": {
        "title": "VIC · Poultry Confinement Order: Status Pending Official Confirmation",
        "short": "Status pending official confirmation: last confirmed valid until 16 Oct 2026; the official page is no longer readable. Do not treat it as a current rule.",
        "body": "The previously announced Control Order (confinement of flocks of 50+ poultry in southern local government areas incl. metropolitan Melbourne) was <strong class=\"text-amber-300\">last confirmed valid until 16 October 2026</strong>. On 2026-11-18 the order's dedicated page returned &quot;Page not found&quot;, and the control orders listed on the Victorian main page are now only poultry vaccination and dead wildlife handling. <strong class=\"text-amber-300\">Whether the confinement order is still in force, lifted, or moved elsewhere is not confirmed by any official source; do not treat it as a current rule.</strong>",
        "note": "Same page statement (obtained 2026-10-08): no H5 detections in poultry or livestock in Australia. (Source: Agriculture Victoria; this card will be updated once officially confirmed)"
      }
    },
    {
      "state": "NSW",
      "tone": "emerald",
      "asof": "2026-09-16",
      "zh": {
        "title": "新州 (NSW) · 維持自願性質",
        "short": "維持自願性質：僅建議自願移入室內，暫無強制立法管制（尚未用官方原文重新核對）。",
        "body": "新州 DPIRD 維持彈性，僅建議自由放養與後院戶「在符合動物福利前提下自願移入室內」，暫無強制立法管制。",
        "note": ""
      },
      "en": {
        "title": "NSW · Voluntary Recommendation",
        "short": "Voluntary: housing is only recommended, no mandatory legislation (not re-checked against the official text).",
        "body": "NSW DPIRD maintains flexibility, strongly encouraging voluntary indoor housing without mandatory legislative lockdowns.",
        "note": ""
      }
    }
  ]
};

window.PolicyStatus = (function () {
    var TONE = { amber: 'text-amber-400', emerald: 'text-emerald-400' };
    function find(state) {
        var d = window.policyStatusEmbedded;
        if (!d || !d.items) return null;
        for (var i = 0; i < d.items.length; i++) if (d.items[i].state === state) return d.items[i];
        return null;
    }
    function days(item) {
        var t = new Date(item.asof + 'T00:00:00Z');
        return isNaN(t.getTime()) ? null : Math.floor((Date.now() - t.getTime()) / 86400000);
    }
    function full(item, lang) {
        var L = item[lang] || item.zh;
        return '<strong class="' + (TONE[item.tone] || TONE.amber) + ' block mb-0.5 font-bold">' + L.title + '</strong>' +
            '<p class="text-[11px] text-slate-300 leading-relaxed">' + L.body + '</p>' +
            (L.note ? '<p class="text-[10px] text-slate-400 leading-relaxed mt-1">' + L.note + '</p>' : '');
    }
    /* 首頁政策卡：整塊改由資料產生；data-asof 同步，既有的 markAsOf() 會在 load 時補上過期警示 */
    function fill(el, state, lang) {
        var it = find(state);
        if (!el || !it) return false;
        el.innerHTML = full(it, lang);
        el.setAttribute('data-asof', it.asof);
        return true;
    }
    /* 風險評估頁的精簡一行（含自己的過期警示，不依賴 markAsOf） */
    function compact(state, lang) {
        var it = find(state);
        if (!it) return '';
        var L = it[lang] || it.zh, n = days(it), stale = n !== null && n > 14, en = lang === 'en';
        var label = en
            ? (stale ? '⚠️ ' : '') + 'as of ' + it.asof + (n !== null ? ' (' + n + ' d ago' + (stale ? ', may be out of date' : '') + ')' : '')
            : (stale ? '⚠️ ' : '') + '資料截至 ' + it.asof + (n !== null ? '（' + n + ' 天前' + (stale ? '，可能已過期' : '') + '）' : '');
        return '<div><strong class="' + (TONE[it.tone] || TONE.amber) + '">' + L.title + '</strong> <span class="text-slate-300">' + L.short +
            '</span> <span class="font-mono text-[10px] ' + (stale ? 'text-amber-300' : 'text-slate-500') + '">' + label + '</span></div>';
    }
    return { find: find, days: days, full: full, fill: fill, compact: compact };
})();
