# Shiritori.py
# -*- coding: utf-8 -*-
import os
import random
import sqlite3
import time
import zipfile  # zip 展開用
from flask import Flask, request, session, jsonify, render_template_string

from InterFace import get_page_html  # ← UIは別ファイルに分離

# ====== 設定 ======
APP_SECRET = os.environ.get("SHIRITORI_SECRET", "change-me-please")

# ★ スクリプトと同じフォルダにある DB を使う
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "wordlist.db")
DB_ZIP_PATH = os.path.join(BASE_DIR, "wordlist.zip")  # ← ここを wordlist.zip に固定

TABLE_NAME = "words"
WORD_COL = "word"

# ★ 文字数分布（％）
#   5:14, 6:20, 7:23, 8:20, 9:10, 10:8, 11+:5
LENGTH_CHOICES = [5, 6, 7, 8, 9, 10, "11+"]
LENGTH_WEIGHTS = [14, 20, 23, 20, 10, 8, 5]

# 「11文字以上」を具体化する上限（必要あれば変更）
LONG_LEN_MAX = 500

# ユーザーに表示する「10以上」ラベル
TARGET_10PLUS_LABEL = "10以上"


# ====== DB の zip 展開ユーティリティ ======
def ensure_db_exists():
    """
    wordlist.db が無ければ、同じフォルダにある wordlist.zip から展開する。
    展開は「DBが無いときに1回だけ」。
    zip の中に wordlist.db が 1個入っている想定。
    """
    if os.path.exists(DB_PATH):
        print("[INFO] DB は既に存在しています:", DB_PATH)
        return

    if not os.path.exists(DB_ZIP_PATH):
        print("[WARN] DB_ZIP が見つかりません:", DB_ZIP_PATH)
        return

    print("[INFO] wordlist.db が無いため、wordlist.zip から展開します...")
    try:
        with zipfile.ZipFile(DB_ZIP_PATH, "r") as zf:
            # 中身を全部 BASE_DIR に展開
            zf.extractall(BASE_DIR)

        if os.path.exists(DB_PATH):
            print("[INFO] DB 展開完了:", DB_PATH)
        else:
            print("[WARN] zip を展開しましたが wordlist.db が見つかりませんでした。")
            print("       zip の中に wordlist.db が含まれているか確認してください。")
    except Exception as e:
        print("[ERROR] DB 展開に失敗しました:", e)


# モジュール読み込み時に一度だけチェック（Flask起動時にも効く）
ensure_db_exists()

# ====== Flask ======
app = Flask(__name__)
app.secret_key = APP_SECRET

# ====== ひらがな系ユーティリティ ======
HIRAGANA_START = ord("ぁ")
HIRAGANA_END = ord("ゖ")
SMALL_TO_LARGE = {
    "ぁ": "あ", "ぃ": "い", "ぅ": "う", "ぇ": "え", "ぉ": "お",
    "ゃ": "や", "ゅ": "ゆ", "ょ": "よ", "っ": "つ",
}

# ボーナスに使う候補（「んぢづ」は除外）
BONUS_KANA = [
    *list("あいうえお"),
    *list("かきくけこがぎぐげご"),
    *list("さしすせそざじずぜぞ"),
    *list("たちつてとだでど"),
    *list("なにぬねの"),
    *list("はひふへほばびぶべぼぱぴぷぺぽ"),
    *list("まみむめも"),
    *list("やゆよ"),
    *list("らりるれろ"),
    *list("わ"),
    "ゔ",
]


def kata_to_hira(s: str) -> str:
    res = []
    for ch in s:
        if ch == "ヴ":
            res.append("ゔ")
            continue
        code = ord(ch)
        if ch == "ー":
            res.append(ch)
        elif 0x30A1 <= code <= 0x30FA or ch in ("ヽ", "ヾ", "ヵ", "ヶ"):
            res.append(chr(code - 0x60))
        else:
            res.append(ch)
    return "".join(res)


def is_hiragana_str(s: str) -> bool:
    for ch in s:
        if ch == "ー":
            continue
        o = ord(ch)
        if not (HIRAGANA_START <= o <= HIRAGANA_END):
            return False
    return True


