def get_page_html() -> str:
    return r"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>Shiritori</title>
  <style>
    :root{
      --ig1:#f09433; --ig2:#e6683c; --ig3:#dc2743; --ig4:#cc2366; --ig5:#bc1888;
      --text:#111827; --bg:#f6f7fb; --card:#ffffff; --muted:#6b7280;
      --chip-bg:#fff0f6; --chip-text:#be185d;
      --overlay: rgba(0,0,0,0.45);
      --border:#e5e7eb;
      --shadow:0 10px 28px rgba(0,0,0,0.10);
      --radius:16px;
      --dm-user:#e8f0fe; --dm-system:#ffffff;

      --sq-bg: linear-gradient(135deg, #cc2366, #dc2743);
      --sq-fg: #ffffff;
    }
    @media (prefers-color-scheme: dark){
      :root{
        --text:#e5e7eb; --bg:#0b1020; --card:#12192a; --muted:#9aa3b2;
        --chip-bg:#331828; --chip-text:#f472b6;
        --overlay: rgba(0,0,0,0.6);
        --border:#223047; --shadow:0 10px 28px rgba(0,0,0,0.35);
        --dm-user:#1e293b; --dm-system:#0f172a;

        --sq-bg: linear-gradient(135deg, #5e1039, #7a1f3e);
        --sq-fg: #fff;
      }
    }

    /* ★ けいフォント読み込み（static/keifont.ttf） */
    @font-face{
      font-family: "KeiFont";
      src: url("/static/keifont.ttf") format("truetype");
      font-display: swap;
    }

    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0; color:var(--text); background: var(--bg);
      font-family: "KeiFont", system-ui, -apple-system, "Segoe UI", Roboto, "Hiragino Sans", "Noto Sans JP", sans-serif;
      -webkit-text-size-adjust: 100%;
      padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
    }
    a, button { -webkit-tap-highlight-color: transparent; }
    :focus-visible { outline: 2px solid #60a5fa; outline-offset: 2px; border-radius: 8px; }

    .container { max-width: 1200px; margin: 0 auto; padding: 12px; }
    .card { background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; }

    /* header */
    .header { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px; }
    h1 {
      margin: 0; font-size: 20px; font-weight: 900; letter-spacing:.02em;
      background: linear-gradient(45deg, var(--ig1), var(--ig2), var(--ig3), var(--ig4), var(--ig5));
      -webkit-background-clip: text; background-clip: text; color: transparent;
    }
    .header-actions { display:flex; gap:8px; align-items:center; }

    /* top bar */
    .topbar { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px; }
    .time-buttons { display:flex; gap:6px; flex-wrap:wrap; }
    .btn {
      padding: 8px 12px; border-radius: 12px; border:1px solid transparent;
      color: #fff; cursor: pointer; user-select:none;
      background: linear-gradient(135deg, var(--ig5), var(--ig3));
      box-shadow: 0 6px 16px rgba(204,35,102,0.2);
      transition: transform .05s ease, filter .15s ease, opacity .15s ease;
      touch-action: manipulation; font-weight:700; font-size:14px;
    }
    .btn:active { transform: translateY(1px); filter: brightness(.98); }
    .btn.ghost { background: #e5e7eb; color: #111827; box-shadow:none; border-color: var(--border); }
    @media (prefers-color-scheme: dark){ .btn.ghost { background:#374151; color:#e5e7eb; border-color:#4b5563; } }
    .btn.small { padding:6px 10px; border-radius:10px; font-size:13px; }

    /* 2カラム */
    .layout{
      display:grid;
      grid-template-columns: clamp(300px, 28%, 360px) 1fr;
      gap:12px; align-items:start;
    }
    .side { display:flex; flex-direction:column; gap:12px; }

    .square-grid{
      display:grid;
      grid-template-columns: repeat(2, 1fr);
      gap:12px;
    }
    .square{
      aspect-ratio: 1 / 1;
      border:1px solid var(--border); border-radius:16px; box-shadow: var(--shadow);
      background: var(--sq-bg); color: var(--sq-fg);
      display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px;
      padding:10px; text-shadow: 0 1px 0 rgba(0,0,0,.35);
    }
    .square .label{ font-weight:800; opacity:.95; }
    .square .big{ font-size: clamp(34px, 6vw, 48px); font-weight:900; line-height:1; letter-spacing:.02em; }

    .pref-mode { font-weight:700; color: var(--chip-text); background: var(--chip-bg);
                 border:1px solid rgba(0,0,0,0.06); padding:8px 10px; border-radius:999px; display:inline-block; }

    .stat-box{
      border:1px solid var(--border); border-radius:16px; background: var(--card); box-shadow: var(--shadow);
      padding:14px; display:flex; flex-direction:column; gap:8px;
    }
    .stat-title{ font-weight:800; opacity:.8; }
    .score-big{
      font-size: clamp(28px, 4vw, 36px);
      font-weight:900; letter-spacing: 0.02em;
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum" 1, "lnum" 1;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    }
    .time-big{ font-size: clamp(26px, 4vw, 34px); font-weight:900; font-variant-numeric: tabular-nums; }

    .chat-wrap{ position: relative; border: 1px solid var(--border); border-radius: 14px; background: color-mix(in oklab, var(--card), #ffffff 6%); overflow: hidden; }
    .chat{
      height: min(54svh, 520px);
      overflow-y: auto; padding: 10px 10px 14px;
      display:flex; flex-direction:column; justify-content:flex-end; gap:8px;
      scroll-behavior: smooth;
    }
    .msg{ display:flex; align-items:flex-end; gap:8px; }
    .msg.system{ justify-content:flex-start; }
    .msg.user{ justify-content:flex-end; }
    .avatar{ width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, var(--ig2), var(--ig5)); flex: 0 0 auto; }
    .avatar.user{ background: linear-gradient(135deg, #60a5fa, #a78bfa); }
    .bubble{ max-width: min(76%, 880px); padding: 10px 12px; border-radius: 14px; line-height:1.5; box-shadow: 0 2px 6px rgba(0,0,0,0.06); word-break: break-word; white-space: pre-wrap; }
    .system .bubble{ background: var(--dm-system); border-top-left-radius: 6px; }
    .user   .bubble{ background: var(--dm-user);   border-top-right-radius: 6px; }

    .input-row{ display:flex; gap:8px; align-items:center; padding-top:8px; }
    input[type=text]{
      flex: 1; padding: 12px 14px; border-radius: 10px; border: 1px solid #cbd5e1; font-size:16px;
      background: var(--card); color: var(--text);
    }
    .error{ color: #fca5a5; margin-top: 6px; min-height:1em; }

    /* 攻め指定 */
    .prefer-pane{
      position: relative;
      display:flex;
      flex-direction:column;
      align-items:flex-end;
    }
    .prefer-card{
      display:none;
      width: min(360px, 86vw);
      background: var(--card);
      border:1px solid var(--border);
      border-radius: 12px;
      box-shadow: var(--shadow);

      /* ★ ここが本命：閉じるボタンより下から「本文が始まる」ように上paddingを増やす */
      padding: 12px;
      padding-top: 52px; /* ← 閉じるボタンの高さ＋余白を確保（被り完全回避） */

      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      z-index: 999;
    }
    .prefer-card.show{ display:block; }

    .prefer-head{
      display:flex;
      align-items:center;
      justify-content:flex-end;
      gap:8px;

      /* ★ ヘッダーはカードの一番上に「浮かせる」 */
      position: absolute;
      top: 12px;
      right: 12px;
      left: 12px;
      height: 32px;
    }

    /* タイトル（終端〜）を「本文開始位置」に置くので、見た目の余白を少し追加 */
    .prefer-title{
      font-weight:800;
      font-size:14px;
      color:var(--text);
      text-align:center;
      width: 100%;
      padding-top: 6px; /* ← 要望：終端〜の文面の上にさらにpadding */
    }

    /* 説明文（指定の文面に変更） */
    .prefer-desc{
      margin-top: 10px;
      margin-bottom: 10px;
      text-align: center;
      line-height: 1.6;
    }

    .prefer-list{ display:flex; flex-wrap:wrap; gap:6px; margin:10px 0 10px; justify-content:center; }

    .prefer-chip{
      padding: 6px 10px; border-radius: 999px;
      border:1px solid var(--border);
      background: color-mix(in oklab, var(--card), #ffffff 4%);
      font-weight:700; cursor:pointer;
    }

    /* 送信の真下にクリア（サイズ統一） */
    .prefer-input-row{
      display:flex;
      gap:8px;
      align-items:flex-start;
      justify-content:center;
    }
    .prefer-actions{
      display:flex;
      flex-direction:column;
      gap:8px;
    }

    .modal{ position: fixed; inset: 0; background: var(--overlay); display:none; z-index:1000; }
    .modal.show{ display:block; }
    .modal-inner{ position:absolute; inset: 6% 4%; background: var(--card); border-radius: 16px; box-shadow: var(--shadow); border:1px solid var(--border); padding:16px; display:flex; flex-direction:column; gap:10px; }
    .modal-header{ display:flex; align-items:center; justify-content:space-between; }
    .modal-title{ font-weight:800; }
    .modal-close{ border:none; background:transparent; font-size:22px; cursor:pointer; color:#9aa3b2; }

    .mobile-hud{ display:none; margin-top:6px; gap:6px; flex-wrap:wrap; }
    .chip{ padding: 6px 10px; border-radius: 999px; background: var(--chip-bg); color:var(--chip-text); border:1px solid rgba(0,0,0,0.06); }
    .timer{ font-variant-numeric: tabular-nums; font-weight: 800; }

    @media (max-width: 900px){
      .layout{ display:block; }
      .chat{ height: min(58svh, 520px); }
    }

    @media (max-width: 640px){
      .mobile-hud{ display:flex; }
      .time-buttons .btn{ padding:6px 9px; font-size:12px; }
      h1{ font-size:18px; }
      .bubble{ max-width: 86%; }
      .modal-inner{ inset: 4% 3%; }
      .side{ display:none; }

      .prefer-card{
        position: fixed;
        left: 0;
        right: 0;
        top: calc(env(safe-area-inset-top) + 64px);
        width: 100vw;
        max-width: 100vw;
        border-radius: 0;
        text-align: center;

        /* ★ スマホでも同じ考え方で上paddingを確保 */
        padding-top: 58px;
        min-height: 300px;
        max-height: 72svh;
        overflow: auto;
        -webkit-overflow-scrolling: touch;
      }

      .prefer-head{
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        height: 34px;
        justify-content:flex-end;
      }

      .prefer-title{
        padding-top: 10px;
      }

      #kanaInput{
        flex: 0 1 auto;
        width: min(64vw, 320px);
      }
    }
  </style>
</head>
<body>
  <div class="container" id="page">
    <div class="card">
      <div class="header">
        <h1>Shiritori</h1>

        <div class="header-actions">
          <div class="prefer-pane">
            <button class="btn small" id="preferToggle" onclick="togglePreferPane()">攻め指定</button>

            <div class="prefer-card" id="preferCard" aria-label="攻め指定パネル">
              <div class="prefer-head">
                <button class="btn ghost small" onclick="togglePreferPane(false)">閉じる</button>
              </div>

              <div class="prefer-title">終端に優先したい文字を登録（最大3文字）</div>

              <div class="muted prefer-desc">
                入力→Enter/送信で追加完了<br/>
                ※3文字入力済みの場合はクリアすると変更できます
              </div>

              <div class="prefer-input-row">
                <input id="kanaInput" type="text" placeholder="例：かさた（最大3文字）" inputmode="kana" maxlength="3"
                       enterkeyhint="send" autocomplete="off" autocapitalize="none" spellcheck="false" lang="ja"/>
                <div class="prefer-actions">
                  <button class="btn small" id="preferSendBtn" onclick="addPreferKana()">送信</button>
                  <button class="btn small" id="preferClearBtn" onclick="clearKana()">クリア</button>
                </div>
              </div>

              <div class="prefer-list" id="preferList"></div>
            </div>
          </div>

          <button class="btn ghost small" onclick="openRules()">？</button>
        </div>
      </div>

      <div class="topbar">
        <div class="time-buttons">
          <button class="btn ghost small" onclick="startGame(1)">1分</button>
          <button class="btn ghost small" onclick="startGame(3)">3分</button>
          <button class="btn ghost small" onclick="startGame(5)">5分</button>
          <button class="btn small" onclick="startGame('endless')">エンドレス</button>
        </div>
      </div>

      <div class="layout">
        <aside class="side">
          <div class="square-grid">
            <div class="square">
              <div class="label">ボーナス</div>
              <div class="big" id="bonus_square">-</div>
            </div>
            <div class="square">
              <div class="label">文字数</div>
              <div class="big" id="len_square">-</div>
            </div>
          </div>

          <div class="pref-mode" id="pref_mode">モードOFF</div>

          <div class="stat-box">
            <div class="stat-title">ポイント</div>
            <div class="score-big" id="score_big">0000</div>
          </div>
          <div class="stat-box">
            <div class="stat-title">残り時間</div>
            <div class="time-big" id="time_big">--:--</div>
          </div>
        </aside>

        <main>
          <div class="chat-wrap">
            <div class="chat" id="chat" tabindex="0" title="ここをクリックすると入力欄にフォーカスします"></div>
          </div>
          <div class="input-row">
            <input id="inputWord" type="text" placeholder="ひらがなで入力（例：さくら）"
                   autofocus enterkeyhint="send" autocomplete="off" autocapitalize="none" spellcheck="false" lang="ja"/>
            <button id="sendBtn" class="btn" onclick="submitWord()">送信</button>
          </div>

          <div class="mobile-hud" id="mobile_hud">
            <span class="chip">ボーナス: <strong id="bonus_chip">-</strong></span>
            <span class="chip">文字数: <strong id="len_chip">-</strong></span>
            <span class="chip">ポイント: <strong id="score_chip">0000</strong></span>
            <span class="chip">残り: <strong class="timer" id="time_chip">--:--</strong></span>
          </div>

          <div id="error" class="error"></div>
        </main>
      </div>
    </div>
  </div>

  <div class="modal" id="rulesModal" aria-hidden="true">
    <div class="modal-inner" role="dialog" aria-modal="true" aria-label="ルール">
      <div class="modal-header">
        <div class="modal-title">ルール</div>
        <button class="modal-close" title="閉じる" onclick="closeRules()" aria-label="閉じる">×</button>
      </div>
      <div style="line-height:1.7; font-size:14px;">
        ・ひらがな限定（「ヴ」のカタカナは可）<br/>
        ・2〜3文字は無効／末尾「ん」は無効<br/>
        ・拗音は大きく扱う・長音は1つ前の文字<br/>
        ・末尾「ぢ」「づ」→ 開始「じ」「ず」
      </div>
      <div style="display:flex; justify-content:flex-end;">
        <button class="btn ghost small" onclick="closeRules()">閉じる</button>
      </div>
    </div>
  </div>

<script>
let pollTimer = null;
let selectedKana = new Set();
let sending = false;
let gameRunning = false;
const PREFER_MAX = 3;
let preferLocked = false;

function focusInput(moveToEnd=true) {
  const inp = document.getElementById("inputWord");
  if (!inp) return;
  inp.focus({ preventScroll: true });
  if (moveToEnd) { const v = inp.value; inp.value = ""; inp.value = v; }
}

function scrollToGameArea(){
  if (window.innerWidth > 900) return;
  const target =
    document.getElementById("mobile_hud") ||
    document.getElementById("inputWord") ||
    document.getElementById("chat");
  if (!target) return;

  const doScroll = () => {
    try { target.scrollIntoView({ behavior: "smooth", block: "end" }); }
    catch(e){
      const rect = target.getBoundingClientRect();
      window.scrollTo(0, rect.top + window.pageYOffset - 40);
    }
  };

  doScroll();
  setTimeout(doScroll, 300);
}

function startGame(minsOrMode) {
  const prefer_ends = Array.from(selectedKana);
  const payload = (minsOrMode === 'endless')
      ? { mode: 'endless', prefer_ends }
      : { minutes: minsOrMode, prefer_ends };
  fetch("/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  }).then(r => r.json()).then(state => {
    updateUIFromState(state);
    focusInput();
    scrollToGameArea();
  });
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(fetchState, 500);
}

function fetchState() { fetch("/state").then(r => r.json()).then(updateUIFromState); }

function submitWord() {
  if (sending) return;
  const wordEl = document.getElementById("inputWord");
  const word = wordEl.value;
  if (!word) { focusInput(false); return; }
  sending = true;
  document.getElementById("sendBtn").disabled = true;

  fetch("/play", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ word: word })
  }).then(r => r.json()).then(res => {
    updateUIFromState(res);
    if (!res.error) { wordEl.value = ""; }
    focusInput(false);
  }).finally(()=>{
    sending = false;
    document.getElementById("sendBtn").disabled = false;
  });
}

function pad4(n){ n = Number(n||0); return n.toString().padStart(4, "0"); }

function setTimeViews(sec, isEndless){
  const t_big  = document.getElementById("time_big");
  const t_chip = document.getElementById("time_chip");
  if (isEndless){ t_big.textContent="∞"; if(t_chip) t_chip.textContent="∞"; return; }
  const s = Math.max(0, Math.floor(sec||0));
  const mm = String(Math.floor(s/60)).padStart(2,"0");
  const ss = String(s%60).padStart(2,"0");
  const val = `${mm}:${ss}`;
  t_big.textContent = val;
  if (t_chip) t_chip.textContent = val;
}

function setPrefMode(prefs){
  const txt = (prefs && prefs.length) ? (prefs.join("・") + " モード") : "モードOFF";
  document.getElementById("pref_mode").textContent = txt;
}

function updatePreferControls(){
  const input = document.getElementById("kanaInput");
  const btn = document.getElementById("preferSendBtn");
  const disabled = preferLocked;
  if (input) input.disabled = disabled;
  if (btn) btn.disabled = disabled;
}

function updateUIFromState(state) {
  const chat = document.getElementById("chat");
  const score_big = document.getElementById("score_big");
  const score_chip = document.getElementById("score_chip");
  const len_square = document.getElementById("len_square");
  const bonus_square = document.getElementById("bonus_square");
  const len_chip = document.getElementById("len_chip");
  const bonus_chip = document.getElementById("bonus_chip");
  const err = document.getElementById("error");

  gameRunning = !!state.is_running && (state.time_left || 0) > 0;

  chat.innerHTML = "";
  (state.messages || []).forEach(m => {
    const row = document.createElement("div");
    row.className = "msg " + (m.side === "user" ? "user" : "system");

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = m.text;

    const av = document.createElement("div");
    av.className = "avatar " + (m.side === "user" ? "user" : "system");

    if (m.side === "user") { row.appendChild(bubble); row.appendChild(av); }
    else { row.appendChild(av); row.appendChild(bubble); }

    chat.appendChild(row);
  });
  chat.scrollTop = chat.scrollHeight;

  const sc = pad4(state.score ?? 0);
  score_big.textContent = sc;
  if (score_chip) score_chip.textContent = sc;

  const tgt = state.target_len ?? "-";
  const bon = state.bonus_char || "-";
  len_square.textContent = tgt;
  bonus_square.textContent = bon;
  if (len_chip) len_chip.textContent = tgt;
  if (bonus_chip) bonus_chip.textContent = bon;

  setTimeViews(state.time_left, !!state.is_endless);

  err.textContent = state.error || "";

  const prefs = (state.prefer_ends || []);
  setPrefMode(prefs);

  updatePreferControls();

  if (state.whose_turn === "user" && gameRunning) { focusInput(false); }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.isComposing) {
    const pane = document.getElementById("preferCard");
    if (pane.classList.contains("show")) {
      e.preventDefault(); addPreferKana(); return;
    }
    e.preventDefault(); submitWord(); return;
  }
  const active = document.activeElement;
  const isTypingKey = (e.key && e.key.length === 1) && !e.ctrlKey && !e.metaKey && !e.altKey;
  if (isTypingKey && (!active || (active.id !== "inputWord" && active.id !== "kanaInput" && active.tagName !== "INPUT" && active.tagName !== "TEXTAREA"))) {
    if (gameRunning) {
      focusInput(false);
    }
  }
});

function togglePreferPane(force){
  const card = document.getElementById("preferCard");
  const show = (typeof force === "boolean") ? force : !card.classList.contains("show");
  card.classList.toggle("show", show);
  if (show) {
    const input = document.getElementById("kanaInput");
    if (input && !preferLocked) input.focus({preventScroll:true});
  }
  renderPreferList();
  updatePreferControls();
}

function hiraOnly(ch){
  if (!ch) return "";
  const katakana = "ァァィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲンヴー";
  const hira     = "ぁあぃいぅうぇえぉおかがきぎぐけげこごさざしじすすせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろわをんゔー";
  const i = katakana.indexOf(ch);
  if (i >= 0) ch = hira[i];
  if (/^[ぁ-ゖゔ]$/.test(ch)) return ch;
  return "";
}

function addPreferKana(){
  const input = document.getElementById("kanaInput");
  const raw = (input.value || "").trim();
  if (!raw) return;

  if (preferLocked) {
    flashError("攻め指定は最大3文字です。クリアすると変更できます。");
    input.select();
    return;
  }

  let added = false;
  for (const chRaw of raw) {
    if (selectedKana.size >= PREFER_MAX) { preferLocked = true; break; }
    const ch = hiraOnly(chRaw);
    if (!ch) continue;
    if (!selectedKana.has(ch)) { selectedKana.add(ch); added = true; }
  }

  if (!added) {
    if (!preferLocked) { flashError("ひらがなを入力してください"); input.select(); }
    else { flashError("攻め指定は最大3文字です。クリアすると変更できます。"); }
    return;
  }

  if (selectedKana.size >= PREFER_MAX) preferLocked = true;

  input.value = "";
  renderPreferList();
  renderPrefViewOnly();
  updatePreferControls();

  if (!preferLocked) input.focus({preventScroll:true});
}

function renderPreferList(){
  const list = document.getElementById("preferList");
  list.innerHTML = "";
  Array.from(selectedKana).forEach(ch=>{
    const span = document.createElement("span");
    span.className = "prefer-chip";
    span.textContent = ch;
    span.title = preferLocked ? "3文字入力済み。変更するにはクリアしてください。" : "クリックで削除";
    span.addEventListener("click", ()=>{
      if (preferLocked) { flashError("3文字入力済みです。変更する場合はクリアしてください。"); return; }
      selectedKana.delete(ch);
      renderPreferList();
      renderPrefViewOnly();
    });
    list.appendChild(span);
  });
}

function renderPrefViewOnly(){
  const prefs = Array.from(selectedKana);
  setPrefMode(prefs);
}

function clearKana(){
  selectedKana.clear();
  preferLocked = false;
  renderPreferList();
  renderPrefViewOnly();
  updatePreferControls();
  const input = document.getElementById("kanaInput");
  if (input) { input.value = ""; input.focus({preventScroll:true}); }
}

function openRules(){ document.getElementById("rulesModal").classList.add("show"); }
function closeRules(){ document.getElementById("rulesModal").classList.remove("show"); }

function flashError(msg){
  const el = document.getElementById("error");
  el.textContent = msg || "";
  if (!msg) return;
  el.style.transition = "none";
  el.style.opacity = "1";
  requestAnimationFrame(()=>{
    el.style.transition = "opacity .9s ease";
    el.style.opacity = "0.001";
    setTimeout(()=>{ el.textContent=""; el.style.opacity="1"; }, 900);
  });
}

document.getElementById("chat").addEventListener("click", () => { if (gameRunning) focusInput(false); });
document.getElementById("page").addEventListener("click", (e) => {
  if (!gameRunning) return;
  const id = (e.target && e.target.id) || "";
  if (id !== "inputWord" && id !== "sendBtn" && id !== "kanaInput") focusInput(false);
});
window.addEventListener("load", () => { fetchState(); focusInput(); renderPreferList(); updatePreferControls(); });
</script>
</body>
</html>"""
