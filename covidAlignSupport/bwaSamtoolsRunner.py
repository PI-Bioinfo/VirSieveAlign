import os
import multiprocessing
try:
    import fileHandling
except ImportError:
    from . import fileHandling

referenceGenomeEnv = os.environ.setdefault("REFGENOME", "/home/biodocker/references/Sars_cov_2.ASM985889v3.dna_sm.toplevel.fa.gz")
bwaExecutable = "/opt/conda/bin/bwa"
samtoolsExecutable = "/usr/bin/samtools"
cpuCount = multiprocessing.cpu_count()


def bwaAlignAndCompress(pe1Reads:str, pe2Reads:str="", outputFilePath:str=None, referenceGenome:str=referenceGenomeEnv): #keep pe2 file defaulting to empty string for proper BWA command
    if not outputFilePath:
        outputFilePath = fileHandling.stripFastqExtensions(pe1Reads) + ".bam"
    bwaCommand = "%s mem -t %s %s %s %s" %(bwaExecutable, cpuCount, referenceGenome, pe1Reads, pe2Reads)
    samtoolsBAMCommand = "%s view -@%s -bS - > %s" %(samtoolsExecutable, cpuCount, outputFilePath)
    fullCommand = "%s | %s" %(bwaCommand, samtoolsBAMCommand)
    print("RUN: %s" %fullCommand)
    exitStatus = os.system(fullCommand)
    if exitStatus != 0:
        raise RuntimeError("Alignment and compression command returned a non-zero exit status.")
    return outputFilePath


def samtoolsSort(inputBAM:str, outputFilePath:str=None):
    if not outputFilePath:
        outputFilePath = inputBAM[:-4] + ".sorted.bam"
    samtoolsSortCommand = "%s sort -@%s %s %s" %(samtoolsExecutable, cpuCount, inputBAM, outputFilePath[:-4]) #samtoolsSort automatically adding bam, fixing with the slice operation
    print("RUN: %s" %samtoolsSortCommand)
    exitStatus = os.system(samtoolsSortCommand)
    if exitStatus != 0:
        raise RuntimeError("BAM sort command returned a non-zero exit status.")
    return outputFilePath


def samtoolsMergeBAMs(inputBAMList:list, outputFilePath:str=None):
    if not inputBAMList:
        raise ValueError("Given an empty list of BAM files to merge.")
    if not outputFilePath:
        outputFilePath = inputBAMList[0].replace(".bam", ".merged.bam")
    inputFileString = " ".join(inputBAMList)
    samtoolsMergeCommand = "%s merge -@%s -f %s %s" %(samtoolsExecutable, cpuCount, outputFilePath, inputFileString)
    print("RUN: %s" %samtoolsMergeCommand)
    exitStatus = os.system(samtoolsMergeCommand)
    if exitStatus != 0:
        raise RuntimeError("Merge command returned a non-zero exit status.")
    return outputFilePath


def samtoolsIndexBAM(inputFilePath:str, outputFilePath:str=None):
    if not outputFilePath:
        outputFilePath = inputFilePath + ".bai"
    samtoolsIndexCommand = "%s index %s %s" % (samtoolsExecutable, inputFilePath, outputFilePath,)
    print("RUN: %s" % samtoolsIndexCommand)
    exitStatus = os.system(samtoolsIndexCommand)
    if exitStatus != 0:
        raise RuntimeError("Index command returned a non-zero exit status.")
    return outputFilePath
