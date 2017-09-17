import pandas as pd
import random
import json
nay_count=0
"""
plan is the following:
1. create clean lists of reqs and resp (listing())
2. iterate on lists, creating groups
2.1 break in 2 parts - primary and other iteration
3. save the results in readable format
3.1 save them along the way?

"""


res=pd.read_csv("filtered.txt",sep="\t")
clean_lists={}

def listing(origin_col):
	theD={}
	tesDict={}
	tesList=[]
	for i in range(len(res)):
	    #templist=re.findall(r'[\w]+', res.loc[i]["Reqs"][1:-1], re.U)
	    templist=[e.replace("'", "").replace('"', "").replace(";", "").replace("[", "").replace("]", "").lower() for e in res.loc[i][origin_col][1:-1].split("', '")]
	    for e in templist:
	        if e in tesDict:
	            tesDict[e]+=1
	        else:
	            tesDict[e]=1
	for i in tesDict:
	    tesList.append([i, tesDict[i]])
	for i in tesList:
	    if len(i[0])<3:
	        tesList.remove(i)
	tesList.sort(key= lambda x:x[1], reverse=True)
	return tesList


def checker(base, i):
	for group in base:
		for one in base[group]:
			if i==one[0]:
				return True
	return False


def new_iterate(b, base={}, namespc=[]):
	leng=0
	ourset=set()
	for e in base:
		for k in base[e]:
			ourset.add(k[0])
	leng=len(ourset)

	print("we are now at {0} entries, that's {1:.2f}% of list.".format(leng, (leng/len(b))*100))
	for i in b:
		if leng%50==0:
			for moar in range(5):
				print("YAY, {} ENTRIES DONE".format(leng))
		if checker(base, i[0])==True:
			continue
		guess=None
		print("№{0}, {1:.2f}%".format(leng, (leng/len(b))*100))
		for count, elem in enumerate(namespc):
			print (count, elem)
		for n in namespc:
			if n in i[0]:
				guess=n
				decision=input("{}:{}?(\"да\" для подтверждения)".format(i[0], guess))
				break
		if guess==None:
			decision=input("{}:".format(i[0]))
		if decision.startswith("+"):
			decisions=decision[1:].split(" ")
			for dec in decisions:
				base[namespc[int(dec)]].append(i)
		else:		
			try:
				base[namespc[int(decision)]].append(i)
			except ValueError:
				if decision=="да":
					base[guess].append(i)
				elif decision in namespc:
					base[decision].append(i)
				else:
					base[decision]=[i]
					namespc.append(decision)
		leng+=1
	return base

def prim_iterate(b, nay_count):#list of entries and base to be updated. sublist is [name, count]
	
	chunks=[b["leftovers"][i*20:(i+1)*20] for i in range(int((len(b["leftovers"])/20)+1))]
	print("Сейчас будет происходить группирование списка. Форма ответа:\nномера элементов одной группы - через пробел\nназвание группы - после номеров и через нижнее подчеркивание (НЕ ПРОБЕЛ!)\nесли групп несколько - разделить их запятыми\nесли название не приходит в голову - пишем \"нет\"")
	for chunk in chunks:
		deduc=0
		for count, elem in enumerate(chunk):
			print (count, elem[0])
		inp=input("группируем!")
		inp1=[i1.split(" ") for i1 in inp.split(", ")]
		itemlist=[]
		for i_1 in inp1:#работа с одной группой
			items=[]
			for e in i_1[:-1]:#работа с номерами в рамках одной группы
				#items.append(chunk.pop(int(e)-deduc))
				items.append(chunk[int(e)])
				#deduc+=1
			if i_1[-1]=="нет":
				#b["base"]["group "+str(nay_count)]=items
				items.append("group "+str(nay_count))
				nay_count+=1
			else:
				items.append(i_1[-1])
#				if i_1[-1] in b["base"]:
#					b["base"][i_1[-1]]+=items
#				else:
#					b["base"][i_1[-1]]=items
			itemlist.append(items)
		for item in itemlist:
			if item[-1] in b["base"]:
				b["base"][item[-1]]+=item[:-1]
			else:
				b["base"][item[-1]]=item[:-1]
		for item in itemlist:
			for entry in item[:-1]:
				b["leftovers"].pop(b["leftovers"].index(entry))
	return b

