import MeCab
import json
import os
import sys
import pickle
import numpy as np

if '--make_data' in sys.argv:
  m = MeCab.Tagger('-Owakati')
  for line in open('./misc/download/reviews.json'):
    obj = json.loads( line )
    text = '********' + obj['review'] + '************'
    terms = '_'.join( m.parse( text ).strip().split() )
    #print( terms )
    for i in range(len(terms)-16):
      head = terms[i:i+8]
      target = terms[i+8]
      tail = terms[i+8:i+16]
      if target != '_' and tail[1] == '_': continue
      #print(head, target, tail )
      if target != '_':
        tail2 = tail.replace('_', '')[:7] 
        head2 = head.replace('_', '')[-4:] + tail2[0]
        print(head2, 'x', tail2[1:])
        continue
      if target == '_':
        tail2 = tail.replace('_', '')[:6]
        head2 = head.replace('_', '')[-5:]  
        print(head2, 'o', tail2)
        continue

if '--make_sparse' in sys.argv:
  idfs = set()
  for enum, line in enumerate( open('./misc/download/dataset_raw.txt') ):
    line = line.strip()
    if enum%100000 == 0:
      print('now iter', enum, line, 'size', len(idfs))
    flag = 0.0 if ' x ' in line else 1.0
    line = line.replace(' x ', '').replace(' o ', '')
    for index, char in enumerate(list(line)):
      idf = '%d%s'%(index,char)
      idfs.add(idf)
  idf_index = {} 
  for index, idf in enumerate(list(idfs)):
    idf_index[idf] = index
  open('./misc/download/idf_index.pkl', 'wb').write( pickle.dumps(idf_index) )

if '--make_sparse2' in sys.argv:
  idf_index = pickle.loads(open('./misc/download/idf_index.pkl', 'rb').read( ) )
  f = open('./misc/download/dataset.txt', 'w')
  for enum, line in enumerate( open('./misc/download/dataset_raw.txt') ):
    line = line.strip()
    if enum%100000 == 0:
      print('now iter', enum, line)
    flag = 0.0 if ' x ' in line else 1.0
    line = line.replace(' x ', '').replace(' o ', '')
    sparse = ' '.join( ['%d:1.0'%idf_index['%d%s'%(index,char)] for index, char in enumerate(list(line))] )
    data = '%0.2f %s'%(flag, sparse)
    f.write(data+ '\n')
