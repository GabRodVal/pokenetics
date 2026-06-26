
ex_arr = []


for f in range(200,0,-1):
    ex_arr.append(f)

print(len(ex_arr))
print(sum(ex_arr))
tot=sum(ex_arr)

for it in range(len(ex_arr)):
    print(f'{ex_arr[it]}-{(ex_arr[it]/tot)*100}%')