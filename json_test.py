import json

# A Python dict — structured data about Mint
mint = {
    "name": "Mint",
    "species": "Indian Ringneck Parrot",
    "age_months": 6,
    "favourite_foods": ["seeds", "fruit", "veggies"],
    "tricks_known": ["step up", "wave"]
}

# Write the dict to a JSON file
with open("mint.json", "w") as f:
    json.dump(mint, f, indent=2)

print("Saved mint.json — open it!")

# Now read it back into a Python dict
with open("mint.json", "r") as f:
    loaded = json.load(f)

print("\nLoaded from file:")
print(loaded)
print(f"\nFavourite foods: {loaded['favourite_foods']}")
print(f"Mint knows {len(loaded['tricks_known'])} tricks")