def normalize_input(s: str) -> str:
    return kata_to_hira(s.strip())


def last_effective_char(word: str) -> str:
    if not word:
        return ""
    i = len(word) - 1
    # 長音は1つ前を見る
    while i >= 0 and word[i] == "ー":
        i -= 1
    if i < 0:
        return ""
    ch = word[i]
    # 拗音(小書き)は大きく
    if ch in SMALL_TO_LARGE:
        ch = SMALL_TO_LARGE[ch]
    return ch


def next_required_start(last_char: str) -> str:
    if last_char == "ぢ":
        return "じ"
    if last_char == "づ":
        return "ず"
    return last_char


def valid_length(word: str) -> bool:
    return len(word) >= 4


def ends_with_n(word: str) -> bool:
    return word.endswith("ん")


def new_bonus_char() -> str:
    return random.choice(BONUS_KANA)


# --- 分布から長さをサンプル ---
def sample_weighted_length() -> int:
    """指定の分布に基づいて文字数を1つサンプルする。
       '11+' は 11..LONG_LEN_MAX のいずれかに具体化する。"""
    pick = random.choices(LENGTH_CHOICES, weights=LENGTH_WEIGHTS, k=1)[0]
    if pick == "11+":
        return random.randint(11, LONG_LEN_MAX)
    return int(pick)


def new_user_target_len():
    """ユーザーの指定文字数（ターゲット）を分布に従って決定。
       表示は 5/6/7/8/9/「10以上」の6種類。"""
    L = sample_weighted_length()
    if L >= 10:
        return TARGET_10PLUS_LABEL  # 「10以上」
    else:
        return int(L)               # 5〜9


# --- ボーナス一致（2倍判定） ---
def is_bonus_hit(user_word: str, bonus_char: str) -> bool:
    if not bonus_char:
        return False
    eff = last_effective_char(user_word)
    return eff == bonus_char


# --- 指定“終端文字”ユーティリティ ---
def sanitize_prefer_ends(items) -> list:
    res, seen = [], set()
    if not items:
        return res
    for x in items:
        if not x:
            continue
        c = normalize_input(str(x))[:1]
        if not c:
            continue
        if c in SMALL_TO_LARGE:
            c = SMALL_TO_LARGE[c]
        o = ord(c)
        if HIRAGANA_START <= o <= HIRAGANA_END and c not in seen:
            seen.add(c)
            res.append(c)
    return res


def ends_with_any_pref(word: str, prefs: list) -> bool:
    if not prefs:
        return False
    for c in prefs:
        if word.endswith(c) or word.endswith(c + "ー"):
            return True
    return False


# ====== DB ======
def db_connect():
    return sqlite3.connect(DB_PATH)


def db_has_word(w: str) -> bool:
    with db_connect() as con:
        cur = con.cursor()
        cur.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE {WORD_COL} = ? LIMIT 1", (w,))
        return cur.fetchone() is not None


# 候補から「語尾の均等ランダム」で1つ選ぶ（prefer_ends が空のときに使用）
def pick_balanced_by_end(candidates: list[str], used: set) -> str | None:
    # グループ化（末尾の有効文字）
    groups = {}
    for w in candidates:
        if w in used:
            continue
        if not is_hiragana_str(w):
            continue
        endc = last_effective_char(w)
        if not endc:
            continue
        groups.setdefault(endc, []).append(w)
    if not groups:
        return None
    keys = list(groups.keys())
    # 均等：終端キーを一様に抽選。外れたら別キーを再抽選。
    while keys:
        k = random.choice(keys)
        pool = groups[k]
        random.shuffle(pool)
        for w in pool:
            if w not in used:
                return w
        keys.remove(k)
    return None


