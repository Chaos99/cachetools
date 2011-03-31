''' HTML Parser for badge definitions'''
from HTMLParser import HTMLParser

class BadgeParser(HTMLParser):
    ''' Parse the badge description page from the kyle mills website.

    Retrieve information about badge names, requirements and icon paths
    '''

    def __init__(self):
        ''' Preset html signatures and init result lists.'''
        HTMLParser.__init__(self)
        self.stack = []
        self.entity = None
        self.sigs = dict(
                     name = ['html', 'body', 'table', 'tr', 'td', 'table',
                             'tr', 'td', 'table', 'tbody', 'tr', 'td', 'b'],
                     desc = ['html', 'body', 'table', 'tr', 'td', 'table',
                             'tr', 'td', 'table', 'tbody', 'tr', 'td'],
                     icon = ['html', 'body', 'table', 'tr', 'td', 'table',
                             'tr', 'td', 'table', 'tbody', 'tr', 'td'],
                     icon2 = ['html', 'body', 'table', 'tr', 'td', 'table',
                              'tr', 'td', 'table', 'tbody', 'tr', 'td', 'p'],
                     level = ['html', 'body', 'table', 'tr', 'td', 'table',
                              'tr', 'td', 'table', 'tbody', 'tr', 'td',
                              'img', 'br'],
                     level2 = ['html', 'body', 'table', 'tr', 'td', 'table',
                               'tr', 'td', 'table', 'tbody', 'tr', 'td',
                               'p', 'img', 'br']
                    )
        self.names = []
        self.descs = []
        self.icons = []
        self.paths = []
        self.limits = []

    def handle_entityref(self, name):
        ''' Unescape HTML entities like &amp; '''
        self.entity = self.unescape('&'+name+';')

    def handle_starttag(self, name, attrs):
        ''' Handle stack; Recognize icon path signature.'''
        self.stack.append(name)
        if((self.sigs['icon'] == self.stack[:-1] or
           self.sigs['icon2'] == self.stack[:-1] ) and
           name == 'img' and
           (len(self.icons) + 1) == len(self.names)):
            src = attrs[2][1]
            path, icon = src.rpartition('/')[0:3:2]
            if '.png' in icon or '.jpg' in icon:
                self.icons.append(icon[:-5])
            else:
                self.icons.append(icon)
            self.paths.append(path+'/')
      
    def handle_endtag(self, name):
        ''' Handle stack; recognize EOF.'''
        self.entity = None
        if name == 'html':
            self.finish_()
        while self.stack.pop() != name:
            pass

    def handle_data(self, data):
        ''' Recognize name, description and levels.'''
        # get the name
        if self.sigs['name'] == self.stack:
            if self.entity:
                self.names.append(self.names.pop() + self.entity + data)
                self. entity = None
            else:
                self.names.append(data)            
                self.limits.append([])
        # get the description   
        if self.sigs['desc'] == self.stack:
            if self.entity and self.stack != []:
                self.descs.append(self.descs.pop() + self.entity + data)
            elif data.strip(' ()').startswith('award'):
                self.descs.append(data)
        #get the levels      
        if(self.stack == self.sigs['level'] or
           self.stack == self.sigs['level2']):
            limit = data.strip().partition('(' if '(' in data else '[')[2][:-1]
            if limit.count('-') == 1 and limit.strip(' -+').count('-')== 1:
                #only one - and not as polarity sign
                self.limits[-1].append(limit.partition('-')[0].strip(' km'))
                #print self.limits[-1]
            elif limit.count('-') == 1 and limit.strip(' -+').count('-')== 0:
                #only one negative number
                self.limits[-1].append(limit.strip(' +km'))            
                #print self.limits[-1]
            elif limit.count('-') == 0 and limit.count(',') == 0:
                # just a single positive number
                self.limits[-1].append(limit.strip(' +km'))
                #print self.limits[-1]
            elif limit.count('-') == 3: # two negative numbers
                self.limits[-1].append('-' +
                                       limit[1:].partition('-')[0].strip(' km'))
                #print self.limits[-1]
            elif limit.count(',') == 1: #new limit notation
                self.limits[-1].append(limit.partition(',')[0].strip(' km'))
            else:
                print limit

    def finish_(self):
        ''' Clean up strings to be returned.'''
        self.names = [a.strip() for a in self.names]
        self.descs = [a.strip(' ()') for a in self.descs]
