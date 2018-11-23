def GetDict(a):
    #Create Seeion as dictionary
    name = []
    mid = []
    i=0
    while(i<len(a)):
        name.append(a[i])
        i=i+1
        mid.append(a[i])
        i=i+1
    namedict = dict(zip(name,mid))
    print namedict
    return namedict