def _fetch_candidates_with_length(
    where_sql: str,
    params: tuple,
    prefer_ends: list,
    used: set,
    limit: int = 800,
) -> list[str]:
    """与えた WHERE 条件で候補を取得して、prefer_ends を優先順に並べ替えて返す。"""
    with db_connect() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            f"""
            SELECT {WORD_COL} AS word FROM {TABLE_NAME}
            WHERE {where_sql}
            ORDER BY RANDOM()
            LIMIT {limit}
            """,
            params,
        )
        rows = [r["word"] for r in cur.fetchall()]

    if not rows:
        return []

    # prefer_ends がある場合は手前に寄せる
    if prefer_ends:
        pref = [w for w in rows if ends_with_any_pref(w, prefer_ends)]
        rest = [w for w in rows if w not in pref]
        rows = pref + rest

    # 既出や非ひらがなを除外
    filtered = [w for w in rows if (w not in used and is_hiragana_str(w))]
    return filtered


def db_random_starting_with(start_char: str, used: set, prefer_ends: list) -> str | None:
    """出現確率に従って“文字数を先に決めて”から、該当長の候補を抽選。"""
    desired_len = sample_weighted_length()

    def where_clause_for_len(L: int) -> tuple[str, tuple]:
        if L >= 11:
            return (
                f"substr({WORD_COL},1,1) = ? AND length({WORD_COL}) >= 4 "
                f"AND {WORD_COL} NOT LIKE '%ん' AND length({WORD_COL}) >= ?",
                (start_char, 11),
            )
        else:
            return (
                f"substr({WORD_COL},1,1) = ? AND length({WORD_COL}) >= 4 "
                f"AND {WORD_COL} NOT LIKE '%ん' AND length({WORD_COL}) = ?",
                (start_char, L),
            )

    # まずは希望長さで試す
    where_sql, params = where_clause_for_len(desired_len)
    candidates = _fetch_candidates_with_length(where_sql, params, prefer_ends, used, limit=800)
    if candidates:
        return candidates[0] if not prefer_ends else candidates[0]

    # 見つからなければフェールバック（長さ無視の従来挙動）
    with db_connect() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            f"""
            SELECT {WORD_COL} AS word FROM {TABLE_NAME}
            WHERE substr({WORD_COL},1,1) = ?
              AND length({WORD_COL}) >= 4
              AND {WORD_COL} NOT LIKE '%ん'
            ORDER BY RANDOM()
            LIMIT 800
            """,
            (start_char,),
        )
        rows = [row["word"] for row in cur.fetchall()]

    if not rows:
        return None

    if prefer_ends:
        pref = [w for w in rows if ends_with_any_pref(w, prefer_ends)]
        rest = [w for w in rows if w not in pref]
        rows = pref + rest

    random.shuffle(rows)
    for w in rows:
        if w not in used and is_hiragana_str(w):
            return w
    return None


def db_random_opening_word(used: set, prefer_ends: list) -> str | None:
    """開始語も分布に従った長さで抽選（無ければ従来挙動にフォールバック）。"""
    desired_len = sample_weighted_length()

    def where_clause_for_len(L: int) -> tuple[str, tuple]:
        if L >= 11:
            return (
                f"length({WORD_COL}) >= 4 AND {WORD_COL} NOT LIKE '%ん' AND length({WORD_COL}) >= ?",
                (11,),
            )
        else:
            return (
                f"length({WORD_COL}) >= 4 AND {WORD_COL} NOT LIKE '%ん' AND length({WORD_COL}) = ?",
                (L,),
            )

    # 希望長さでまず探す
    where_sql, params = where_clause_for_len(desired_len)
    candidates = _fetch_candidates_with_length(where_sql, params, prefer_ends, used, limit=1200)
    if candidates:
        return candidates[0] if not prefer_ends else candidates[0]

    # 見つからなければ従来挙動
    with db_connect() as con:
        cur = con.cursor()
        cur.execute(
            f"""
            SELECT {WORD_COL} FROM {TABLE_NAME}
            WHERE length({WORD_COL}) >= 4
              AND {WORD_COL} NOT LIKE '%ん'
            ORDER BY RANDOM()
            LIMIT 1200
            """
        )
        rows = [r[0] for r in cur.fetchall()]

    if not rows:
        return None

    if prefer_ends:
        pref = [w for w in rows if ends_with_any_pref(w, prefer_ends)]
        rest = [w for w in rows if w not in pref]
        rows = pref + rest

    # 均等ランダム（語尾）
    pick = pick_balanced_by_end(rows, used)
    if pick:
        return pick

    random.shuffle(rows)
    for w in rows:
        if w not in used and is_hiragana_str(w):
            return w
    return None


