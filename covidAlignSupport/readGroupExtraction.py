import os
import pysam
import json
import typing
try:
    import fileHandling
except ImportError:
    from . import fileHandling


def makeReadGroupFromFastqFileName(fileSet:fileHandling.ReadSet):
    fileName = os.path.split(fileSet.pe1Raw)[1]
    fileBase = fileName.split(".")[0]
    fileSplit = fileBase.split("_")
    if len(fileSplit) < 5:
        readGroupString = "RGPL=Illumina RGLB=LaneX RGPU=NONE RGSM=%s" %fileSplit[0]
    else:
        readGroupString = "RGPL=Illumina RGLB=%s RGPU=NONE RGSM=%s" %(fileSplit[-3], fileSplit[0])
    fileSet.readGroupString = readGroupString
    return readGroupString


def extractReadGroup(fileSet:fileHandling.ReadSet):
    bamFile = pysam.AlignmentFile(fileSet.rawPairedBAM, 'rb')
    header = bamFile.header
    try:
        readGroup = header['RG']
        print("Extracted read group %s from %s" % (readGroup, fileSet.rawPairedBAM))
        fileSet.readGroupString = readGroup
    except KeyError:
        readGroup = makeReadGroupFromFastqFileName(fileSet)
        print("Generated read group %s from %s" %(readGroup, fileSet.pe1Raw))
    finally:
        bamFile.close()
    return readGroup


def saveReadGroups(readSets:typing.Dict[str, fileHandling.ReadSet], outputFolder):
    outputDict = {}
    for fileBase, fileSet in readSets.items():
        outputDict[fileBase] = fileSet.readGroupString
    outputFilePath = os.path.join(outputFolder, "readgroups.json")
    outputFile = open(outputFilePath, 'w')
    json.dump(outputDict, outputFile, indent=4)
    outputFile.close()
    return outputFilePath
