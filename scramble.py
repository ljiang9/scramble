"""scramble —— 终端词语还原小游戏。

把打乱的字母拼回原词。每词 3 次机会，默认 5 轮，猜对得分。
纯标准库，离线运行。
"""

import argparse
import random
import sys

# 内置词库：约 100 个常见英文单词（5-8 字母，字母不全相同，保证能打乱）
WORDS = [
    "apple", "grape", "mango", "lemon", "peach", "melon", "berry", "cherry",
    "table", "chair", "house", "river", "mountain", "forest", "ocean", "desert",
    "piano", "guitar", "violin", "drums", "trumpet", "flute", "singer", "dance",
    "tiger", "eagle", "shark", "whale", "snake", "zebra", "panda", "koala",
    "bread", "cheese", "honey", "sugar", "spice", "pizza", "pasta", "salad",
    "cloud", "storm", "rain", "snow", "wind", "thunder", "sunny", "frost",
    "book", "pen", "paper", "school", "teacher", "student", "lesson", "exam",
    "happy", "brave", "clever", "gentle", "honest", "kind", "lucky", "proud",
    "bridge", "castle", "garden", "market", "museum", "palace", "street", "tower",
    "camera", "phone", "laptop", "keyboard", "mouse", "screen", "cable", "robot",
    "train", "plane", "ship", "car", "bike", "truck", "rocket", "subway",
    "doctor", "nurse", "hospital", "medicine", "health", "clinic", "patient",
    "smile", "laugh", "dream", "magic", "music", "story", "movie", "game",
    "green", "yellow", "purple", "orange", "silver", "golden", "bright", "dark",
    "quick", "slow", "early", "late", "young", "old", "rich", "poor",
]

MAX_TRIES = 3


def scramble_word(word, rng):
    """打乱单词字母顺序，保证结果与原词不同（尽力而为）。"""
    letters = list(word)
    for _ in range(20):
        rng.shuffle(letters)
        scrambled = "".join(letters)
        if scrambled != word:
            return scrambled
    return "".join(letters)  # 极端情况（如全同字母）直接返回


def is_permutation(a, b):
    """检查两个字符串是否为字母重排。"""
    return sorted(a) == sorted(b)


def pick_words(n, rng, fixed=None):
    """选出本局要玩的词。fixed 指定时只用固定词（测试/演示）。"""
    if fixed:
        return [fixed] * n
    pool = [w for w in WORDS if len(w) >= 4]
    return rng.sample(pool, min(n, len(pool)))


def play_round(word, rng, input_fn, output_fn, auto=False):
    """玩一轮。返回 True=猜中，False=失败，None=玩家中途退出(EOF)。"""
    scrambled = scramble_word(word, rng)
    output_fn(f"\n打乱后的词：{scrambled}  （{len(word)} 个字母）")
    attempt = 0
    while attempt < MAX_TRIES:
        if auto:
            guess = word
            output_fn(f"  第 {attempt + 1} 次：{guess}（自动作答）")
        else:
            try:
                guess = input_fn(
                    f"  第 {attempt + 1}/{MAX_TRIES} 次猜测：").strip().lower()
            except EOFError:
                output_fn("\n输入结束，游戏提前结束。")
                return None
        if not guess:
            output_fn("  输入为空，再试一次（不计次数）。")
            continue
        attempt += 1
        if guess == word:
            output_fn(f"  ✅ 猜对了！答案就是 {word}。")
            return True
        left = MAX_TRIES - attempt
        if left:
            output_fn(f"  ❌ 不对，还剩 {left} 次机会。")
        else:
            output_fn(f"  ❌ 机会用完了。答案是：{word}。")
    return False


def play_game(rounds=5, fixed_word=None, auto=False, seed=None,
             input_fn=None, output_fn=None):
    """主游戏循环。返回 (得分, 总轮数)。"""
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    input_fn = input_fn or input
    output_fn = output_fn or print
    words = pick_words(rounds, rng, fixed_word)
    score = 0
    played = 0
    output_fn(f"===== 词语还原（共 {len(words)} 轮，每词 {MAX_TRIES} 次机会）=====")
    for i, word in enumerate(words, 1):
        output_fn(f"\n—— 第 {i}/{len(words)} 轮 ——")
        result = play_round(word, rng, input_fn, output_fn, auto=auto)
        if result is None:  # EOF 提前退出
            break
        played += 1
        if result:
            score += 1
    output_fn(f"\n===== 游戏结束：{score}/{played} =====")
    if played:
        if score == played:
            output_fn("🎉 全对！词语大师！")
        elif score >= played * 0.6:
            output_fn("👍 不错，继续加油！")
        else:
            output_fn("💪 多练练，下次更好！")
    return score, played


def build_parser():
    p = argparse.ArgumentParser(
        prog="scramble",
        description="终端词语还原小游戏：把打乱的字母拼回原词。",
    )
    p.add_argument("--rounds", type=int, default=5, help="轮数（默认 5）")
    p.add_argument("--word", default=None, help="固定用词（测试/演示用）")
    p.add_argument("--auto", action="store_true", help="自动作答演示（验证用）")
    p.add_argument("--seed", type=int, default=None, help="随机种子（可复现）")
    p.add_argument("--version", action="version", version="scramble 0.1.0")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.rounds < 1:
        print("error: --rounds 至少为 1", file=sys.stderr)
        return 2
    if args.word and (not args.word.isalpha() or len(args.word) < 2):
        print("error: --word 必须是长度 ≥2 的字母词", file=sys.stderr)
        return 2
    score, played = play_game(rounds=args.rounds, fixed_word=args.word,
                              auto=args.auto, seed=args.seed)
    return 0 if score == played and played > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
