from CoreV2 import AppCore

a = AppCore.AppCore()

result = a.find_keys_by_value({'a': 1, 'b': {'b1': 2, 'b2': 1}, 'c': 1, 'd': {'dd1' : 1, 'dd2': {'ddd1' : 1}}}, 1, "eq", True)
print(result.data) 