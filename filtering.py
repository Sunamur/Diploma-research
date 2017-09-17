import pandas as pd

lwr=lambda x: x.lower()

df=pd.read_csv("db.csv", sep="|")
len_start=len(df)
df["Name"]=df["Name"].map(lwr)
nms=df["Name"].tolist()
print("База готова к фильтровке")
# nms=[i for i in pd.read_csv("db.csv", sep="|")["Name"]]

D={}# key=name, value=count
for name in nms:
    if name in D:
        D[name]+=1
    else:
        D[name]=1
l={}#list of names by frequency
for i in D:
    if D[i] in l:
        l[D[i]].append(i)
    else:
        l[D[i]]=[i]
L={}#frequency of names
for i in D:
    if D[i] in L:
        L[D[i]]+=1
    else:
        L[D[i]]=1

def counter_of_hits(L, count):#scaffold, no runtime purpose
    q=0
    for i in L:
        if i>=count:
            q+=i*L[i]
    print("number of entries with freq above {}: {}".format(count, q))
    
filtered=[]
criteria=10
for i in l:
    if i>criteria:
        filtered+=l[i]

for count, elem in enumerate(filtered):
	print(count, elem)
trash=input("укажите через пробел номера нерелевантных позиций")
trash=sorted([int(i) for i in trash.split()])# list of indexes of trashy positions
log_trash=[]
for elem in trash:
	log_trash.append(filtered[elem])
	del filtered[elem]
	trash=[i-1 for i in trash]
print ("Были удалены: {}".format(log_trash))

#newfil=filtered[:7]+filtered[8:-1]#list with all the required names
dffilter=pd.DataFrame({"Name":filtered})
df_filtered=df.merge(dffilter, on="Name")
len_predup=len(df_filtered)
df_final=df_filtered.drop_duplicates(subset=["Reqs", "Resp"])
len_end=len(df_final)
df_final.to_csv("filtered.txt",sep="\t")#TESTING TSV
print("База сокращена в {} раз\nубрано {} позиций (из которых {} после исключения дубликатов)\nитоговая база содержит {} записей\nфайл сформирован".format(len_start/len_end, len_start-len_end, len_predup-len_end, len_end))