def prim_iter_end(result, nay_count):#transforming leftovers to the base with nonames
	for entry in result["leftovers"]:
		result["base"]["group "+str(nay_count)]=entry
		nay_count+=1

	return result["base"]


def sec_iterate(dic, nay_count):
	print("сейчас будет происходить группирование списков\nчтобы свести несколько групп в одну, укажите их номер через пробел\nпоследней цифрой - номер группы, название которой лучше всего отражает суть, либо свое - словосочетанием ЧЕРЕЗ \"_\"\nотделяйте группирования запятой!")
	keys=[i[0] for i in [[i, dic[i]] for i in dic.keys().sort(key= lambda x:len(x[1]))]]#groups sorted by the number of entries - smallest
	chunks=[keys[i*10:(i+1)*10] for i in range(int((len(keys)/10)+1))]
	for chunk in chunks:
		deduc=0
		for count, elem in enumerate(chunk):#ten groups in work
			print("{}:{}\n   {}".format(count, elem, dic[elem]))
			inp=input("группируем!")
			
			inp1=[i1.split(" ") for i1 in inp.split(", ")]
			for l in inp1:#one to-be-combined group
				items=[]
				for e in l[:-1]:#работа с номерами в рамках одной группы
					items+=dic.pop(chunk[int(e)-deduc])
					deduc+=1
				try:
					origin=int(l[-1])
				except ValueError:
					origin=l[-1]
				dic[origin]=items
	return dic

def loader():
	base=json.loads(open("Reqs_filtered.json").read())
	namespc_raw=[[i, len(base[i])] for i in list(base.keys())]
	namespc_raw.sort(key= lambda x:x[1], reverse=True)
	namespc=[i[0] for i in namespc_raw]
	return[base, namespc]

def main(base={}, namespc=[]):
	try:
		cols=["Reqs"]
		for col in cols:
			filenm=col+"_filtered.json"
			result=new_iterate(listing(col), base, namespc)
			with open(filenm, "w") as out:
				json.dump(result, out, ensure_ascii=False)
	except:
		result=locals()["base"]
		with open(filenm, "w") as out:
			json.dump(result, out, ensure_ascii=False)

if __name__ == '__main__':
	if input("launch now? y/n ") =="y":
		if input("load lost progress? y/n")=="y":
			archiv=loader()
			print("archive loaded! {} groups located.".format(len(archiv[1])))
			main(archiv[0], archiv[1])

		else:
			print("fresh start!")
			main()


# def main():
# 	co="y"
# 	co2="y"
# 	result1={"leftovers":listing("Resp"), "base":{}}
# 	while co=="y":
# 		result1=prim_iterate(result1)
# 		co=input("{} rejects found, do we carry on? (y/n) ".format(len(result1["leftovers"])))
# 	result2=prim_iter_end(result1)
# 	while co2=="y":
# 		result2=sec_iterate()
# 		co2=input("{} rejects found, do we carry on? (y/n) ".format(len(result2["fail"])))
# 	with open("resp.json", "w") as out:
# 		json.dump(result2, out, ensure_ascii=False)


# def maint(test):
# 	global nay_count
# 	nay_count=0
# 	co="y"
# 	co2="y"
# 	result1={"leftovers":test, "base":{}}
# 	while co=="y":
# 		result1=prim_iterate(result1, nay_count)
# 		co=input("{} rejects found, do we carry on? (y/n) ".format(len(result1["leftovers"])))
# 	result2={prim_iter_end(result1, nay_count)}
# 	while co2=="y":
# 		result2=sec_iterate(result2, nay_count)
# 		co2=input("{} rejects found, do we carry on? (y/n) ".format(len(result2["fail"])))
# 	with open("resp.json", "w") as out:
# 		json.dump(result2, out, ensure_ascii=False)		



# print("len(list) is {}".format(len(tesList)))
# print("first 80 entries are\n{}".format(tesList[:80]))
# cnt=0
# for i in tesList[:400]:
#     cnt+=i[1]
# print (cnt)
# print (tesList[600:700])