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
    }

    * { box-sizing: border-box; }
    body {
      margin:0; background:var(--bg); color:var(--text);
      font-family: system-ui, -apple-system, "Hiragino Sans", "Noto Sans JP", sans-serif;
    }

    .btn{
      padding:8px 12px;
      border-radius:12px;
      font-weight:700;
      border:none;
      cursor:pointer;
      background:linear-gradient(135deg,#cc2366,#dc2743);
      color:#fff;
    }
    .btn.small{ padding:6px 10px; font-size:13px; }
    .btn.ghost{
      background:#e5e7eb;
      color:#111827;
    }

    .prefer-pane{ position:relative; }
    .prefer-card{
      display:none;
      position:absolute;
      right:0;
      top:calc(100% + 8px);
      width:min(360px,86vw);
      background:var(--card);
      border:1px solid var(--border);
      border-radius:12px;
      padding:12px;
      box-shadow:var(--shadow);
      z-index:999;
    }
    .prefer-card.show{ display:block; }

    .prefer-head{
      display:flex;
      justify-content:space-between;
      align-items:center;
    }
    .prefer-title{
      font-weight:800;
      font-size:14px;
    }

    /* ★ 修正1：説明文をヘッダーから明確に分離 */
    .prefer-desc{
      margin-top:12px;
      margin-bottom:8px;
      font-size:13px;
      color:var(--muted);
      text-align:center;
    }

    .input-row{
      display:flex;
      gap:8px;
      align-items:flex-start;
      justify-content:center;
    }

    .prefer-actions{
      display:flex;
      flex-direction:column;
      gap:6px;
    }

    .prefer-list{
      display:flex;
      gap:6px;
      flex-wrap:wrap;
      justify-content:center;
      margin:10px 0;
    }
    .prefer-chip{
      padding:6px 10px;
      border-radius:999px;
      border:1px solid var(--border);
      cursor:pointer;
    }

    @media (max-width:640px){
      .prefer-card{
        position:fixed;
        left:0;
        right:0;
        top:64px;
        width:100vw;
        border-radius:0;
        min-height:300px;
        max-height:72svh;
        overflow:auto;
      }
    }
  </style>
</head>
<body>

<div class="prefer-pane">
  <button class="btn small" onclick="togglePreferPane()">攻め指定</button>

  <div class="prefer-card" id="preferCard">
    <div class="prefer-head">
      <div class="prefer-title">終端に優先したい文字を登録（最大3文字）</div>
      <button class="btn ghost small" onclick="togglePreferPane(false)">閉じる</button>
    </div>

    <!-- ★ ここが被ってた説明文：完全に下へ -->
    <div class="prefer-desc">
      ひらがなを最大3文字まとめて入力 → Enter / 送信で追加
    </div>

    <div class="input-row">
      <input id="kanaInput" type="text" maxlength="3" placeholder="例：かさた"/>
      <div class="prefer-actions">
        <button class="btn small" onclick="addPreferKana()">送信</button>
        <button class="btn small" onclick="clearKana()">クリア</button>
      </div>
    </div>

    <div class="prefer-list" id="preferList"></div>

    <div class="prefer-desc">
      ※ 3文字入力済みの場合はクリアすると変更できます
    </div>
  </div>
</div>

<script>
function togglePreferPane(force){
  const card = document.getElementById("preferCard");
  const show = (typeof force === "boolean") ? force : !card.classList.contains("show");
  card.classList.toggle("show", show);
}
function addPreferKana(){}
function clearKana(){}
</script>

</body>
</html>"""
