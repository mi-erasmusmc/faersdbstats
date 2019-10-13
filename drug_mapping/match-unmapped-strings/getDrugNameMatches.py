#!/usr/bin/python3

# getDrugNameMatches.py

# Accepts string input - expects the exact string for a drug of
# interest (could be ingredient generic or brand)

# Parameter specifies if the string results returned need to include
# exact match or a "fuzzy" to some metric of fuzzyness (e.g., 1,
# 2, or 3, character replacements)

# Return all records that have the match


import sys
import getopt
import Levenshtein
import re


def main(argv):
    distance = 0
    drugstring = ''
    drugstringL = None
    inputFName = ''
    outputFName = None

    linesN = 0
    dnFile = None
    lines = None
    badRecs = []
    originalStringsD = {}
    matches = []
    outString = ""

    try:
        opts, args = getopt.getopt(argv, 'hd:s:f:o:', ['distance=', 'drugstring=', 'inputfile=', 'outputfile='])
    except getopt.GetoptError:
        print('getDrugNameMatches.py -d <number of character changes to match> <string>')
        sys.exit(2)

    for opt, arg in opts:
      if opt == '-h':
         print('getDrugNameMatches.py -d <allowable number of character changes to match> -s <drug string - could be a single drug name or a quoted pipe-delimitted list of drug names e.g., "name 1|name 2|name 3". If the latter, names cannot include pipes.> -f <pipe delimited file (unix newlines) with unmapped drug strings as the first field and the count of reports as the second> -o <(optional) file to write the output to>')
         sys.exit()
         
      elif opt in ('-d', '--distance'):
          try:
              distance = int(arg)
          except ValueError:
              print('Please pass the allowable as a number of character changes to match - you passed',arg)
              sys.exit(2)
              
      elif opt in ("-s", "--drugstring"):
         drugstring = arg.upper()
         if drugstring.find(',') != -1:
             drugstringL = [x.strip() for x in drugstring.split('|')]

      elif opt in ("-f", "--inputfile"):
         inputFName = arg

      elif opt in ("-o", "--outputfile"):
         outputFName = arg

    outString += '\nSearching for string matches to ' + drugstring + ' using input file ' + inputFName + ' and ' + str(distance) + ' allowed character replacements.\n'

   
    try:
        dnFile = open(inputFName,"r")
        
    except IOError:
        outString += '\nERROR: There was an error opening the file, please be sure it is a simple text file (i.e., not a Word document or similar) pipe delimited file (unix newlines) with unmapped drug strings as the first field and the count of reports as the second\n'
       
    lines = dnFile.read().split('\n')
    dnFile.close()
    
    linesN = len(lines)
    outString += 'Input file ' + str(inputFName) + ' has ' + str(linesN) + ' lines.'

    i = -1
    for elt in lines:
        i +=1
        
        pipeCnt = elt.count('|')
        if pipeCnt == 0:
            outString += '\n\nNOTE: There is a record that has no pipes - assuming end of file. Total number of lines processed: ' + str(i) + '. Total lines in file:' + str(linesN) + '\n'
            break
        
        if pipeCnt > 1:
            badRecs.append(elt)
            continue
            
        (dname,recCnt) = elt.split('|')
        originalStringsD[dname.upper()] = 1


    outString += '\n\nTotal length of unmapped drug strings input from the file (removing duplicates): ' + str(len(originalStringsD.keys())) + '\n'

    if distance == 0:
        if not drugstringL:
            matches = list(filter(lambda x: x.find(drugstring) != -1, originalStringsD.keys()))
        else:
            for delt in drugstringL:
                matches += list(filter(lambda x: x.find(delt) != -1, originalStringsD.keys()))
    else:
        ## Iterate through the list of umapped, split each by non-alphanumeric, iterate through that list, anything that matches based on the distance is a hit
        if not drugstringL:
            for k in originalStringsD.keys():
                kL = re.split('[^a-zA-Z]', k)
                subMatches = filter(lambda x:  Levenshtein.distance(drugstring, x) == distance, kL)
                if len(list(subMatches)) > 0:
                    matches.append(k)
        else:
            for delt in drugstringL:
                for k in originalStringsD.keys():
                    kL = re.split('[^a-zA-Z]', k)
                    subMatches = filter(lambda x: Levenshtein.distance(delt, x) == distance, kL)
                    if len(list(subMatches)) > 0:
                        matches.append(k)

    sortedMatches = list(set(matches))
    sortedMatches.sort()

    outString += '\n\n\nNOTE: these drug strings could not be processed because they contain more than one pipe symbol. These will need to be corrected BOTH in the database and in   the input file:\n' + "\n".join(badRecs) + '\n'
    
    outString += '\n\n\nMATCH RESULTS:\n' + '\n'.join(sortedMatches) + '\n'

    if outputFName:
        oFile = open(outputFName, 'w')
        oFile.write(outString)
        oFile.close()
    else:
        print(outString)
    
if __name__ == "__main__":
   main(sys.argv[1:])


    