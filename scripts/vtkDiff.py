#! /usr/bin/env python

import vtkIO
from optparse import OptionParser
from xml.dom.minidom import parse
from copy import deepcopy

def IsInvalid(val):
    # other options exist to check for nan, but none is good
    # 1) use numpy.isnan() and numpy.isinf, which obviously requires numpy
    # 2) use math.isnan() and math.isinf(), which are available only in python versions >= 2.6
    if str(val) == str(1e400*0):
        return True
    return False

def vtkDiffOptionParser():
    usageMsg = "usage: %prog file1 file2 [option]"
    parser = OptionParser(usage=usageMsg)
    parser.add_option("-u", "--uniformTolerance", dest="uniformTolerance", metavar="TOLERANCE", \
                          help="specify a uniform tolerance that will be applied to all fields")
    parser.add_option("-f", "--toleranceFile", dest="toleranceFile", metavar="FILE", \
                          help="specify a .tol file that contains tolerances for each field to be compared")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbosity flag")
    return parser

def vtkDiffCheckOptions(options, args):
    if len(args) != 2:
        raise Exception()
    if options.uniformTolerance == None and options.toleranceFile == None:
        raise Exception("\nException:  Either --uniformTolerance or --toleranceFile option is required\n")
    return

def GetDataTuples(pt, goldData, data):
    numComponents = data.GetNumberOfComponents()
    goldDataTuple = None
    dataTuple = None
    if numComponents == 1:
        goldDataTuple = [goldData.GetTuple1(pt)]
        dataTuple = [data.GetTuple1(pt)]
    elif numComponents == 2:
        goldDataTuple = goldData.GetTuple2(pt)
        dataTuple = data.GetTuple2(pt)
    elif numComponents == 3:
        goldDataTuple = goldData.GetTuple3(pt)
        dataTuple = data.GetTuple3(pt)
    elif numComponents == 4:
        goldDataTuple = goldData.GetTuple4(pt)
        dataTuple = data.GetTuple4(pt)
    elif numComponents == 9:
        goldDataTuple = goldData.GetTuple9(pt)
        dataTuple = data.GetTuple9(pt)
    else:
        raise Exception("Invalid data dimension: " + str(numComponents))
        
    if goldDataTuple == None or dataTuple == None:
        raise Exception("Error processing " + dataName + ", invalid data")
            
    return (numComponents, goldDataTuple, dataTuple)

def CheckPvtuSanity(pvtuFileNames):    
    for timestep in range(len(pvtuFileNames)):
        pvtuFileName = pvtuFileNames[timestep][1]
        vtuData = vtkIO.GetGrid(pvtuFileName)
        if vtuData.GetPoints() == None:
            raise Exception ("Error reading " + pvtuFileName + ".  Invalid data?  Possible NaN or Inf?")
    return

def SetUniformTolerance(pvtuGoldFileName, pvtuFileName):
    tolerances = {}
    # get the list of fields from the first files in the time series
    vtuGoldData = vtkIO.GetGrid(pvtuGoldFileName)
    vtuGoldPointData = vtuGoldData.GetPointData()
    goldArrayNames = vtkIO.GetDataFieldNames(vtuGoldPointData)
    goldArrayNames.sort()
    vtuData = vtkIO.GetGrid(pvtuFileName)
    vtuPointData = vtuData.GetPointData()
    arrayNames = vtkIO.GetDataFieldNames(vtuPointData)
    arrayNames.sort()
    for i in range(len(goldArrayNames)):
        if arrayNames[i] != goldArrayNames[i]:
            raise Exception("Data files must contain the same fields if using the --uniformTolerance option")
        tolerances[arrayNames[i]] = float(options.uniformTolerance)
    return tolerances

def SetTolerances(toleranceFile):
    tolerances = {}
    toleranceElements = parse(toleranceFile).documentElement.getElementsByTagName("Tolerance")
    for toleranceElement in toleranceElements:
        variable = toleranceElement.getAttribute("variable")
        tol = toleranceElement.getAttribute("value")
        tolerances[variable] = float(tol)
    return tolerances

