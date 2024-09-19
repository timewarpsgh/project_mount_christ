# Sample dictionary
my_dict = {'apple': 3, 'banana': 1, 'cherry': 2}

# Sort the dictionary by its values
sorted_dict = dict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))

print(sorted_dict)