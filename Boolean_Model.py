
from re import A
import re
from tempfile import tempdir
import os
from tkinter import messagebox
from turtle import pos
# from nbformat import write
# from pyrsistent import b
import nltk
# nltk.download('punkt')
from nltk.tokenize import word_tokenize
import string
from nltk.stem import PorterStemmer
Pstem=PorterStemmer()
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
root=tk.Tk()
root.withdraw()

#Creating inverted index for processing boolean queries
def Inv_ind():
    global DIR 
    DIR = 'Abstracts/'
    i=0
    dict={}     #document content with all ids
    doc=[]
    index={}   #inverted index

    for i in range(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])):
        docId=str(i+1)

        #reading content of files in abstract folder
        f1=open(DIR+docId+".txt",'r')
        file_con=f1.read()
        file_con=file_con.replace('\n',' ')

        file_con=re.sub(r'[0–9]+', '', file_con )
        f = open("Stopword-List.txt", 'r')
        for line in f:
            for st in line.split():
                file_con=file_con.lower().replace(' '+st+' ',' ')
        f.close()
    
        #Tokenizing words and removing punctuations and symbols
        doc=word_tokenize(file_con)
        doc=[''.join(c for c in s if c not in string.punctuation) for s in doc]
        doc=[s for s in doc if s]
        
        #stemming of tokens
        stemming=[]     
        for j in doc:
            stemming.append(Pstem.stem(j))

        #Removing duplicate tokens
        temp=[]
        for w in stemming:
            if w not in temp:
                temp.append(w)
        stemming=temp
        stemming=sorted(stemming)
        
        #creating posting lists
        for w in stemming:
            index.setdefault(w,[])
            index[w].append(i+1)

    #Sorting inverted Index
    s_index={}
    for key in sorted(index.keys()):
        s_index[key]=index[key]

    # print(s_index)  ###uncomment to view inverted index
    return index

#Creating positional index for processing Proximity queries
def Pos_ind():
    DIR = 'Abstracts/'
    i=0
    dict={}     #document content with all ids
    doc=[]
    index={}   #inverted index
    f = open("Stopword-List.txt", 'r')
    for i in range(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])):
        docId=str(i+1)

        #reading content of files in abstract folder      
        f1=open(DIR+docId+".txt",'r')
        file_con=f1.read() 

        file_con=file_con.replace('\n',' ')
        file_con=re.sub(r'[0–9]+', '', file_con )
        f = open("Stopword-List.txt", 'r')
        for line in f:
            for st in line.split():
                file_con=file_con.lower().replace(' '+st+' ',' ')
        f.close()
    
        #Tokenizing words and removing punctuations and symbols
        doc=word_tokenize(file_con)
        doc=[''.join(c for c in s if c not in string.punctuation) for s in doc]
        doc=[s for s in doc if s]
        
        #stemming tokens
        stemming=[]
        for j in doc:
            stemming.append(Pstem.stem(j))
       
        #creating posting lists
        temp={}
        pos=0
        for w in stemming:
            temp.setdefault(w,[])
            temp[w].append(pos)
            pos=pos+1
        
        #Creating posional index
        for w in temp:
            if index.get(w):
                index[w][docId]=temp[w]
            else:
                index.setdefault(w,[])
                index[w]={}
                index[w][docId]=temp[w]
    sorted(index)
    # print(index) ####uncomment to print positional index
    return index

#Boolean Query processing
def bool_query(query,index):
    query1=word_tokenize(query)
    oper=['AND', 'OR', 'NOT']
    q_words=[]
    q_oper=[]
    NOT_index=[]
    count=0

    #seperate words and boolean expressions
    for w in query1:
        if(w not in oper):
            q_words.append(w)
            count=+1
        else:
            if(w=='NOT'):
                NOT_index.append(count)
            else:
                q_oper.append(w)          
            count=+1
    stemming=[]
    stemming1=[]

    #stemming query words
    for j in query1:
        if(j not in q_oper):
            stemming1.append(Pstem.stem(j))
    for j in q_words:
        stemming.append(Pstem.stem(j))
    r=[]
    temp=[]
    
    #For processing queries with NOT
    if(NOT_index):
        if(len(stemming)==1):   
            return(set(range(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))).symmetric_difference(set(index[stemming1[1]])))  
        for i in range(len(NOT_index)):
            r.append(set(range(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))).symmetric_difference(set(index[stemming1[i+1]])))
            temp.append(stemming1[i+1])

    #Getting posting lists of tokens in query
    for w in stemming:
        if(w not in temp):
            r.append(get_post(w,index))
    if(len(stemming)==1):   
        return(get_post(stemming[0],index))

    #Processing queries of AND, OR expressions
    if(len(stemming)==2 and q_oper[0]=='AND'):
        result=Oper_AND(r[0],r[1])
        return result

    elif(len(stemming)==2 and q_oper[0]=='OR'):
        result=Oper_OR(r[0],r[1])
        return result

    elif(len(stemming)==3 and q_oper[0]=='OR'):
        result=Oper_OR(r[0],r[1])
        if(q_oper[1]=='AND'):
            result1=set(result)
            result2=Oper_AND(result1,r[2])
        if(q_oper[1]=='OR'):
            result1=set(result)
            result2=Oper_OR(result1,r[2])
        return result2

    elif(len(stemming)==3 and q_oper[0]=='AND'):
        result=Oper_AND(r[0],r[1])
        if(q_oper[1]=='OR'):
            result1=set(result)
            result2=Oper_OR(result1,r[2])
        if(q_oper[1]=='AND'):
            result1=set(result)
            result2=Oper_AND(result1,r[2])
        return result2

#Retrieving posting list from inverted index
def get_post(q_word, index):
    l0=set()
    for k, v in index.items():
        if(k==q_word):
            for val in v:
                l0.add(val)
    return sorted(l0)       

#And operation between posting lists
def Oper_AND(r1, r2):
    result=set(r1).intersection(r2)
    return sorted(result)

#OR operation between posting lists
def Oper_OR(r1,r2):
    result=set(r1).union(r2)
    return sorted(result)

#Processing Proximity Queries
def Proxi_query(query, index):
    query=query.replace(' AND ', ' ')
    q=word_tokenize(query)

    if '/' in q[len(q)-1]:
        q[2]=q[2].replace('/', '')
        k=int(q[2])+1
    else:
        k=1

    #stemming tokens of query
    stemming=[]
    for j in q:
        stemming.append(Pstem.stem(j))
    w1=index.get(stemming[0])
    w2=index.get(stemming[1])
    AND=set(w1).intersection(w2)
    result=[]
    i=j=0

    #Retrieving positional list and getting results
    for w in AND:
        pos1=index.get(stemming[0])[w]
        pos2=index.get(stemming[1])[w]  
        for i in range(len(pos1)):
            for j in range(len(pos2)):
                if(abs(pos1[i]-pos2[j])==k):
                    result.append(w)
                elif pos2[j]>pos1[i]:
                    break
        result=list(dict.fromkeys(result))
    return result


def main():
    bool_oper=['AND','OR','NOT']
    query=simpledialog.askstring(title="Boolean Model", prompt="Enter Query: ")
    # query=input('Enter Query: ')
    q=word_tokenize(query)
    if '/' in q[len(q)-1]:
        ind=Pos_ind()
        result=Proxi_query(query,ind)
    else:
        ind=Inv_ind()
        result=bool_query(query,ind)       
    messagebox.showinfo("Result-Set",result)
    print(result)

main()