# ====== セッション管理 ======
def reset_game():
    session["messages"] = []
    session["used"] = []
    session["score"] = 0
    session["is_running"] = False
    session["is_endless"] = False  # 廃止だが互換のため保持
    session["ends_at"] = 0.0
    session["whose_turn"] = None
    session["target_len"] = None           # 5〜9 または "10以上"
    session["bonus_char"] = None
    session["prefer_ends"] = []
    session.modified = True


def get_used_set() -> set:
    return set(session.get("used", []))


def set_used_set(s: set):
    session["used"] = list(s)
    session.modified = True


def time_left_seconds() -> float:
    if not session.get("is_running"):
        return 0.0
    if session.get("is_endless"):
        return 9999999.0  # 互換のため残す（UI側では∞非表示）
    return max(0.0, session.get("ends_at", 0.0) - time.time())


def state_payload(error: str = None):
    return {
        "is_running": session.get("is_running", False),
        "is_endless": session.get("is_endless", False),
        "time_left": time_left_seconds(),
        "messages": session.get("messages", []),
        "score": session.get("score", 0),
        "target_len": session.get("target_len"),
        "bonus_char": session.get("bonus_char"),
        "whose_turn": session.get("whose_turn"),
        "prefer_ends": session.get("prefer_ends", []),
        "error": error,
    }


def game_over_state():
    return {
        "is_running": False,
        "is_endless": session.get("is_endless", False),
        "time_left": 0,
        "messages": session.get("messages", []),
        "score": session.get("score", 0),
        "target_len": None,
        "bonus_char": None,
        "whose_turn": None,
        "prefer_ends": session.get("prefer_ends", []),
        "error": None,
    }


# ====== ルーティング ======
@app.route("/")
def index():
    if "messages" not in session:
        reset_game()
    return render_template_string(get_page_html())


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json(force=True)
    reset_game()

    # エンドレス廃止：分モードのみ
    minutes = int(data.get("minutes", 3) or 3)
    if minutes not in (1, 3, 5):
        minutes = 3
    session["is_endless"] = False
    session["ends_at"] = time.time() + minutes * 60

    # 終端優先
    prefer_ends = sanitize_prefer_ends(data.get("prefer_ends", []))
    session["prefer_ends"] = prefer_ends

    session["is_running"] = True
    session["whose_turn"] = "system"

    used = get_used_set()
    opening = db_random_opening_word(used, prefer_ends)
    if opening is None:
        session["messages"].append({"side": "system", "text": "（開始できませんでした…単語DBを確認してください）"})
        return jsonify(game_over_state())

    used.add(opening)
    set_used_set(used)

    session["messages"].append({"side": "system", "text": opening})
    session["whose_turn"] = "user"
    session["target_len"] = new_user_target_len()  # ★ 5〜9 or 「10以上」
    session["bonus_char"] = new_bonus_char()
    session.modified = True
    return jsonify(state_payload())


@app.route("/state")
def state():
    return jsonify(state_payload())


def _length_diff_for_scoring(word_len: int, target) -> int:
    """スコア用の長さ差。
       ・target が「10以上」の場合：10未満なら (10 - len)、10以上なら 0
       ・target が数値の場合：従来どおりの絶対差
    """
    if isinstance(target, str) and target == TARGET_10PLUS_LABEL:
        return 0 if word_len >= 10 else (10 - word_len)
    try:
        t = int(target)
        return abs(word_len - t)
    except Exception:
        return 0


