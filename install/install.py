

#BOOTSTRAP CODE
handle = urlopen(url)
with open(to, 'wb') as out:
    while True:
        data = handle.read(1024)
        if len(data) == 0: break
        out.write(data)
handle.close()
out.close()


print do.getTmpPath("test")