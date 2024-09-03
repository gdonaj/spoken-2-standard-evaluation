import sys
import argparse
import random
import numpy as np
import Levenshtein

def CalculateAR(rawErrors,n,twoSided=True):

    pValues = [None]
    for testFileNumber, rawErrorsThisFile in enumerate(rawErrors):
        
        if (testFileNumber == 0):
            rawErrorsBaseline = rawErrorsThisFile
            setSize = len(rawErrorsBaseline)
            continue
        
        count = 0
        actualDiff = sum(rawErrorsBaseline) - sum(rawErrorsThisFile)
        
        for i in range(n):
            newDiff = 0
            for j in range(setSize):
                r = random.random()
                if (r > 0.5):
                    newDiff = newDiff + rawErrorsBaseline[j] - rawErrorsThisFile[j]
                else:
                    newDiff = newDiff - rawErrorsBaseline[j] + rawErrorsThisFile[j]

            if (twoSided==True):
                if(abs(newDiff) >= abs(actualDiff)):
                    count = count + 1
            else:
                if(newDiff >= actualDiff):
                    count = count + 1

        pValues.append(float(count + 1.0) / float(n+1.0))

    return pValues

def CalculatePairedBR(rawErrors,n):

    pValues = [None]
    for testFileNumber, rawErrorsThisFile in enumerate(rawErrors):
        
        if (testFileNumber==0):
            rawErrorsReference = rawErrorsThisFile
            setSize = len(rawErrorsReference)
            continue

        count = 0
        
        for i in range(n):
            rawErrorsDiff = np.subtract(rawErrorsReference,rawErrorsThisFile)
            x = sum(np.random.choice(rawErrorsDiff,size=setSize,replace=True))

            if(x<=0):
                count = count + 1
        
        pValues.append(float(count+1.0) / float(n+1.0))
    
    return pValues

def CalculateBR(rawErrors,n,twoSided=True):

    pValues = [None]
    for testFileNumber, rawErrorsThisFile in enumerate(rawErrors):

        if (testFileNumber==0):
            rawErrorsBaseline = rawErrorsThisFile
            setSize = len(rawErrorsBaseline)
            continue

        count = 0
        actualDiff = sum(rawErrorsBaseline) - sum(rawErrorsThisFile)

        allBootstraps = []
        for i in range(n):
            allBootstraps.append(np.random.choice(range(setSize),size=setSize,replace=True))

        sampleMean = 0
        for thisBootstrap in allBootstraps:
            for i in thisBootstrap:
                sampleMean = sampleMean + rawErrorsBaseline[i] - rawErrorsThisFile[i]
        sampleMean = float(sampleMean) / float(n)
        
        for thisBootstrap in allBootstraps:
            leftside = 0
            for i in thisBootstrap:
                leftside = leftside + rawErrorsBaseline[i] - rawErrorsThisFile[i]
            leftside = leftside - sampleMean
            
            if (twoSided==True):
                if (abs(leftside) >= abs(actualDiff)):
                    count = count + 1
            else:
                if (leftside >= actualDiff):
                    count = count + 1
        
        pValues.append(float(count+1.0) / float(n))
    
    return pValues

def GetAlignment(lineSource, lineReference, lineTest):

    editOpsAll = Levenshtein.editops(lineReference,lineTest)
    opsOnReference = 0
    opsOnTest = 0

    for editOps in editOpsAll:
        if (editOps[0] == 'insert'):
            lineSource.insert(editOps[1]+opsOnReference, "")
            lineReference.insert(editOps[1]+opsOnReference, "")
            opsOnReference = opsOnReference + 1
        elif (editOps[0] == 'delete'):
            lineTest.insert(editOps[2]+opsOnTest, "")
            opsOnTest = opsOnTest + 1
    
    return lineSource, lineReference, lineTest

def processFile(LinesSource, LinesReference, LinesTest):
    
    mainResults = {
        "correct"    : 0,
        "WordInsert" : 0,
        "WordDelete" : 0,
        "missing"    : 0,
        "wrong"      : 0,
        "insert"     : 0,
        "total"      : 0,
        "notneeded"  : 0
    }
    
    rawErrors = []
    
    for lineSource, lineReference, lineTest in zip(LinesSource,LinesReference,LinesTest):
        
        lineSource    = lineSource.split()
        lineReference = lineReference.split()
        lineTest      = lineTest.split()
        
        lineSource, lineReference, lineTest = GetAlignment(lineSource, lineReference, lineTest)

        rawErrorsThisLine = 0
        
        for wordS, wordR, wordT in zip(lineSource, lineReference, lineTest):
            if (wordS != ""):
                mainResults["total"] = mainResults["total"] + 1
            
            if (wordS == wordR):
                mainResults["notneeded"] = mainResults["notneeded"] + 1

            if (wordT == wordR):
                mainResults["correct"] = mainResults["correct"] + 1
            elif (wordR == ""):
                mainResults["WordInsert"] = mainResults["WordInsert"] + 1
                rawErrorsThisLine = rawErrorsThisLine + 1
            elif (wordT == ""):
                mainResults["WordDelete"] = mainResults["WordDelete"] + 1
                rawErrorsThisLine = rawErrorsThisLine + 1
            elif (wordS == wordR):
                mainResults["insert"] = mainResults["insert"] + 1
                rawErrorsThisLine = rawErrorsThisLine + 1
            elif (wordS == wordT):
                mainResults["missing"] = mainResults["missing"] + 1
                rawErrorsThisLine = rawErrorsThisLine + 1
            else:
                mainResults["wrong"] = mainResults["wrong"] + 1
                rawErrorsThisLine = rawErrorsThisLine + 1
                
        rawErrors.append(rawErrorsThisLine)
                
    return mainResults, rawErrors

