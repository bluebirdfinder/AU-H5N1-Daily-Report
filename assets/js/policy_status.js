/* 各州家禽圈養令現況：首頁政策卡（report_template*.html）與風險評估頁（risk_assessment*.html）共用。
 * 更新政策時只改下面的資料，並同步 asof（官方原文最後取得日）；不要再改各頁面的寫死文字。
 * 這是人工維護的資料檔，h5n1.py 不會覆寫它。 */
window.policyStatusEmbedded = {
  "updated": "2026-11-26",
  "note": "各州家禽圈養令現況。首頁政策卡與風險評估頁共用此檔，更新時只改這裡；asof＝官方原文最後取得日（超過 14 天頁面會顯示 ⚠️）。",
  "items": [
    {
      "state": "VIC",
      "tone": "amber",
      "asof": "2026-11-26",
      "zh": {
        "title": "維州 (VIC) · 家禽臨時圈養令已於 2026 年 10 月 16 日結束",
        "short": "強制圈養要求已結束（官方新聞稿 2026-10-16）；官方仍強烈鼓勵業者持續隔離家禽與野鳥，並保留日後再發布管制令的權限。",
        "body": "維州農業局新聞稿（2026-10-16）宣布，大墨爾本及指定沿海與鄰近地區（飼養 50 隻以上家禽者）的<strong class=\"text-amber-300\">臨時圈養要求已於 2026 年 10 月 16 日結束</strong>；官方列出的理由是預報夏季氣溫高於平均，加上動物福利考量。維州首席獸醫官<strong class=\"text-amber-300\">強烈鼓勵所有業者繼續採取一切可行措施</strong>：讓家禽與野鳥保持隔離、保護飼料與飲水不被野鳥接觸、防止野鳥進入禽舍與活動場地，並保留依《1994 年牲畜疾病控制法》於情況改變時再發布管制令的權限。",
        "note": "本站註：圈養要求結束代表防護放寬，並非疫情緩解——同一份新聞稿指出野生動物的檢出仍在全州持續，澳洲則尚無家禽或牲畜的 H5 檢出。維州 H5 主頁目前列出的管制令只剩野生動物屍體處理相關兩項，不含家禽圈養。（來源：Agriculture Victoria 新聞稿 2026-10-16 與 H5 主頁，2026-11-26 讀取）"
      },
      "en": {
        "title": "VIC · Temporary poultry confinement requirement ended on 16 October 2026",
        "short": "The mandatory confinement requirement ended (official media release, 16 Oct 2026); producers are still strongly encouraged to keep poultry separated from wild birds, and the Chief Veterinary Officer retains the power to issue new Control Orders.",
        "body": "An Agriculture Victoria media release (16 Oct 2026) announced that the temporary requirements for poultry producers (50 or more poultry) in metropolitan Melbourne and specified coastal and adjacent areas <strong class=\"text-amber-300\">ended on 16 October 2026</strong>; the stated reasons are forecast hotter-than-average summer temperatures together with animal welfare considerations. Victoria's Chief Veterinary Officer <strong class=\"text-amber-300\">strongly encourages all producers to keep using every practical measure</strong>: keep poultry separated from wild birds, protect feed and water from wild bird access, and prevent wild birds entering sheds and yards. The Chief Veterinary Officer retains the authority to issue future Control Orders under the Livestock Disease Control Act 1994 if the situation changes.",
        "note": "Site note: ending the confinement requirement is a loosening of protection, not an easing of the outbreak: the same release says detections in wildlife continue across the state, while there have been no H5 detections in Australian poultry or livestock. The control orders now listed on the Victorian H5 page are only the two on dead wildlife handling; none concerns poultry confinement. (Source: Agriculture Victoria media release 16 Oct 2026 and H5 page, read 2026-11-26)"
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
