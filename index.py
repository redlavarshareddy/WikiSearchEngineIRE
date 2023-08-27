import xml
from nltk.corpus import stopwords
from datetime import datetime
import os
import pickle
import json
import re
from nltk import stem
from collections import Counter
from collections import defaultdict
import xml.sax as sax

LEN_INFOBOX  = len('{{infobox')
LEN_CATEGORY = len('[[category:')
LEN_EXTERNS  = len('==external links==')

TAG_RE = re.compile(r'<[^>]+>')
infoBoxRegex = re.compile(r'(\{\{infobox1`(.|\n)*?\}\}\n)(?:[^\|])')
categoryRegex = re.compile(r'\[\[category:.*\]\]\n')
externalsRegex = re.compile(r'==external links==\n(.|\n)*?\n\n')
reftagRegex =  re.compile(r'<ref(.|\n)*?</ref>')
refsRegex = re.compile(r'(==references==(.|\n)*?\n)(==|\{\{DEFAULTSORT)')
stop_words = set(stopwords.words('english'))
stemmer = stem.PorterStemmer()
MIN_STOP_LENGTH = 3
MAX_STOP_LENGTH = 15
alphabet_lis = 'abcdefghijklmnopqrstuvwxyz'

# punctuation='¡©!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~0123456789'
dert = [ele for ele in list(range(0,1_1141_111)) if ele not in list(range(97,123))]
remove_punctuation_map = dict((char, 32) for char in dert)

EACH_FILE_HAS = 30_000
stemmer_dict = {}

def remove_tags(text):
    return TAG_RE.sub('', text)
def word_tokenize(text):
    return text.split()

def remove_stopwords(content):
    cleaned_data = []
    for ele in content:
        if len(ele) <= MIN_STOP_LENGTH:
            continue
        if len(ele) >= MAX_STOP_LENGTH:
            continue
        elif ele not in stop_words:
            cleaned_data.append(ele)
    return cleaned_data

def stem_data(content):
    stems = []
    for word in content:
        if word in stemmer_dict:
            stems.append(stemmer_dict[word])
        else:
            new_stem = stemmer.stem(word)
            stemmer_dict[word] = new_stem
            stems.append(new_stem)
    return stems

def getSinglePageIndex(infoWords, categoryWords, externalWords, refsWords, titleWords, mainWords, __ID__):
    cnt_info = Counter(infoWords)
    cnt_cat  = Counter(categoryWords)
    cnt_ext  = Counter(externalWords)
    cnt_ref  = Counter(refsWords)
    cnt_title  = Counter(titleWords)
    cnt_main = Counter(mainWords)
    final_cnt = cnt_info + cnt_cat + cnt_ext + cnt_ref + cnt_title + cnt_main
    invertedPageIndex = {}
    for word,count in final_cnt.items():
        invertedPageIndex[word] = [count,0,0,0,0,0,0]
    for word, count in cnt_info.items():
        invertedPageIndex[word][1] = count
    for word, count in cnt_cat.items():
        invertedPageIndex[word][2] = count
    for word, count in cnt_ext.items():
        invertedPageIndex[word][3] = count
    for word, count in cnt_ref.items():
        invertedPageIndex[word][4] = count
    for word, count in cnt_title.items():
        invertedPageIndex[word][5] = count
    for word, count in cnt_main.items():
        invertedPageIndex[word][6] = count
    return invertedPageIndex