def writeHTML(LinesSource, LinesReference, LinesTestAll, OutFileName, InFileNames):

    f = open(OutFileName, "w")

    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<style>\n")
    f.write("table, th, td { border: 1px solid aqua; border-collapse: collapse; padding: 3px;}\n")
    f.write("</style>\n")
    f.write("</head>\n")
    f.write("<body>\n")

    for fileName, LinesTest in zip(InFileNames, LinesTestAll):
        f.write("<h1>Filename: " + fileName + "</h1>\n")

        n = len(LinesSource)
        i = 0
        for lineSource, lineReference, lineTest in zip(LinesSource,LinesReference,LinesTest):
            i = i + 1

            lineSource    = lineSource.split()
            lineReference = lineReference.split()
            lineTest      = lineTest.split()

            lineSource, lineReference, lineTest = GetAlignment(lineSource, lineReference, lineTest)
 
            ErrorsTypesThisLine = []
            ChangeNeeded = []
            ErrorsFound = False

            for wordS, wordR, wordT in zip(lineSource, lineReference, lineTest):
                if (wordS == wordR):
                    ChangeNeeded.append(0)
                else:
                    ChangeNeeded.append(1)

                if (wordT == wordR):
                    ErrorsTypesThisLine.append("correct")
                elif (wordR == ""):
                    ErrorsTypesThisLine.append("wordInsert")
                    ErrorsFound = True
                elif (wordT == ""):
                    ErrorsTypesThisLine.append("wordDelete")
                    ErrorsFound = True
                elif (wordS == wordR):
                    ErrorsTypesThisLine.append("insert")
                    ErrorsFound = True
                elif (wordS == wordT):
                    ErrorsTypesThisLine.append("missing")
                    ErrorsFound = True
                else:
                    ErrorsTypesThisLine.append("wrong")
                    ErrorsFound = True

            if ErrorsFound == False:
                continue

            f.write("Line no. " + str(i) + " / " + str(n) + "\n")
            f.write("<table>\n")
            f.write("  <tr>\n")

            for wordS, change, ErrorType in zip(lineSource,ChangeNeeded,ErrorsTypesThisLine):
                if (change == 0) and (ErrorType == "correct"):
                    f.write("    <td style=\"color:grey;\">" + wordS + "</td>\n")
                else:
                    f.write("    <td>" + wordS + "</td>\n")
            f.write("  </tr>\n")

            for wordR, change, ErrorType in zip(lineReference,ChangeNeeded,ErrorsTypesThisLine):
                if (change == 0) and (ErrorType == "correct"):
                    f.write("    <td style=\"color:grey;\">" + wordR + "</td>\n")
                else:
                    f.write("    <td>" + wordR + "</td>\n")
            f.write("  </tr>\n")

            for wordT, change, ErrorType in zip(lineTest,ChangeNeeded,ErrorsTypesThisLine):
                if (change == 0) and (ErrorType == "correct"):
                    f.write("    <td style=\"color:grey;\">" + wordT + "</td>\n")
                elif ErrorType == "correct":
                    f.write("    <td>" + wordT + "</td>\n")
                elif ErrorType == "wordInsert":
                    f.write("    <td bgcolor=\"red\">" + wordT + "</td>\n")
                elif ErrorType == "wordDelete":
                    f.write("    <td bgcolor=\"red\">" + wordT + "</td>\n")
                elif ErrorType == "insert":
                    f.write("    <td bgcolor=\"lightblue\">" + wordT + "</td>\n")
                elif ErrorType == "missing":
                    f.write("    <td bgcolor=\"lightcoral\">" + wordT + "</td>\n")
                elif ErrorType == "wrong":
                    f.write("    <td bgcolor=\"lightgreen\">" + wordT + "</td>\n")

            f.write("  </tr>\n")
            f.write("</table><p>\n")

    f.write("</body>\n")
    f.write("</html>\n")
    f.close()

