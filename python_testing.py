## Sorting dictionaries
test_dict1 = {1: 'D', 3: 'C', 2: 'B', 4: 'E', 5: 'A'}
print(f"Original dictionary: {test_dict1}")
print(f"Sorted: {sorted(test_dict1)}")
print(f"Sorted by items: {sorted(test_dict1.items())}")
print(f"Sorted by values: {sorted(test_dict1.values())}")
print(test_dict1.get)
sorted_keys = sorted(test_dict1, key=test_dict1.get)
print(f"Keys of the dictionary entries sorted by value: {sorted_keys}")
sorted_dict_vals = {}
for key in sorted_keys:
    sorted_dict_vals[key] = test_dict1[key]
print(f"Dictionary sorted by values: {sorted_dict_vals}")


## Lists of dictionaries
print(f"Original dictionary: {test_dict1}")
print(f"list(dict) = list of keys: {list(test_dict1)}")
print(f"list(dict.values()) = list of values: {list(test_dict1.values())}")
print(f"list(dict.items()) = list of items (i.e. (key, value) pairs): {list(test_dict1.items())}")