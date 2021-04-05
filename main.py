import covidAlignSupport
import os
import typing


workingFolderEnv = os.environ.setdefault("WORKINGFOLDER", "/data")
if not os.path.isdir(workingFolderEnv):
    raise NotADirectoryError("Unable to find working directory at %s" %workingFolderEnv)
inputFolderEnv = os.environ.setdefault("INPUTFOLDER", os.path.join(workingFolderEnv, "rawFASTQ"))
if not os.path.isdir(inputFolderEnv):
    raise NotADirectoryError("Unable to find raw FASTQ input folder at %s" %inputFolderEnv)
adapterFileEnv = os.environ.setdefault("ADAPTERS", os.path.join(inputFolderEnv, "adapters.fa"))
if not os.path.isfile(adapterFileEnv):
    adapterFileEnv = None
processedReadsFolderEnv = os.environ.setdefault("PROCESSEDREADFOLDER", os.path.join(workingFolderEnv, "processedFASTQ"))
if not os.path.isdir(processedReadsFolderEnv):
    os.mkdir(processedReadsFolderEnv)
rawBAMFolderEnv = os.environ.setdefault("RAWBAMFOLDER", os.path.join(workingFolderEnv, "rawBAM"))
if not os.path.isdir(rawBAMFolderEnv):
    os.mkdir(rawBAMFolderEnv)
mergedBAMFolderEnv = os.environ.setdefault("MERGEDBAMFOLDER", os.path.join(workingFolderEnv, "mergedBAM"))
if not os.path.isdir(mergedBAMFolderEnv):
    os.mkdir(mergedBAMFolderEnv)


def performAdapterTrimming(fileSet:covidAlignSupport.fileHandling.ReadSet, outputFolder:str=processedReadsFolderEnv, adapterFile:str=adapterFileEnv, useCutadapt:bool=False):
    if useCutadapt:
        trimWrapper = covidAlignSupport.cutadaptRunner.runCutadapt
        trimmer = "Cutadapt"
    else:
        trimWrapper = covidAlignSupport.scytheRunner.runScythe
        trimmer = "Scythe"
    print("Adapter trimming %s with %s" %(fileSet.pe1Raw, trimmer))
    pe1AdapterTrim = trimWrapper(fileSet.pe1Raw, outputFolder, adapterFile)
    if not pe1AdapterTrim:
        fileSet.pe1AdapterTrim = fileSet.pe1Raw
    else:
        fileSet.pe1AdapterTrim = pe1AdapterTrim
    if fileSet.isPaired:
        print("Adapter trimming %s with %s" %(fileSet.pe2Raw, trimmer))
        pe2AdapterTrim = trimWrapper(fileSet.pe2Raw, outputFolder, adapterFile)
        if not pe2AdapterTrim:
            fileSet.pe2AdapterTrim = fileSet.pe2Raw
        else:
            fileSet.pe2AdapterTrim = pe2AdapterTrim


def performQualityTrimming(fileSet:covidAlignSupport.fileHandling.ReadSet, outputFolder:str=processedReadsFolderEnv):
    if fileSet.isPaired:
        print("Quality trimming %s and %s jointly" %(fileSet.pe1AdapterTrim, fileSet.pe2AdapterTrim))
        fileSet.pe1QualTrim, fileSet.pe2QualTrim, fileSet.singletonQualTrim = covidAlignSupport.sickleRunner.runSicklePaired(fileSet.pe1AdapterTrim, fileSet.pe2AdapterTrim, outputFolder)
    else:
        fileSet.pe1QualTrim = covidAlignSupport.sickleRunner.runSickleSingle(fileSet.pe1AdapterTrim, outputFolder)


