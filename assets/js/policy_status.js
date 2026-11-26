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
        "body": "維州農業局新聞稿（2026-10-16）宣布，大墨爾本及指定沿海與鄰近地區的<strong class=\"text-amber-300\">臨時圈養要求已於 2026 年 10 月 16 日結束</strong>；官方列出的理由是預報夏季氣溫高於平均，加上動物福利考量。維州首席獸醫官<strong class=\"text-amber-300\">強烈鼓勵所有業者繼續採取一切可行措施</strong>：讓家禽與野鳥保持隔離、保護飼料與飲水不被野鳥接觸、防止野鳥進入禽舍與活動場地，並保留依《1994 年牲畜疾病控制法》於情況改變時再發布管制令的權限。",
        "note": "本站註：圈養要求結束代表防護放寬，並非疫情緩解——同一份新聞稿指出野生動物的檢出仍在全州持續，澳洲則尚無家禽或牲畜的 H5 檢出。維州 H5 主頁目前列出的管制令只剩野生動物屍體處理相關兩項，不含家禽圈養。結束前的規定：依維州農業局 2026-08-21 新聞稿，沿海與南部各郡飼養 50 隻以上家禽者須圈養（當時延長至少 28 天），其他地區僅為建議。（來源：Agriculture Victoria 新聞稿 2026-10-16、2026-08-21 與 H5 主頁，2026-11-26 讀取）"
      },
      "en": {
        "title": "VIC · Temporary poultry confinement requirement ended on 16 October 2026",
        "short": "The mandatory confinement requirement ended (official media release, 16 Oct 2026); producers are still strongly encouraged to keep poultry separated from wild birds, and the Chief Veterinary Officer retains the power to issue new Control Orders.",
        "body": "An Agriculture Victoria media release (16 Oct 2026) announced that the temporary requirements for poultry producers in metropolitan Melbourne and specified coastal and adjacent areas <strong class=\"text-amber-300\">ended on 16 October 2026</strong>; the stated reasons are forecast hotter-than-average summer temperatures together with animal welfare considerations. Victoria's Chief Veterinary Officer <strong class=\"text-amber-300\">strongly encourages all producers to keep using every practical measure</strong>: keep poultry separated from wild birds, protect feed and water from wild bird access, and prevent wild birds entering sheds and yards. The Chief Veterinary Officer retains the authority to issue future Control Orders under the Livestock Disease Control Act 1994 if the situation changes.",
        "note": "Site note: ending the confinement requirement is a loosening of protection, not an easing of the outbreak: the same release says detections in wildlife continue across the state, while there have been no H5 detections in Australian poultry or livestock. The control orders now listed on the Victorian H5 page are only the two on dead wildlife handling; none concerns poultry confinement. Rule before it ended: per the Agriculture Victoria media release of 21 Aug 2026, owners with 50 or more birds in coastal and southern shires were required to confine them (extended for at least 28 days then); elsewhere housing was only recommended. (Source: Agriculture Victoria media releases 16 Oct and 21 Aug 2026 and H5 page, read 2026-11-26)"
      }
    },
    {
      "state": "NSW",
      "tone": "emerald",
      "asof": "2026-11-26",
      "zh": {
        "title": "新州 (NSW) · 自願性圈養建議已延長至 2026 年 11 月 28 日",
        "short": "自願性建議（非強制命令）：新州首席獸醫官將自願圈養建議再延長 28 天，至 2026-11-28，之後視疫情檢討（NSW DPIRD 產業通報 2026-10-27）。",
        "body": "NSW DPIRD 產業通報（2026-10-27）：新州首席獸醫官因野生鳥類持續檢出，將<strong class=\"text-emerald-300\">自願性家禽圈養建議</strong>再延長 28 天，<strong class=\"text-emerald-300\">至 2026 年 11 月 28 日</strong>；建議將持續依疫情演變檢討，若風險狀況改變可能修訂，並會通知業界。這是建議而非強制命令。",
        "note": "本站註：此建議將於 2026-11-28 到期，到期後是否續延需待官方公告，本站尚未取得 11/28 之後的公告。來源是 NSW DPIRD 作者於 extensionaus 發布的產業通報（2026-10-27），不是 nsw.gov.au 主頁原文；nsw.gov.au 家禽業者頁（2026-11-26 讀取）本身不含圈養建議的日期。"
      },
      "en": {
        "title": "NSW · Voluntary housing recommendation extended to 28 November 2026",
        "short": "A voluntary recommendation (not a mandatory order): the NSW Chief Veterinary Officer extended it by a further 28 days, to 28 Nov 2026, with review to follow (NSW DPIRD industry update, 27 Oct 2026).",
        "body": "NSW DPIRD industry update (27 Oct 2026): because of continued detections in wild birds, the NSW Chief Veterinary Officer extended the <strong class=\"text-emerald-300\">voluntary housing recommendation for poultry</strong> by a further 28 days, <strong class=\"text-emerald-300\">until 28 November 2026</strong>. It will keep being reviewed as the disease situation evolves; if the risk profile changes it may be amended and industry will be informed. This is a recommendation, not a mandatory order.",
        "note": "Site note: the recommendation expires on 28 Nov 2026, and whether it is extended again depends on a later official announcement, which this site has not yet obtained. The source is the NSW DPIRD industry update (27 Oct 2026) published on extensionaus, not the nsw.gov.au home page text; the nsw.gov.au poultry producers page (read 2026-11-26) does not itself state the housing recommendation or its date."
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