class WikiHandler(sax.ContentHandler):
    def __init__(self):
        self.inTitle = False
        self.inText = False
        self.inId = False
        self.title = ""
        self.id = ""
        self.count = 0
        self.text = ""
        self.ids = []
        self.fileId = 0
        self.file_counter = EACH_FILE_HAS
        self.isIndexed = 0
        self.encounteredId = False
        self.miniIndex = defaultdict(str)
        self.indexmap = []
        if not os.path.isdir('buggi_dir'):
            os.mkdir('buggi_dir')
        if not os.path.isdir('title_dir'):
            os.mkdir('title_dir')

    def startElement(self, name, attrs):
        if name == 'id' and self.encounteredId == False:
            self.inId = True
            self.id = ""
        if name == 'title':
            self.inTitle = True
            self.title = ""
        if name == 'text':
            self.inText = True
            self.text = ""

    def endElement(self, name):References
        if name == 'id' and self.encounteredId == False:
            self.inId = False
            self.id = int(self.id)
            self.encounteredId = True
        if name == 'title':
            self.inTitle = False
        if name == 'text':
            self.inText = False
        if name == 'page':
            self.encounteredId = False #After page is done, encountered id, can be removed
            self.id = int(self.id)
            self.content = self.text
            self.count +=1
            self.splitTextContent()
            self.id = ""
            self.title = ""
            self.text = ""
            pbar.update()

    def characters(self, content):
        if self.inId:
            self.id += content
        if self.inTitle:
            self.title += content
        if self.inText:
            self.text += content

    def splitTextContent(self):
        title = self.title.lower()
        origcontent = self.content.lower()
        Words1 = []
        Words2 = []
        Words3 = []
        Words4 = []
        minpos = len(origcontent)
        pos = origcontent.find('{{infobox')
        if pos != -1:
            content = origcontent[pos:]
            match = infoBoxRegex.search(content)
            if match is not None: #Found some content
                Text = match.group(1)
                Words1 = Text.replace('|','')
                Words1 = remove_tags(Words1[LEN_INFOBOX:-2])
                Words1 = word_tokenize(Words1.translate(remove_punctuation_map)) #TOKENIZATION
                Words1 = remove_stopwords(Words1) #STOPWORDREMOVAL
                Words1 = stem_data(Words1)
        #---------------------------
        pos = origcontent.find('[[category')
        if pos != -1:
            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = categoryRegex.findall(content)
            Words2 = []
            if match: #Found some content
                for singleCategory in match:
                    output = singleCategory
                    output = remove_tags(output[LEN_CATEGORY:-2])
                    output = word_tokenize(output.translate(remove_punctuation_map)) #TOKENIZATION
                    output = remove_stopwords(output) #STOPWORDREMOVAL
                    output = stem_data(output)
                    Words2 += output
                    Text = match
            #---------------------------
        pos = origcontent.find('==external')
        if pos != -1:

            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = externalsRegex.search(content)
            if match:
                content = origcontent[pos:]
                Text = match.group()
                Words3 = Text
                Words3 = word_tokenize(Words3[LEN_EXTERNS:].translate(remove_punctuation_map)) #TOKENIZATION
                Words3 = remove_stopwords(Words3) #STOPWORDREMOVAL
                Words3 = stem_data(Words3)
            #---------------------------
        pos = origcontent.find('==references==')
        if pos != -1:
            minpos = min(minpos,pos)
            content = origcontent[pos:]
            match = refsRegex.search(content)
            if match:
                minpos = min(minpos,pos)
                Text = match.group(1)
                Words4 = Text
                Words4 = word_tokenize(Words4.translate(remove_punctuation_map)) #TOKENIZATION
                Words4 = remove_stopwords(Words4) #STOPWORDREMOVAL
                Words4 = stem_data(Words4)
            #---------------------------
        if title is not None: #Found some content
            titleWords = word_tokenize(title.translate(remove_punctuation_map)) #TOKENIZATION
            titleWords = [ele for ele in titleWords if len(ele) > 2]
            titleWords = stem_data(titleWords)
        else:
            titleWords = []
            #---------------------------
        content = origcontent[:minpos]
        if content:
            content = re.sub(reftagRegex,'',content)
            content = word_tokenize(content.translate(remove_punctuation_map)) #TOKENIZATION
            content = remove_stopwords(content) #STOPWORDREMOVAL
            content = stem_data(content)
        else:
            content = []
        cnt_info = Counter(Words1)
        cnt_cat  = Counter(Words2)
        cnt_ext  = Counter(Words3)
        cnt_ref  = Counter(Words4)
        cnt_title  = Counter(titleWords)
        cnt_main = Counter(content)
        all_tokens = set(cnt_main.keys())
        all_tokens = all_tokens.union(cnt_info.keys(),cnt_cat.keys(), cnt_ext.keys(), cnt_ref.keys() , cnt_title.keys() , cnt_main.keys())
        all_tokens_arr = list(all_tokens)
        all_tokens_arr.sort()
        for word in all_tokens_arr:
            string = ""
            string += str(self.count)
            if word in cnt_main:
                string+= 'b'+str(cnt_main.get(word))
            if word in cnt_title:
                string+= 't'+str(cnt_title.get(word))
            if word in cnt_info:
                string+= 'i'+str(cnt_info.get(word))
            if word in cnt_ref:
                string+= 'r'+str(cnt_ref.get(word))
            if word in cnt_ext:
                string+= 'x'+str(cnt_ext.get(word))
            if word in cnt_cat:
                string+= 'c'+str(cnt_cat.get(word))
            string+='|' #EOF  of info for this word, for this file
            self.miniIndex[word] += string
        clean_title = ''.join([i if ord(i) < 128 else ' ' for i in self.title])
        self.indexmap.append(str(self.count)+':'+clean_title+'\n')
        self.file_counter-=1

        if self.file_counter == 0:
