import os, sys, time
import re
import json
import glob

import utils


def load_json_files(json_files) :
	startime = time.time()

	corpus_raw_french = u""
	# corpus_raw_english = u""


if __name__ == "__main__":

	if len(sys.argv) < 2 :
		print(u"Please use # python beatstats.py settings.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])

		out_dir = settings.find('settings').find('output').text
		if not os.path.exists(out_dir+'/json'):
			print("Out dir {} not found".format(out_dir+'/json'))
			exit()

	# Load JSON raw and compute stats
	json_files = sorted(glob.glob(out_dir+'/json/*.json'))

	# Stats
	dates= []
	stats = {}

	nb_publis = 0
	for jfile in json_files:
		# print("Read {}".format(jfile))
		j = utils.utils.loadjson(jfile)
		for news in j :
			if news != "statistics" :
				for t in j[news] :
					nb_publis += 1

					service = t['service']
					if service not in stats :
						# print("New service {} detected ".format(service))
						stats[service] = {}

					datepubli = time.strftime('%d/%m/%Y', time.localtime(int(news)/1000))
					if datepubli not in stats[service] :
						stats[service][datepubli] = {}
						stats[service][datepubli]['nb'] = 1
					else :
						stats[service][datepubli]['nb'] += 1

					if datepubli not in dates :
						dates.append(datepubli)

					nb_words=len(t['text'].split())
					if 'nb_words' not in stats[service][datepubli] :
						stats[service][datepubli]['nb_words'] = nb_words
					else :
						stats[service][datepubli]['nb_words'] += nb_words

					similarity = t['similarity']
					if 'similarity' not in stats[service][datepubli] :
						stats[service][datepubli]['similarity'] = similarity
					else :
						stats[service][datepubli]['similarity'] += similarity

					if 'filtered' not in stats[service][datepubli] :
						if t['rate'] == '1' :
							stats[service][datepubli]['filtered'] = 1
					else :
						if t['rate'] == '1' :
							stats[service][datepubli]['filtered'] += 1

	print("{} souces analysed".format(len(stats)))
	print("{} news analysed".format(nb_publis))
	print("Writing file")


	# Nb posts
	header="source;"
	corpsline = {}

	for sname,svalue in stats.items() :
		corpsline[sname]=sname+';'

	outfile = open("statistics_nb.csv", "w")
	for d in dates :
		header += d + ';'
		for sname,svalue in stats.items() :
			if d in svalue :
				corpsline[sname] += str(svalue[d]['nb']) +';'
			else :
				corpsline[sname] += "0;"

	outfile.write("%s\n" % header)
	for it,line in corpsline.items() :
		outfile.write("%s\n" % line)

	outfile.close()

	# Nb filtered posts
	header="source;"
	corpsline = {}

	for sname,svalue in stats.items() :
		corpsline[sname]=sname+';'

	outfile = open("statistics_sim.csv", "w")
	for d in dates :
		header += d + ';'
		for sname,svalue in stats.items() :
			if d in svalue and 'similarity' in svalue[d] and  'nb' in svalue[d] :
				val = svalue[d]['similarity']/svalue[d]['nb']
				corpsline[sname] += str(val) +';'
			else :
				corpsline[sname] += "0;"

	outfile.write("%s\n" % header)
	for it,line in corpsline.items() :
		outfile.write("%s\n" % line)

	outfile.close()
