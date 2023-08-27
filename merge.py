import heapq

class Merger():
    def __init__(self):
        try:
            #1. create priority queue
            self._heap = []
            self.batch_size = 700
            self.out_file_path = ''
            self._output_file = ''
        except Exception as err_msg:
            print("Error while creating Merger",err_msg)

    def tuplify(self,file):
        line = file.readline()
        if line != '':
            word = line.split(':',1)[0]
            return(word, line, file)
        return ('','',file)

    def merge(self, input_files):
        if True:
            open_files = []
            [open_files.append(open(file__, 'r')) for file__ in input_files]
            # enqueue the pair (key,sent,f) using the first value as priority key
            for file__ in open_files:
                heapq.heappush(self._heap,self.tuplify(file__))
            # 3. While queue not empty
            # dequeue head of queue
            # output m
            # if f not depleted
            # enqueue (nextNumberIn(f), f)
            while(self._heap):
                # get the smallest key
                smallest = heapq.heappop(self._heap)
                # write to output file
                self._output_file.write(smallest[1])
                # read next line from current file
                tuple__ = self.tuplify(smallest[2])
                # check that this file has not ended
                if(len(tuple__[1]) != 0):
                    # add next element from current file
                    heapq.heappush(self._heap, tuple__)
            # clean up
            [file__.close() for file__ in open_files]
            self._output_file.close()

#         except Exception as err_msg:
#             print("Error while merging:", err_msg)

    def mergeProperly(self,path):
        list_of_files = [f for f in os.listdir(path) if not f.startswith('.')]
        self.filep = len(list_of_files) #Get list of files
        print(self.filep)
        while(len(list_of_files)) > 1:
            len_ = len(list_of_files)
            size = len_ if len_ <= self.batch_size else self.batch_size
            self._output_file = open(os.path.join(path+str(self.filep)),'w+')
            self.merge([os.path.join(path,ele) for ele in list_of_files[:size]])
            for tobedelted in list_of_files[:size]:
                fp = os.path.join(path,tobedelted)
                os.remove(fp)
            self.filep += 1
            list_of_files = [f for f in os.listdir(path) if not f.startswith('.')]
        for file_ in list_of_files:
            os.rename(os.path.join(path,file_),os.path.join(path,'index'))

    def compressFile(self, path,remove_index=True):
        out_file = open(os.path.join(path,'index_shortened'),'w+')
        with open(os.path.join(path,'index'),'r') as f:
            line = f.readline()
            if line == '':
                return
            prev_word = line.split(':',1)[0]
            out_file.write(line[:-1]) #Write the first line
            line = f.readline()
            while line != '':
                word,sent = line.split(':',1)
                if word == prev_word:
                    out_file.write(sent[:-1])
                else:
                    out_file.write('\n'+line[:-1])
                    prev_word = word
                line = f.readline()
        out_file.close()
        fp = os.path.join(path,'index')
        if remove_index == True:
            os.remove(fp)

def test(path):
    merger = Merger()
    merger.mergeProperly(path)
    merger.compressFile(path)

test_folder = input('Test Folder Path ->')
test(test_folder)
