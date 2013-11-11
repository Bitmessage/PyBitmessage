class hashtag(object):
	
    _instance = None
    class Singleton:
        def __init__(self):
			#define class variables here 
            self.string = ""
            self.dic = {}
            self.array = []
			
    def __init__(self):
        if hashtag._instance is None:
            # Create and remember instanc
			hashtag._instance = hashtag.Singleton()
        self._EventHandler_instance = hashtag._instance
		
    def __getattr__(self, aAttr):
        return getattr(self._instance, aAttr)

    def __setattr__(self, aAttr, aValue):
        return setattr(self._instance, aAttr, aValue)
    
    def update_array(self):
        for w in sorted(self.dic, key=self.dic.get, reverse=True):
            self.array.append(w)

    def extract (self,sentence):
        array = []
        pattern='#'
        count = 0
        for word in sentence.split(' '):
            for word2 in word.split('\\n'):
                if word2.startswith(pattern):
                    for word3 in word2.split('#'):
                        if(word3 != ''):
                            array.append('#'+word3.lower())
                            count+=1
        self.update_dic(array)
        return count
		#return array
		
    def update_dic (self, array):
        for item in array:
            if (self.dic.get(item)==None):
                self.dic[item]=1
            else:
                self.dic[item]=self.dic[item]+1
                
    def get_color(self, value , sum):
        x = value/float(sum)
        if(x==0.5):
            return 0xffff
        elif(x>0.5):
            return int(x * 255)
        else: 
            return int(255*x)+0xff00
