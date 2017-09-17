import requests
import json
import bs4
import pandas as pd
import codecs
import os.path



def read_positions():#reads required positions from file
	positions=[]
	fini=codecs.open('positions.txt', encoding='utf-8')
	fin=fini.readlines()
	for res in fin:
		positions.append(res.strip().lower())
	return positions

def search_by_keyword(kw):#gets key word, returns all relevant vacancies
	url="https://api.hh.ru/vacancies"
	resps=[]
	codes=[]
	print("Ищем {}, пристегните ремни.".format(kw))
	for pg in range(10):
		r=requests.get(url, params={
			'text':"'"+kw+"'"+" AND ((Высшее OR образование) AND (психология OR психологическое))",
			'per_page': 199,
			'page':pg
			})
		if r.status_code!=200:
			print ("error! code - {}".format(r.status_code))
			print (r.text)
		js = json.loads(r.text)
		for i in range(len(js["items"])):
			urlcode=js["items"][i]["url"]
			code=urlcode[urlcode.find("cies")+5:urlcode.find("?")]
			codes.append(int(code))
	print("Keyword search done!({})".format(len(codes)))
	return codes

def html_reader(text, name): #gets raw html string of description, returns nested lists of topics
	html=bs4.BeautifulSoup(text, "lxml")
	lists=html.findAll("ul")
	if len(lists)<2:
		print ("invalid data in {}".format(name))
		return[[], []]
	else:
		resp_raw=lists[0].findAll("li")
		resp=[]
		for i in range(len(resp_raw)):
			try:
				resp.append(resp_raw[i].contents[0].strip(",."))
			except Exception as e:
				print("{} in {}".format(e, name))
				continue	
		reqs_raw=lists[1].findAll("li")
		reqs=[]
		for i in range(len(reqs_raw)):
			try:
				reqs.append(reqs_raw[i].contents[0].strip(",."))
			except Exception as e:
				print("{} in {}".format(e, name))
				continue
		return [resp, reqs]


def indiv_search(code):#gets data on vacancy with given code
	url="https://api.hh.ru/vacancies/"
	r=requests.get(url+str(int(code)))
	if r.status_code!=200:
		print ("error! code - {}".format(r.status_code))
		print (r.text)
	js = json.loads(r.text)
	key_skills=[]
	if js["key_skills"]==[]:
		pass
	else:
		for a in js["key_skills"]:
			key_skills.append(a["name"])
	name=js["name"]
	desc=html_reader(js["description"], name+"/"+str(code))
	return [code, name, desc[0], desc[1], key_skills]

def codes_loader():
	try:
		return {int(i) for i in set(pd.read_csv("db.csv", sep="|")["Code"])}
	except FileNotFoundError:
		return set()

def iterator(new_codes):
	working_codes=set(new_codes).difference(codes_loader())
	print("{} entries have been found, {} are redundant; {} entries are in work now".format(len(new_codes), len(new_codes)-len(working_codes), len(working_codes)))
	working_frame=[]
	for c in working_codes:
		working_frame.append(indiv_search(c))
	return pd.DataFrame({
		"Code":[i[0] for i in working_frame],
		"Name":[i[1] for i in working_frame],
		"Resp":[i[2] for i in working_frame],
		"Reqs":[i[3] for i in working_frame],
		"KeyS":[i[4] for i in working_frame]
		}).set_index("Code")
	

def main():
	found_codes=[]
	for kw in read_positions():
		found_codes.extend(search_by_keyword(kw))
	print("Codes fetched, beginning the parse now.")	
	news=iterator(found_codes)
	if os.path.isfile("db.csv")==True:
		news.to_csv("db.csv", mode="a", header=False, sep="|")
	else:
		news.to_csv("db.csv", mode="w", sep="|")
	print("All done! {} entries added".format(len(news)))


if __name__ == "__main__":
	main()
