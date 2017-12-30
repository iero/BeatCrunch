class Statistics:

    def __init__(self, jsonfile):
        self.total = 0
        self.twitted = 0
        self.tooted = 0
        self.filtered = 0
        self.duplicates = 0
        self.nbwords = 0
        self.nbtags = 0

        if jsonfile :
            if 'statistics' in jsonfile :
                self.total=jsonfile['statistics']['total']
                self.twitted=jsonfile['statistics']['twitted']
                if hasattr(jsonfile['statistics'], 'tooted'):
                    self.tooted=jsonfile['statistics']['tooted']
                self.filtered=jsonfile['statistics']['filtered']
                self.duplicates=jsonfile['statistics']['duplicates']
                self.nbwords=jsonfile['statistics']['nbwords']
                self.nbtags=jsonfile['statistics']['nbtags']

        # Computed each time.. need to store ?
        self.top_trend=[]

    def printJson(self) :
        return {
        	'total': self.total,
        	'twitted': self.twitted,
        	'tooted': self.tooted,
        	'filtered': self.filtered,
        	'duplicates': self.duplicates,
        	'nbwords': self.nbwords,
        	'nbtags': self.nbtags,
        	'nbwords': self.nbwords,
        	'top_trend' : self.top_trend
        }

    def show(self) :
        print(u'+-[Statistics]')
        print(u'+-- {} articles today'.format(self.total))
        print(u'+-- {} tags'.format(self.nbtags))
        print(u'+-- {} words'.format(self.nbwords))
        print(u'+--- {} twitted'.format(self.twitted))
        print(u'+--- {} tooted'.format(self.tooted))
        print(u'+--- {} filtered'.format(self.filtered))
        print(u'+--- {} duplicates'.format(self.duplicates))

        tags = ' '.join(self.top_trend)
        print(u'+-- Trend [{}]'.format(tags.encode('utf8')))
        print(u'+-[/Statistics]')
