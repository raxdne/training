#
# https://docs.python.org/3/library/glob.html
#
# (setq python-shell-interpreter "python3")

import glob

print("sep=	")

files = sorted(glob.glob('[0-9]*.tdv'))
for filename in files:
    print("* ",filename)
    with open(filename) as f:
        content = f.read().splitlines()
    f.close()

    for l in content:
        entry = l.split()
        #print(entry)
        if len(entry) < 4:
            print(l)
            continue
        date = entry[0].split(".")
        entry[0] = "{year}{month:02}{day:02}".format(year=date[2],month=int(date[1]),day=int(date[0]))
        if len(entry) > 4:
            remark = " ".join(entry[4:])
            del entry[4:]
            entry.append("\"{0}\"".format(remark))
        print("	".join(entry))

