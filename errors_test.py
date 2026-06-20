# === Old way vs comprehension ===

# Old way — 3 lines
squares_old = []
for x in range(1, 6):
    squares_old.append(x ** 2)
print("Old way:", squares_old)

# Comprehension — 1 line, same result
squares_new = [x ** 2 for x in range(1, 6)]
print("Comprehension:", squares_new)

print()  # blank line

# === 5 exercises ===

# 1. Cubes of 1 to 10
cubes = [x ** 3 for x in range(1, 11)]
print("1. Cubes:", cubes)

# 2. Even numbers from 0 to 20 — the 'if' filters the input
evens = [x for x in range(21) if x % 2 == 0]
print("2. Evens:", evens)

# 3. Uppercase a list of words
words = ["mint", "basil", "claude", "jarvis"]
upper = [w.upper() for w in words]
print("3. Upper:", upper)

# 4. Dict comprehension — name → length of name
names = ["Mint", "Basil", "Jarvis"]
name_lengths = {name: len(name) for name in names}
print("4. Lengths:", name_lengths)

# 5. Conditional expression inside a comprehension
nums = [-5, 3, -1, 8, 0]
labels = ["positive" if n > 0 else "non-positive" for n in nums]
print("5. Labels:", labels)