#             self.makeGoodIndex()
            print(self.count)
            print('Starting')
            self.file_counter = EACH_FILE_HAS
            with open('buggi_dir/'+str(self.fileId),'w+') as f:
                for key in sorted(self.miniIndex.keys()) :
                    f.write(key+':'+self.miniIndex[key]+'\n')
            self.miniIndex = defaultdict(str)


            with open("title_dir/"+'title_file',"a+") as f:
                f.writelines(self.indexmap)

            self.indexmap = []
            self.fileId+=1

    def startDocument(self):
        pass
#         if not os.path.isdir('alphabet_dir'):
#             o

s.mkdir('alphabet_dir')
#         for i in alphabet_lis:
#             open('alphabet_dir/'+i,'w+').close()

    def endDocument(self):
        print('End-----')
        if self.file_counter != EACH_FILE_HAS:
#             self.makeGoodIndex() #Make Index to the last file
#             with open("buggi_dir/"+str(self.fileId),"wb") as f:
#                 pickle.dump(dict(self.miniIndex),f)
            with open('buggi_dir/'+str(self.fileId),'w+') as f:
                for key in sorted(self.miniIndex.keys()) :
                    f.write(key+':'+self.miniIndex[key]+'\n')
            self.miniIndex = defaultdict(str)

            with open("title_dir/"+'title_file',"a+") as f:
                f.writelines(self.indexmap)
            self.indexmap = []
        print(self.count)

    def makeGoodIndex(self):
        alpha_file = '-'
        dict_ = self.miniIndex
        for key in sorted(dict_):
            if key[0] != alpha_file:
#                 if key[0] == '':
#                     print(key, dict_[key])
                old_alpha = alpha_file
                alpha_file = key[0]
                if old_alpha != '-':
                    file.close()
                    tmp.close()
                    os.rename('alphabet_dir/tmp','alphabet_dir/'+old_alpha)
                file = open('alphabet_dir/'+alpha_file,'r')
                tmp  = open('alphabet_dir/tmp','w')
            #Changed the file, so that, you can add to the apt file
            line = file.readline()
            #Start the loop to copy lines
            done_flag = False
            while line != '' and done_flag == False:
                try:
                    word,sentence = line.split(':',1)
                except:
                    print(line)
                #Got the line from file
                if word < key: #Key is not in the right spot
                    tmp.write(line)
                    line = file.readline()
                elif word == key:
                    tmp.write(line[:-1]+dict_[key]+'\n')
                    done_flag = True
                elif word > key:
                    #Just reached the spot where, key has crossed
                
/IRE/Submission/
Name
Last Modified

    tmp.write(key+':'+dict_[key]+'\n')
                    tmp.seek(file.tell()-len(line))
                    done_flag = True
            if line == '': #Reached Eof and the word is not there obvi
                tmp.write(key+':'+dict_[key]+'\n')
        try:
            if alpha_file != '-':
                file.close()
                tmp.close()
                os.rename('alphabet_dir/tmp','alphabet_dir/'+alpha_file)
        except:
            pass


parser = xml.sax.make_parser()
handler = WikiHandler()
hellp = parser.setContentHandler(handler)
now = datetime.now()
path = input('Path:')
parser.parse(path)
diff = datetime.now() - now
print(diff.total_seconds())