@app.route("/play", methods=["POST"])
def play():
    if not session.get("is_running"):
        return jsonify(game_over_state())
    if not session.get("is_endless") and time_left_seconds() <= 0:
        session["is_running"] = False
        return jsonify(game_over_state())

    data = request.get_json(force=True)
    raw = str(data.get("word", "")).strip()
    word = normalize_input(raw)

    if not word:
        return jsonify(state_payload("入力が空です。"))
    if not is_hiragana_str(word):
        return jsonify(state_payload("入力はひらがなのみでお願いします（※「ヴ」はカタカナでもOK）。"))
    if not valid_length(word):
        return jsonify(state_payload("2文字・3文字の単語は無効です。"))
    if ends_with_n(word):
        return jsonify(state_payload("末尾が「ん」の単語は無効です。"))

    used = get_used_set()
    msgs = session.get("messages", [])
    score = session.get("score", 0)
    target_len = session.get("target_len", None)
    bonus_char = session.get("bonus_char", None)
    turn = session.get("whose_turn", "user")

    if turn != "user":
        return jsonify(state_payload("まだシステムの番です。"))
    if word in used:
        return jsonify(state_payload("この試合では既に使われています。"))
    if not db_has_word(word):
        return jsonify(state_payload("単語DBに存在しません。"))

    # 前回システム語から開始文字チェック
    last_sys = next((m["text"] for m in reversed(msgs) if m["side"] == "system"), None)
    if last_sys:
        req = next_required_start(last_effective_char(last_sys))
        if word[0] != req:
            return jsonify(state_payload(f"開始文字が不正です。「{last_sys}」の次は「{req}」から始めてください。"))

    # 使用登録 & スコア
    used.add(word)
    set_used_set(used)
    msgs.append({"side": "user", "text": word})

    # スコア計算：±0=120, ±1=70, ±2=50（「10以上」は10以上で±0扱い）
    diff = _length_diff_for_scoring(len(word), target_len)
    base = 120 if diff == 0 else (70 if diff == 1 else (50 if diff == 2 else 0))
    if is_bonus_hit(word, bonus_char):
        base *= 2
    score += base
    session["score"] = score

    # システムの手（分布内で長さ選択）
    start_char = next_required_start(last_effective_char(word))
    prefer_ends = session.get("prefer_ends", [])
    system_word = db_random_starting_with(start_char, used, prefer_ends)

    if not system_word:
        msgs.append({"side": "system", "text": f"（「{start_char}」で始まる有効な単語が見つかりませんでした…）"})
        alt_open = db_random_opening_word(used, prefer_ends)
        if alt_open:
            used.add(alt_open)
            set_used_set(used)
            msgs.append({"side": "system", "text": alt_open})
            session["whose_turn"] = "user"
            session["target_len"] = new_user_target_len()  # ★ 次ターン指定
            session["bonus_char"] = new_bonus_char()
        else:
            session["is_running"] = False
            session["whose_turn"] = None
            session["target_len"] = None
            session["bonus_char"] = None
            session.modified = True
            return jsonify(state_payload("有効な単語が見つからず、ゲームを終了します。"))
    else:
        used.add(system_word)
        set_used_set(used)
        msgs.append({"side": "system", "text": system_word})
        session["whose_turn"] = "user"
        session["target_len"] = new_user_target_len()  # ★ 次ターン指定
        session["bonus_char"] = new_bonus_char()

    session["messages"] = msgs
    session.modified = True

    if not session.get("is_endless") and time_left_seconds() <= 0:
        session["is_running"] = False
        session["whose_turn"] = None
        session["target_len"] = None
        session["bonus_char"] = None
        session.modified = True
        return jsonify(game_over_state())

    return jsonify(state_payload())


if __name__ == "__main__":
    print("[DEBUG] BASE_DIR:", BASE_DIR)
    print("[DEBUG] DB_PATH:", DB_PATH)
    print("[DEBUG] DB_ZIP_PATH:", DB_ZIP_PATH)

    # 起動時にも念のためチェック
    ensure_db_exists()

    if not os.path.exists(DB_PATH):
        print(f"[!] DBが見つかりません: {DB_PATH}")
        print("    wordlist.db または wordlist.zip を同じフォルダに配置してください。")

     # Railway などの PaaS 用：PORT 環境変数を優先
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)