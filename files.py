# Write three lines to a new file
with open("notes.txt", "w") as f:
    f.write("First note\n")
    f.write("Second note\n")
    f.write("Third note\n")

print("Wrote notes.txt — check your file explorer!")
# Now read the file we just wrote, line by line
print("\n--- Reading notes.txt ---")
with open("notes.txt", "r") as f:
    for line in f:
        print(line.strip())