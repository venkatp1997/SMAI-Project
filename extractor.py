"""
Contains functions to handle data. 
Extracts and removes noise, ultimately to give {authors: keywords} relation.

"""
import re
import pandas as pd
from collections import Counter
import pickle as pi
import tfidf 

def second_names(x):
    if x: return x.split()[-1]
    else: return ''

def filter_authors(probable_authors):
    """ Returns filtered list of authors """
    #second_names = lambda x: x.split()[-1]
    names, ids = zip(*probable_authors)
    cleaned = []
    counter = Counter(list(map(second_names, names)))
    for (name, aid) in probable_authors:
        if counter[second_names(name)] == 1:
            cleaned.append((name, aid))
    return cleaned



def squeeze(aid_aname_papers):
    id_name = {}
    id_papers = {}
    paper_authors = {}

    # Create list of authors for each paper
    # {key: value} = {pid: (name, aid)}
    print("Creating list of authors for paper..")
    for (pid, aid, name) in aid_aname_papers:
        if pid not in paper_authors.keys():
            paper_authors[pid] = []
        paper_authors[pid].append((name, aid))

    #print(paper_authors)
    # Filter authors for paper, noise
    print("Filtering to remove noise...")
    for pid in paper_authors:
        paper_authors[pid] = filter_authors(paper_authors[pid])

    # After filtering, create required relation
    print("Creating required relation...")
    for pid in paper_authors:
        for (aname, aid) in paper_authors[pid]:
            if aid not in id_papers.keys():
                id_papers[aid] = []
                id_name[aid] = aname
            id_papers[aid].append(pid)

    gentuple = lambda x: (x, id_name[x], id_papers[x])
    return map(gentuple, id_name.keys())

def export(authors, outputfile):
    # TODO add header rows.
    print("Opening file to writeout...")
    with open(outputfile, 'w+') as fp:
        data = pd.DataFrame.from_records(authors)
        data.to_csv(authors)


def Authors(authorpaperfile):
    print("Loading data...")
    data = pd.read_csv('dataRev2/PaperAuthor.csv', delimiter=',', header=0)
    data.fillna('', inplace=True)
    print("Loaded data...")
    aid_aname_papers = zip(data["PaperId"], data["AuthorId"], data["Name"])

    print("Squeezing authors...")
    return squeeze(aid_aname_papers)


def keywords_Paper(paperfile):
    """ Reads csv, returns dict{ paper_id: keywords} """
    data = pd.read_csv(paperfile, delimiter=',', header=0)
    data.fillna('', inplace=True)
    cleanKeyword = lambda x: re.split(':|;|,|\|| ', x)
    strdata = map(str,data["Id"])
    pid_keywords = zip(strdata, map(cleanKeyword, data["Keyword"]))

    return dict(pid_keywords)

def authors_Paper(authorfile):
    """ Reads csv, returns [(author_id, [paper_ids])]"""
    data = pd.read_csv(authorfile, delimiter=',', header=0)
    data.fillna('', inplace=True)
    translator = str.maketrans({key:None for key in '\'\"[] '})
    extractPapers = lambda x: x.translate(translator).split(',')
    aid_pids = zip(data["author_id"], map(extractPapers, data["paper_ids"]))
    return list(aid_pids)

def authors_keywords(auth_paper, keyword_paper):
   """ Reads dicts, creates new relation: {author:keyword} """
   # getKeywords = lambda paper_id: keyword_paper[int(paper_id)]
   # getAuthorKeywords = lambda x: (x[0], list(map(getKeywords, x[1])))
   # auth_kwds = list(map(getAuthorKeywords, auth_paper))
   auth_kwds = {}
   for x in auth_paper:
       for paper in x[1]:
           if paper in keyword_paper:
               for wd in keyword_paper[paper]:

                    if x[0] in auth_kwds:
                        auth_kwds[x[0]].append(wd)
                    else:
                        auth_kwds[x[0]] = []
                        auth_kwds[x[0]].append(wd)
   return auth_kwds

def journal_keywords(keyword_paper,papers):
    """ Returns a dict where the key is JournalId and the value is the list of keywords assosciated with all the papers published in that journal. """
    data = pd.read_csv(papers, delimiter=',', header=0)
    data.fillna('', inplace=True)
    translator = str.maketrans({key:None for key in '\'\"[] '})
    # extractPapers = lambda x: x.translate(translator).split(',')
    aid_pids = zip(data["JournalId"],data["Id"])
    jKw=list(aid_pids)
    kWd={}
    for (i,j) in jKw:
        if i not in kWd:
            kWd[i]=[]
        j=str(j)
        if j not in keyword_paper: continue
        for w in keyword_paper[j]:
            kWd[i].append(w)
    return kWd

if __name__ == '__main__':
    #records = Authors('dataRev2/PaperAuthor.csv')
    #exportConfirmedAuthor(records, "confirmedAuthor.csv")
    kwP = keywords_Paper("dataRev2/Paper.csv")
    print(" keywords of papers : DONE")
#    for a,b in kwP.items():
#        print(b)
#        k = input()
#        if k == '0':
#            break
    aP = authors_Paper("confirmedAuthors.csv")
    print(" authors of papers : DONE")
#    for a in aP:
#        print(a)
#        k = input()
#        if k == '0':
#            break
    aKw = authors_keywords(aP, kwP)
    print(" Keyword of authors : DONE")
    T=tfidf.tfidf("keywrd")
    T.create()
    # for a,b in aKw.items():
    #     print(b)
    #     k = input()
    #     if k == '0':
    #         break
    # f = open('keywrd','wb')
    # pi.dump(aKw,f)
    jKw=journal_keywords(kwP,"dataRev2/Paper.csv")
    f=open('dataRev2/journalKeywords','wb')
    pi.dump(jKw,f)