def writeLatex(mainResultsForFiles,pAR,pBR,pPairedBR,args):
    
    OutFileName = args.latex
    noFiles = len(args.TestFiles)
    noValues = 6
    if (args.ar == True):
        noValues = noValues + 1
    if (args.br == True):
        noValues = noValues + 2
    
    width = max(map(len, args.TestFiles))
    if (width < 15):
        width = 15
    cells = [["" for i in range(noValues+1)] for j in range(noFiles+1)]
    
    cells[0][0] = "{0:>{1}s}".format("Filename", width)
    cells[0][1] = "Corr  [\%]"
    cells[0][2] = "Miss  [\%]"
    cells[0][3] = "Wrng  [\%]"
    cells[0][4] = "Ins   [\%]"
    cells[0][5] = "W-ins [\%]"
    cells[0][6] = "W-del [\%]"
    
    if (args.ar == True) and (args.br == False):
        cells[0][7] = "AR p-value"
    elif (args.ar == False) and (args.br == True):
        cells[0][7] = "BR p-value"
        cells[0][8] = "P-BR p-val"
    elif (args.ar == True) and (args.br == True):
        cells[0][7] = "AR p-value"
        cells[0][8] = "BR p-value"
        cells[0][9] = "P-BR p-val"
    
    for row in range(1,noFiles+1):

        total = mainResultsForFiles[row-1]['total']

        cells[row][0] = "{0:>{1}s}".format(args.TestFiles[row-1], width)
        cells[row][1] = '% 10.2f' % (mainResultsForFiles[row-1]['correct']    / total * 100) 
        cells[row][2] = '% 10.2f' % (mainResultsForFiles[row-1]['missing']    / total * 100) 
        cells[row][3] = '% 10.2f' % (mainResultsForFiles[row-1]['wrong']      / total * 100) 
        cells[row][4] = '% 10.2f' % (mainResultsForFiles[row-1]['insert']     / total * 100) 
        cells[row][5] = '% 10.2f' % (mainResultsForFiles[row-1]['WordInsert'] / total * 100) 
        cells[row][6] = '% 10.2f' % (mainResultsForFiles[row-1]['WordDelete'] / total * 100) 
        
        if (args.ar == True) and (args.br == False):
            if (pAR[row-1] is None):
                cells[row][7] = "          "
            else:
                cells[row][7] = '% 10.4f' % (pAR[row-1])
        elif (args.ar == False) and (args.br == True):
            if (pAR[row-1] is None):
                cells[row][7] = "          "
                cells[row][8] = "          "
            else:
                cells[row][7] = '% 10.4f' % (pBR[row-1])
                cells[row][8] = '% 10.4f' % (pPairedBR[row-1])
        elif (args.ar == True) and (args.br == True):
            if (pAR[row-1] is None):
                cells[row][7] = "          "
                cells[row][8] = "          "
                cells[row][9] = "          "
            else:
                cells[row][7] = '% 10.4f' % (pAR[row-1])
                cells[row][8] = '% 10.4f' % (pBR[row-1])
                cells[row][9] = '% 10.4f' % (pPairedBR[row-1])


    f = open(OutFileName, "w")

    if (args.ar == False) and (args.br == False):
        f.write("\\begin{tabular}{lrrrrrr}\n")
    if (args.ar == True) and (args.br == False):
        f.write("\\begin{tabular}{lrrrrrrr}\n")
    if (args.ar == False) and (args.br == True):
        f.write("\\begin{tabular}{lrrrrrrrr}\n")
    if (args.ar == True) and (args.br == True):
        f.write("\\begin{tabular}{lrrrrrrrrr}\n")
    f.write("\hline\n")

    # for i in range(noFiles+1):
    #     for j in range(noValues+1):
    #         f.write(cells[i][j])
    #         if (j < noValues):
    #             f.write(" & ")
    #     f.write(" \\\\\n")
    #     if (i == 0):
    #         f.write("\\hline\n")    

    for j in range(noValues+1):
        for i in range(noFiles+1):
            f.write(cells[i][j])
            if (i < noFiles):
                f.write(" & ")
        f.write(" \\\\\n")
        if (j == 0):
            f.write("\\hline\n")    
    

    f.write("\\hline\n")
    f.write("\\end{tabular}\n")
    f.close()
    pass

def showResultsSimple(resultsForFiles):
    for resultsSingle in resultsForFiles:
        correct = float(resultsSingle["correct"]) / float(resultsSingle["total"]) * 100
        print ("%.2f" % correct)

