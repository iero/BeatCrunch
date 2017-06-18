class Statistics:

    def __init__(self, jsonfile):
        if not jsonfile :
            self.total = 0
            self.twitted = 0
            self.filtered = 0
            self.duplicates = 0
            self.nbwords = 0
            self.nbtags = 0
        else :
            for s in jsonfile['statistics'] :
                self.total=s['total']
                self.twitted=s['twitted']
                self.filtered=s['filtered']
                self.duplicates=s['duplicates']
                self.nbwords=s['nbwords']
                self.nbtags=s['nbtags']

        self.top_trend=[]

    def printJson(self) :
        return {
        	'total': self.total,
        	'twitted': self.twitted,
        	'filtered': self.filtered,
        	'duplicates': self.duplicates,
        	'nbwords': self.nbwords,
        	'nbtags': self.nbtags,
        	'top_trend' : self.top_trend
        }
