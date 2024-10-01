option_2_callback = {
    'b': 1,
    'a': 2,
}

# sort by key
option_2_callback = dict(sorted(option_2_callback.items(), key=lambda x: x[0]))

print(option_2_callback)