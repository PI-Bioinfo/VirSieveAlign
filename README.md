# COVID Aligner

## Summary

This container is part of the Environmental Viral Detection pipeline and covers the pre-processing of raw reads and alignment as well as some post-alignment BAM file organization steps.  This portion of the pipeline centers around Sickle and Scythe for trimming adapter contamination and bad quality sequence as well as BWA in MEM mode for alignment of short reads to the viral reference genome.  The output of this pipeline will be merged BAM files aligned from the supplied raw reads.

**SECURITY CONCERN**: This pipeline is currently using os.system to run commands and sanitization was causing runs to fail. If running files from untrusted sources, please be sure to sanitize file names to prevent potential command injections into the container.

### File naming and structure
The simplest way to run this pipeline is to set up a working directory where all of the subsequent files and folders will be created.  In this folder, create a folder called **rawFASTQ** where you can put your paired and unpaired raw reads.  File naming should follow the standard Illumina scheme where they will look something like this: **sample-name_S6_L001_R1_001.fastq.gz**.  Please avoid the use of dots and underscores in your sample names, as those characters are used to identify the created files during processing.  FASTQ files should all end with _.fastq_ or _.fq_ unless gzip compressed in which case they should end with _fastq.gz_ or _fq.gz_.  For adapter trimming to take place, include a FASTA-formatted file named **adapters.fa** in the rawFASTQ folder.

### Running the container
To run this container (presumed to be named _covidalign_ here), simply use the following command:
```bash
docker container run --rm -v /path/to/working/folder:/data covidalign
```

### Setting non-default options
Some options can be set to non-default values by passing them into the container as environmental variables using the standard Docker commandline technique for setting environmental variables as follows:

| Variable        | Type           | Default  | Description |
| --------------- |:--------------:|:--------:|-------------|
WORKINGFOLDER | string | /data | Working folder name within the container
INPUTFOLDER | string | /$WORKINGFOLDER/rawFASTQ | The name of the raw sequence folder within the working folder
ADAPTERS | string | /$WORKINGFOLDER/$INPUTFOLDER/adapters.fa | The fasta file with the adapter sequences for trimming
PROCESSEDREADFOLDER | string | /$WORKINGFOLDER/processedFASTQ | The name of the folder for processed, unaligned reads
RAWBAMFOLDER | string | /$WORKINGFOLDER/rawBAM | The name of the folder for the initial alignment files
MERGEDBAMFOLDER | string | /$WORKINGFOLDER/mergedBAM | The name of the folder for the processed alignment files
REFGENOME | string | /home/biodocker/references/Sars_cov_2.ASM985889v3.dna_sm.toplevel.fa.gz | Path to the BWA-indexed reference genome (the default reference genome is indexed on container build for efficiency)


## Contributing

We welcome and encourage contributions to this project from the microbiomics community and will happily accept and acknowledge input (and possibly provide some free kits as a thank you).  We aim to provide a positive and inclusive environment for contributors that is free of any harassment or excessively harsh criticism. Our Golden Rule: *Treat others as you would like to be treated*.

## Versioning

We use a modification of [Semantic Versioning](https://semvar.org) to identify our releases.

Release identifiers will be *major.minor.patch*

Major release: Newly required parameter or other change that is not entirely backwards compatible
Minor release: New optional parameter
Patch release: No changes to parameters

## Authors

- **Michael M. Weinstein** - *Project Lead, Programming and Design* - [michael-weinstein](https://github.com/michael-weinstein)


See also the list of [contributors](https://github.com/Zymo-Research/figaro/contributors) who participated in this project.

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details.
This license restricts the usage of this application for non-open sourced systems. Please contact the authors for questions related to relicensing of this software in non-open sourced systems.

## Acknowledgments

We would like to thank the following, without whom this would not have happened:
* The Python Foundation
* The staff at Zymo Research
* The scientific and public health COVID response community
* Our customers


