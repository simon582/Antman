with open('20160131.csv') as csv_file:
    for line in csv_file.readlines():
        print line.strip()