if __name__ == "__main__":

    print "\n----VTK File Comparison----\n"

    # handle command-line options
    parser = vtkDiffOptionParser()
    options, args = parser.parse_args()
    try:
        vtkDiffCheckOptions(options, args)
    except Exception, e:
        parser.print_help()
        print e
        exit(1)   

    # data file names
    pvdGoldFileName = args[0]
    pvtuGoldFileNames = None
    vtuGoldFileNames = None
    pvdFileName = args[1]
    pvtuFileNames = None
    vtuFileNames = None

    print "Data set one: ", pvdGoldFileName
    print "Data set two: ", pvdFileName

    # read the gold pvd file
    try:
        pvtuGoldFileNames = vtkIO.GetTimeCollection(pvdGoldFileName)
    except Exception, e:
        print "\nException thrown by vtkIO.GetTimeCollection():", e, "\n"
        exit(1)
    except:
        print "\nUnknown error generated by vtkIO.GetTimeCollection()\n"
        exit(1)

    # read the pvd file
    try:
        pvtuFileNames = vtkIO.GetTimeCollection(pvdFileName)
    except Exception, e:
        print "\nException thrown by vtkIO.GetTimeCollection():", e, "\n"
        exit(1)
    except:
        print "\nUnknown error generated by vtkIO.GetTimeCollection()\n"
        exit(1)

    # perform a sanity check on the data
    try:
        CheckPvtuSanity(pvtuGoldFileNames)
        CheckPvtuSanity(pvtuFileNames)
    except Exception, e:
        print  "\nException thrown by CheckPvtuSanity():", e, "\n"
        exit(1)

    # specify the fields to compare and set the tolerances
    if options.uniformTolerance != None and options.toleranceFile != None:
        parser.print_help()
        print "\nError: Invalid options, uniformTolerance and toleranceFile cannot both be specified\n"
        exit(1)
    if options.uniformTolerance != None:
        print "\nApplying uniform tolerance =", options.uniformTolerance
        tolerances = SetUniformTolerance(pvtuGoldFileNames[0][1], pvtuFileNames[0][1])
    elif options.toleranceFile != None:
        tolerances = SetTolerances(options.toleranceFile)

    # print out the fields to be compared and their tolerances
    print "\nFields to be comparied:"
    for key in tolerances.keys():
        if len(key) < 20:
            print " ", key, " "*(20-len(key)), tolerances[key]
        else:
            print " ", key, tolerances[key]
    if len(tolerances.keys()) == 0:
        print "  NONE!"

    # make sure the number of file names (timesteps) is the same
    if len(pvtuFileNames) != len(pvtuGoldFileNames):
        print "\nError, len(pvtuFileNames) != len(pvtuGoldFileNames).  Different numbers of time steps?\n"
        exit(1)

    # loop over the timesteps and compare requested data
    filesDiff = False
    for timestep in range(len(pvtuFileNames)):

        verboseText = "\nTime step " + str(timestep)
        nonVerboseText = "\nTime step " + str(timestep)
        printNonVerboseText = False

        # read pvtu files and points data
        pvtuGoldFileName = pvtuGoldFileNames[timestep][1]
        vtuGoldData = vtkIO.GetGrid(pvtuGoldFileName)
        if vtuGoldData.GetPoints() == None:
            print "\nError reading", pvtuGoldFileName, "\n"
            exit(1)
        pvtuFileName = pvtuFileNames[timestep][1]
        vtuData = vtkIO.GetGrid(pvtuFileName)
        if vtuData.GetPoints() == None:
            print "\nError reading", pvtuFileName, "\n"
            exit(1)

        # get the array of global node IDs and store them in lists
        goldIDs = []
        IDs = []        
        goldIDData = vtuGoldData.GetPointData().GetVectors("Id")
        IDData = vtuData.GetPointData().GetVectors("Id")
        if goldIDData == None or IDData == None:
            print "\nError:  Data not found for global ID field.  This field is required for vtkDiff.py.\n"
            exit(1)
        if IDData.GetNumberOfTuples() != goldIDData.GetNumberOfTuples():
            print "\nError:  Mismatched array sizes for ID field,", \
                IDData.GetNumberOfTuples(), "!=", goldIDData.GetNumberOfTuples(), "\n"
            exit(1)
        # Get the ID data
        for pt in range(IDData.GetNumberOfTuples()):
            try:
                numComponents, goldIDTuple, IDTuple = GetDataTuples(pt, goldIDData, IDData)
            except Exception, e:
                print "\n", e, "\n"
                exit(1)
            goldIDs.append([int(goldIDTuple[0])])
            IDs.append([int(IDTuple[0])])

        # compare data
        for dataName in tolerances.keys():
            
            # get the specified data for this time step
            # points data are handled in a unique way by VTK, so the are processed differently here
            goldData = None
            data = None
            if dataName == 'Points':
                goldData = vtkIO.GetPointTuples(vtuGoldData)
                data = vtkIO.GetPointTuples(vtuData)
            else:
                goldData = vtuGoldData.GetPointData().GetVectors(dataName)
                data = vtuData.GetPointData().GetVectors(dataName)

            # make sure data fields exist and are the same length
            if goldData == None or data == None:
                print "\nError:  Data not found for requested", dataName, "field.  Error in .comp file?\n"
                exit(1)
            if data.GetNumberOfTuples() != goldData.GetNumberOfTuples():
                print "\nError:  Mismatched array sizes for", dataName, "field,", \
                    data.GetNumberOfTuples(), "!=", goldData.GetNumberOfTuples(), "\n"
                exit(1)

            # comparison tolerance for this field
            tol = tolerances[dataName]
            maxDiff = 0.0
            dataDiff = False

            # text specific to this data comparison
            compText =  "\n  Comparing " + dataName + "\n"
            compText += "    number of values: " + str(data.GetNumberOfTuples()) + '\n'
            compText += "    tolerance: " + str(tol) + '\n'

            # loop over the points and perform comparison
            # care must be taken to ensure that points with the same global IDs are compared to each other
            goldDataList = deepcopy(goldIDs)
            dataList = deepcopy(IDs)
            for pt in xrange(data.GetNumberOfTuples()):

                # determine the number of components and get the data
                try:
                    numComponents, goldDataTuple, dataTuple = GetDataTuples(pt, goldData, data)
                except Exception, e:
                    print "\n", e, "\n"
                    exit(1)
                for i in range(numComponents):
                    goldDataList[pt].append(goldDataTuple[i])
                    dataList[pt].append(dataTuple[i])

            # sort the lists (they will be sorted by global ID)
            goldDataList.sort()
            dataList.sort()

            # loop over each point
            for pt in xrange(len(goldDataList)):
                # loop over each component of the data
                for i in range(len(goldDataList[pt])-1): # skip the ID, which is the first entry in the list
                    goldVal = goldDataList[pt][i+1]
                    val = dataList[pt][i+1]
                    diff = abs(goldVal - val)
                    if diff > maxDiff:
                        maxDiff = diff
                    if diff > tol or IsInvalid(goldVal) or IsInvalid(val):
                        compText += "TOLERANCE EXCEEDED " # TODO GET GLOBAL IDS AND PRINT THEM
                        compText += str(goldVal) + " != " + str(val)
                        compText +=  ", difference = " + str(diff) + "\n"
                        dataDiff = True
                        filesDiff = True

            compText += "    maximum difference: " + str(maxDiff)
            verboseText += compText
            if dataDiff == True:
                nonVerboseText += compText
                printNonVerboseText = True

        if options.verbose == True:
            print verboseText
        if options.verbose == False and printNonVerboseText == True:
            print nonVerboseText

    returnCode = 0
    if filesDiff == False:
        print "\nFILES MATCH\n"
    else:
        print "\nFILES DIFFER\n"
        returnCode = 1

    exit(returnCode)