def performAlignmentAndSort(fileSet:covidAlignSupport.fileHandling.ReadSet, outputNameBase:str, outputFolder:str=rawBAMFolderEnv):
    if fileSet.isPaired:
        print("Aligning and sorting %s" %outputNameBase)
        pairedAlignmentFileName = outputNameBase + ".paired.bam"
        pairedAlignmentPath = os.path.join(outputFolder, pairedAlignmentFileName)
        pairedAlignmentPath = covidAlignSupport.bwaSamtoolsRunner.bwaAlignAndCompress(fileSet.pe1QualTrim, fileSet.pe2QualTrim, pairedAlignmentPath)
        fileSet.rawPairedBAM = pairedAlignmentPath
        sortedAlignmentFileName = outputNameBase + ".paired.sorted.bam"
        sortedAlignmentFilePath = os.path.join(outputFolder, sortedAlignmentFileName)
        sortedAlignmentPath = covidAlignSupport.bwaSamtoolsRunner.samtoolsSort(pairedAlignmentPath, sortedAlignmentFilePath)
        fileSet.sortedPairedBAM = sortedAlignmentPath
        singletonAlignmentFileName = outputNameBase + ".single.bam"
        singletonAlignmentFilePath = os.path.join(outputFolder, singletonAlignmentFileName)
        singletonAlignmentPath = covidAlignSupport.bwaSamtoolsRunner.bwaAlignAndCompress(fileSet.singletonQualTrim, outputFilePath=singletonAlignmentFilePath)
        fileSet.rawSingleBAM = singletonAlignmentPath
        singletonSortedFileName = outputNameBase + ".single.sorted.bam"
        singletonSortedFilePath = os.path.join(outputFolder, singletonSortedFileName)
        singletonSortedPath = covidAlignSupport.bwaSamtoolsRunner.samtoolsSort(singletonAlignmentPath, singletonSortedFilePath)
        fileSet.sortedSingleBAM = singletonSortedPath
    else:
        print("Aligning and sorting %s" %outputNameBase)
        alignmentFileName = outputNameBase + ".bam"
        alignmentFilePath = os.path.join(outputFolder, alignmentFileName)
        alignmentPath = covidAlignSupport.bwaSamtoolsRunner.bwaAlignAndCompress(fileSet.singletonQualTrim, outputFilePath=alignmentFilePath)
        fileSet.rawPairedBAM = alignmentPath
        sortedAlignmentFileName = outputNameBase + ".sorted.bam"
        sortedAlignmentFilePath = os.path.join(outputFolder, sortedAlignmentFileName)
        sortedAlignmentPath = covidAlignSupport.bwaSamtoolsRunner.samtoolsSort(alignmentPath, sortedAlignmentFilePath)
        fileSet.sortedSingleBAM = sortedAlignmentPath
        fileSet.mergedBAM = sortedAlignmentPath


def mergeMoveAndIndexBAMs(fileSet:covidAlignSupport.fileHandling.ReadSet, outputNameBase:str, outputFolder:str=mergedBAMFolderEnv, moveSingleEndToFolder:bool=True):
    if fileSet.isPaired:
        print("Merging and indexing %s" %outputNameBase)
        mergedBAMFileName = outputNameBase + ".merged.bam"
        mergedBAMFilePath = os.path.join(outputFolder, mergedBAMFileName)
        filesToMerge = [fileSet.sortedPairedBAM, fileSet.sortedSingleBAM]
        outputFilePath = covidAlignSupport.bwaSamtoolsRunner.samtoolsMergeBAMs(filesToMerge, mergedBAMFilePath)
        fileSet.mergedBAM = outputFilePath
    else:
        if moveSingleEndToFolder:
            print("%s is unpaired and being moved to the final folder" %outputNameBase)
            fileName = os.path.split(fileSet.sortedBAM)[1]
            outputFilePath = os.path.join(outputFolder, fileName)
            os.rename(fileSet.sortedBAM, outputFilePath)
        else:
            outputFilePath = fileSet.sortedBAM
    fileSet.finalBAM = outputFilePath
    fileSet.finalBAMIndex = covidAlignSupport.bwaSamtoolsRunner.samtoolsIndexBAM(outputFilePath)


def harvestReadGroup(fileSet:covidAlignSupport.fileHandling.ReadSet):
    readGroupString = covidAlignSupport.readGroupExtraction.extractReadGroup(fileSet)
    return readGroupString


def saveReadGroups(fileSets:typing.Dict[str, covidAlignSupport.fileHandling.ReadSet], outputFolder:str=rawBAMFolderEnv):
    readGroupFilePath = covidAlignSupport.readGroupExtraction.saveReadGroups(fileSets, outputFolder)
    return readGroupFilePath


def processInputFolder(inputFolder:str=inputFolderEnv):
    fileSets = covidAlignSupport.fileHandling.groupFastqsFromFolder(inputFolder)
    for fileGroupName, fileSet in fileSets.items():
        print("Processing %s" %fileGroupName)
        performAdapterTrimming(fileSet)
        performQualityTrimming(fileSet)
        performAlignmentAndSort(fileSet, fileGroupName)
        harvestReadGroup(fileSet)
        mergeMoveAndIndexBAMs(fileSet, fileGroupName)
        print("Successfully processed %s" %fileGroupName)
    saveReadGroups(fileSets)
    return fileSets


if __name__ == "__main__":
    processInputFolder()
