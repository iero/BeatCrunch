# -*-coding:utf-8 -*
import sys

import utils

if __name__ == "__main__":

	if len(sys.argv) < 3 :
		print(u"Please use # python file.py settings.xml services.xml")
		sys.exit(1)
	else :
		settings = utils.utils.loadxml(sys.argv[1])
		services = utils.utils.loadxml(sys.argv[2])

	# Get Services list
	sList_global = {}

	sList_selected = []
	sList_ok = []
	sList_missing = []
	sList_notavailable = []

	# Get whole list
	for s in settings.findall('service'):
		sList_global[s.find('id').text] = s.get('name')

	# Get new articles for each selected service
	for s in services.find('settings').find("services").findall('service'):
		sList_selected.append(s.text)

		if s.text in sList_global :
			sList_ok.append(s.text)
		else :
			sList_notavailable.append(s.text)

	# Check if all services are selected
	for s in sList_global :
		if s not in sList_selected :
			sList_missing.append(sList_global[s])

	print("[{}] services available".format(len(sList_global)))
	print("[{}] in use".format(len(sList_ok)))

	print("[{}] not in use : ".format(len(sList_missing)))
	for s in sList_missing :
		print(" - {}".format(s))

	print("[{}] not available anymore : ".format(len(sList_notavailable)))
	for s in sList_notavailable :
		print(" - {}".format(s))
