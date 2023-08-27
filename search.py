import pickle
from datetime import datetime
import re
import os
from collections import defaultdict
from math import log10 as logt

MIN_STOP_LENGTH = 2
MAX_STOP_LENGTH = 15
from nltk.corpus import stopwords

from nltk import stem
stop_words = set(stopwords.words('english')) 
stemmer = stem.PorterStemmer() 
global_phrase_dict = {}
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

def FileBinarySearch(query):
    file_name = 'buggi_dir/index_shortened' 
    with open(file_name,'r') as f:
        size = os.fstat(f.fileno()).st_size
        lo=0
        hi=size
        if hi == 0:
            return False
        line = f.readline() #Read first line
        word, sent = line.split(':',1)
        if word == query:
            return word, sent
        while lo < hi:
            loc = int((hi+lo)/2)
            f.seek(loc)
            line = f.readline()
            if line == "":
                r = size
                continue
            line = f.readline()
            row = line.split(':',1)
            if query == row[0]:
                retReferencesurn row
            elif query < row[0]:
                hi=loc-1
            else:
                # Split into higher half
                lo=loc+1
        # If not found
    return False

def TitleBinarySearch(num_):
    file_name = 'title_dir/title_file'
    with open(file_name,'r') as f:
        size = os.fstat(f.fileno()).st_size
        hi = size
        lo=0
        if hi == 0:
            return False
        line = f.readline() #Read first line
        line_no, title = line.split(':',1)
        if num_ == 1:
            return title
        while lo < hi:
            loc = int((hi+lo)/2)
            f.seek(loc)
            line = f.readline()
            if line == "":
                r = size
                continue
            line = f.readline()
            row = line.split(':',1)
            if num_ == int(row[0]):
                return row[1]
            elif num_ < int(row[0]) :
                hi=loc-1
                continue
            else:
                # Split into higher half
                lo=loc+1
                continue
            return row  # Found
        # If not found
    return False

import itertools 
def getNum(strim):
    file = ''
    for i in strim:
        if i.isdigit():
            file+=i
        else:
            break
    return file, strim[len(file):]

def getCount(char,strim):
    if char in strim:
        num = ''
        pos = strim.find(char)
        for i in strim[pos+1:]:
            if i.isdigit():
                num+=i 
            else:
                break
        return int(num)
    else:
        return 0

def str_to_dict(query):
    dict_ = defaultdict(float)
    query_list = query.split('|')[:-1]
    num_docs = len(query_list)
    for ele in query_list:
        splite = getNum(ele)
        sum_ = sum([getCount(char, splite[1]) for char in 'btirxc'])
        dict_[int(splite[0])] = (1+logt(sum_))*(15-logt(num_docs))
    return dict_

def NormalSearch(query):
    query = query.strip()
    splitted_words = query.lower().split(' ')
    splitted_words = remove_stopwords(splitted_words)
    main_strim = defaultdict(float)
    dict_array = []
    dict_set = set()
    for ele in splitted_words:
        if ele not in global_phrase_dict:
            output = FileBinarySearch(ele) 
            global_phrase_dict[ele] = output
        else:
            output = global_phrase_dict[ele]
            
        if output != False: #Check if data has some files
            strim = str_to_dict(output[1])
            dict_array.append(strim)
        else:
            dict_array.append(defaultdict(float))
    for dict_ in dict_array:
        dict_set = dict_set.union(dict_.keys())
    for key in dict_set:
        main_strim[key] = sum([dict_[key] for dict_ in dict_array])
    sorted_dict = sorted(main_strim.items(), key=lambda x: -x[1])
    output = []
    for ele in sorted_dict:
        title = TitleBinarySearch(ele[0])
        if title == False:
            continue
        output.append(title)
        if(len(output)) > 10:
            output = output[:10]
    return output #All the valid files

def getfieldPieces(query):
    pieces = []
    query = query.strip()#Remove /n
    while ':' in query:
        query_str = query.rsplit(':',1)[1] #Query str has 
        query = query.rsplit(':',1)[0]
        if ' ' not in query: #Reached the last word 
            loc = query
            query = ''
        else:
            loc = query.rsplit(' ',1)[1]
            query = query.rsplit(' ',1)[0]
        pieces.append([loc.strip(), query_str.strip()])
    return pieces

field_map = {'title':'t',
             'body':'b',
             'infobox':'i',
             'ref':'r',
             'category':'c',
             'external':'x'
            }
def getNum(strim):
    file = ''
    for i in strim:
        if i.isdigit():
            file+=i
        else:
            break
    return file, strim[len(file):]

def getCount(char,strim):
    if char in strim:
        num = ''
        pos = strim.find(char)
        for i in strim[pos+1:]:
            if i.isdigit():
                num+=i 
            else:
                break
        return int(num)
    else:
        return 0
    
def str_to_dict_with_field(query, letter):
    dict_ = defaultdict(float)
    query_list = query.split('|')[:-1]
    num_docs = len(query_list)
    for ele in query_list:
        count = getCount(letter,ele)  
        if count != 0:
            splite = getNum(ele)
            dict_[int(splite[0])] = (1+logt(count))*(15-logt(num_docs))
    return dict_

def FieldSearch(queryList):
    lofields = getfieldPieces(queryList)
    main_strim = defaultdict(float)
    output = []
    flag = False
    dict_array = []
    dict_set = set()
    
    for ele in lofields:
        field_char = field_map[ele[0]]
        query = ele[1]
        splitted_words = query.lower().split(' ')
        splitted_words = remove_stopwords(splitted_words)
        for jele in splitted_words:
            if jele not in global_phrase_dict:
                output = FileBinarySearch(jele) 
                global_phrase_dict[jele] = output
            else:
                output = global_phrase_dict[jele]
            res = FileBinarySearch(jele)
            if res != False: #Check if data has some files
                strim = str_to_dict_with_field(res[1],field_char)
                dict_array.append(strim)
            else:
                dict_array.append(defaultdict(float))
    for dict_ in dict_array:
        dict_set = dict_set.union(dict_.keys())
    for key in dict_set:
        main_strim[key] = sum([dict_[key] for dict_ in dict_array])

        sorted_dict = sorted(main_strim.items(), key=lambda x: -x[1])
    output = []
    
    for ele in sorted_dict:
        title = TitleBinarySearch(ele[0])
        if title == False:
            continue
        output.append(title)
        if(len(output)) > 10:
            output = output[:10]
    return output #All the valid files

# with open('sampleQueriesAndResults/queryfile','r') as f:
#     listofqueries = f.readlines()
#         output = []
while True:
    query = input()
    if query == '!':
        break
    output = []
    now = datetime.now()
    if ':' in query:
        output = FieldSearch(query)
    else:
        output = NormalSearch(query)
    diff = datetime.now() - now
    for ele in output:
        print(ele.strip())
    print(diff.total_seconds())
    
#     for ele in output:
#     print(ele)
