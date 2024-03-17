with open("storage3_2020.06.list.txt","r") as f:
    lines = f.readlines()
    lines = [item.split("/", 1)[1].strip() if "/" in item else item for item in lines]
    new_line = []
    with open("storage2_2021.08.2.list.txt","r") as f2:
        plines = f2.readlines()
        plines = [item.split("/", 1)[1].strip() if "/" in item else item for item in plines]
    new_line = []
    print("2020.6 length = "+str(len(lines)))
    origin_set = set(plines)
    result = []
    for t in lines:
        if t in origin_set:
            pass
        else:
            result.append(t)
    print("result length = "+str(len(result)))
    with open("download_list.txt", "w") as fout:
        for item in result:
            fout.write(item + "\n")