def showResults(ResultsForFiles,pValuesAR,pValuesBR,pValuesPairedBR,args):
    for i, (ResultsSingle, Filename) in enumerate (zip(ResultsForFiles, args.TestFiles)):
        correct = float(ResultsSingle["correct"])    / float(ResultsSingle["total"]) * 100
        missing = float(ResultsSingle["missing"])    / float(ResultsSingle["total"]) * 100
        wrong   = float(ResultsSingle["wrong"])      / float(ResultsSingle["total"]) * 100
        insert  = float(ResultsSingle["insert"])     / float(ResultsSingle["total"]) * 100
        wordINS = float(ResultsSingle["WordInsert"]) / float(ResultsSingle["total"]) * 100
        wordDEL = float(ResultsSingle["WordDelete"]) / float(ResultsSingle["total"]) * 100
        noNeed  = float(ResultsSingle["notneeded"])  / float(ResultsSingle["total"]) * 100

        print ("Filename: " + Filename)
        print ("")
        print ("-> Correctly converted  = " + "%5.2f" % correct  + " %")
        print ("-> Missing conversions  = " + "%5.2f" % missing  + " %")
        print ("-> Wrong conversions    = " + "%5.2f" % wrong    + " %")
        print ("-> Unwarranted conv.    = " + "%5.2f" % insert   + " %")
        print ("-> Inserted words       = " + "%5.2f" % wordINS  + " %")
        print ("-> Deleted words        = " + "%5.2f" % wordDEL  + " %")
        print ("-> No change needed     = " + "%5.2f" % noNeed   + " %")

        if (i>0) and (args.ar):
            print ("-> AR p-value           = " + "%7.4f" % pValuesAR[i])
        
        if (i>0) and (args.br):
            print ("-> BR p-value           = " + "%7.4f" % pValuesBR[i])
        
        if (i>0) and (args.br):
            print ("-> Paired BR p-value    = " + "%7.4f" % pValuesPairedBR[i])

        print ("")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--br',     action='store_true', required=False, default=False, help='Perform bootstrap resampling statistical test')
    parser.add_argument('--br-n',   metavar="INT",  type=int, required=False, default=1000, help='Number of iterations in bootstrap resampling test (default=1000)')
    parser.add_argument('--ar',     action='store_true', required=False, default=False, help='Perform approximate randominzation statistical test')
    parser.add_argument('--ar-n',   metavar="INT",  type=int, required=False, default=1000, help='Number of iterations in approximate randominzation test (default=1000)')
    parser.add_argument('--latex',  metavar="FILE", type=str, required=False, default=None, help='Write results in LaTeX tabaluar form')    
    parser.add_argument('--html',   metavar="FILE", type=str, required=False, default=None, help='Name of HTML file for detailed results')
    parser.add_argument('--simple', action='store_true', required=False, default=False, help='Output only numbers of main results (e.g., for automatic processing)')
    parser.add_argument('SourceFile',    metavar="SourceFile",    type=str, help="Source side file")
    parser.add_argument('ReferenceFile', metavar="ReferenceFile", type=str, help="References for target side")
    parser.add_argument('TestFiles',     metavar="TestFile",      type=str, nargs='+', help="Conversion output(s) to be evaluated")
    args = parser.parse_args()
    
    mainResultsForFiles = []
    rawResultsForFiles = []
    pValuesAR = []
    pValuesBR = []
    pValuesPairedBR = []

    LinesSource = []
    file = open(args.SourceFile, "r")
    for line in file:
        LinesSource.append(line)
    file.close()
    
    LinesReference = []
    file = open(args.ReferenceFile, "r")
    for line in file:
        LinesReference.append(line)
    file.close()
    
    LinesTestAll = []
    for TestFile in args.TestFiles:
        
        LinesTest = []
        file = open(TestFile, "r")
        for line in file:
            LinesTest.append(line)
        file.close()
        LinesTestAll.append(LinesTest)
        
        thisFileResults, thisFileRaw = processFile(LinesSource,LinesReference,LinesTest)
        mainResultsForFiles.append(thisFileResults)
        rawResultsForFiles.append(thisFileRaw)
    
    if (args.ar == True):
        pValuesAR = CalculateAR(rawResultsForFiles,args.ar_n)
    
    if (args.br == True):
        pValuesBR = CalculateBR(rawResultsForFiles,args.br_n)
    
    if (args.br == True):
        pValuesPairedBR = CalculatePairedBR(rawResultsForFiles,args.br_n)

    if (args.simple is True):
        showResultsSimple(mainResultsForFiles)
    else:
        showResults(mainResultsForFiles,pValuesAR,pValuesBR,pValuesPairedBR,args)

    if (args.html is not None):
        writeHTML (LinesSource,LinesReference,LinesTestAll,args.html,args.TestFiles)
        
    if (args.latex is not None):
        writeLatex (mainResultsForFiles,pValuesAR,pValuesBR,pValuesPairedBR,args)

if __name__ == '__main__':
    main()
