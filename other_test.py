

bigassarray = open('bigassarray.txt', 'a')
bigassarray.write('[')
for it in range(152, 387):
    bigassarray.write(f'[{str(it)}],')
bigassarray.write(']')

bigassarray.close