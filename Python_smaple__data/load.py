import numpy as np

print("Load and print the numpy file")
load_py = np.load('D:/UnrealData/apartment_room_all.npy')

# print(load_py.len())
# print(load_py.shape)
# print(load_py[1][0][0][0][100])

flattened_array = load_py[13, :, :, :, 0].reshape(-1)[:500]
formatted_string = ",".join(map(str, flattened_array))

print(formatted_string )
print(len(formatted_string) )