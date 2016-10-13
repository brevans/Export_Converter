Export_Converter
================
A utility to convert Affy Genotyping Console 4 export files for Axiom_aegypti1 into more useful data files

Table of Contents
=================

  * [Intro](#intro)
  * [Requirements](#requirements)
  * [Setup](#setup)
  * [Genotyping](#genotyping)
  * [Converting to ped file](#converting-to-ped-file)
    * [Getting Started](#getting-started)
      * [Annotation file](#annotation-file)
      * [Genotypes file](#genotypes-file)
      * [SNP list file](#snp-list-file)
      * [Fam file](#fam-file)

#Intro
While working on the [Axiom_aegypti1](http://g3journal.org/cgi/doi/10.1534/g3.114.016196) Affymetrix SNP chip, I wanted to get data out of the affy software in a simple and flexible way into standard genetics file formats. Here I'll try to guide you through getting set up and generating useable genotypes for new DNA samples run on the chip. There is a new piece of software that Affy offers called ["Axiom Analysis Suite"](http://www.affymetrix.com/estore/catalog/prod920001/AFFY/Axiom%26%23153%3B+Analysis+Suite#1_1) that natively outputs [vcf files](https://en.wikipedia.org/wiki/Variant_Call_Format) (and makes most of this redundant), but I haven't gotten it working with this custom chip. They say it should though, so give it a try if you want!

#Requirements
Note: The genotyping software is windows only, but most everything else can be done anywhere you have an internet connection and python installed.

 1. [Affymetrix Genotyping Console](http://www.affymetrix.com/estore/browse/level_seven_software_products_only.jsp?productId=131535#1_1) (I used v4.2)
 2. excel or other xls reader
 3. Python3: either the [official distribution](https://www.python.org/downloads/), or my favorite, [anaconda python](https://www.continuum.io/downloads).
	 1. [pandas](http://pandas.pydata.org/) if you want to be able to make fam files with `make_fam.py`. It comes standard in the anaconda distribution.
 4. [plink2](https://www.cog-genomics.org/plink2) for playing with your data output

#Setup
*NOTE to powell lab people: This should all be done for you. If not, send an email and a beer to me and we can get it set up again.*

On your favorite windows computer, download [Affymetrix Genotyping Console](http://www.affymetrix.com/estore/browse/level_seven_software_products_only.jsp?productId=131535#1_1) and install. Affy instructions for this are [here](http://media.affymetrix.com/support/technical/other/readme_genotyping_console_4_2.pdf), and the software does come with a lengthy manual. I'll try and walk you through bare-bones getting it up and running, but if you plan on using the software more, you should [RTFM](https://en.wikipedia.org/wiki/RTFM).

- Create a new user profile:

![setup1](/img/setup1.png?raw=true "setup1")

- It will complain that you haven't got a library path specified. Choose a location, either somewhere with your data or in a documents folder. We'll need to add custom library files to this folder in a minute.
- Give it a temp directory location either on a different local drive or on your C drive, don't use a network drive.
- Once it asks about workspaces, close the Genotyping Console. Navigate to the folder you chose as your library folder. It should have a hundred files or so all having to do with the standard affy snp chips. They should look like this:

![setup2](/img/setup2.png?raw=true "setup2")

- Download the library files from our [box.com account](https://yale.box.com/shared/static/iiz90k0c57iamljcsclsxq2lvcmeg6ws.zip), or request them from Affy. Put all these files in the library folder.

![setup3](/img/setup3.png?raw=true "setup3")

- Fire back up Genotyping Console. Chose your profile, and create a new workspace. This file is like the table of contents and does *not* contain any actual data. Once you get to the create new dataset dialogue, you should see "Axiom_aegypti1" as an option. If not, go back and try again.

![setup4](/img/setup4.png?raw=true "setup4")

- Hooray! You're all set up. Included in this repo in the [`/resources/evansetal2015_chip_data`](/resources/evansetal2015_chip_data) directory there are all the samples used in the original manuscript if you'd like to include those for reference. Now dump some .arr and .cel files into a folder where you have some space and import them all at once (this may take some time for a large number of files):

![setup5](/img/setup5.png?raw=true "setup5")

#Genotyping
Note: 
TODO

#Converting to ped file
Now, to get things into a format that we can use! I currently prefer [ped files](http://pngu.mgh.harvard.edu/~purcell/plink/data.shtml#ped) for their ease of use with plink2 and for their explicit use of a family ID, which can be used to indicate sampling location or population. Hopefully, in the future vcf aware tools will adopt a more standard way to do this.

##Getting Started
In order to run the script `export2plink.py`, you'll need a few files.

###Annotation file

The annotation file that affy maintains for this chip. I have included it in this repo as [`CsvAnnotationFile.v1.sorted.csv`](/resources/CsvAnnotationFile.v1.sorted.csv?raw=true) with one major difference. Here I have position and supercontig sorted the loci to make downstream analyses easier.

###Genotypes file

Go to the directory that you chose as output during the genotyping process. There should be a file there called `AxiomGT1.calls.txt`. This file contains all the genotypes we are after, as well as some logged info about the genotyping run.

###SNP list file

A list of snp IDs, one per line, indicating the SNPs you would like to be output from the dataset. I've included 3 lists in this repo for you to chose between, though feel free to modify or add to them as needed.

 * [`all_snps.txt`](/resources/all_snps.txt?raw=true): All 50,000 SNPs from the original design. Not recommended, especially since ped files do not include confidence information about each base called
 * [`evansetal2015_snps.txt`](/resources/evansetal2015_snps.txt?raw=true): The 25,590 loci that passed QC and Mendel tests from the manuscript describing the chip.
 * [`mendel9_snps.txt`](/resources/mendel9_snps.txt?raw=true): I re-ran the same QC and mendel tests from the manuscript describing the chip with basecalls generated using clustering of more individuals (after having run the first 9 chips). This is the SNP list I typically use to start.

###Fam file

This is a file, in the [plink fam format](https://www.cog-genomics.org/plink2/formats#fam), that you'll use to specify the individuals you want in the output file and their metadata. The official spec is:

A text file with no header line, and one line per sample with the following six fields:

 1. Family ID ('FID')
 2. Within-family ID ('IID'; cannot be '0')
 3. Within-family ID of father ('0' if father isn't in dataset)
 4. Within-family ID of mother ('0' if mother isn't in dataset)
 5. Sex code ('1' = male, '2' = female, '0' = unknown)
 6. Phenotype value ('1' = control, '2' = case, '-9'/'0'/non-numeric = missing data if case/control)

I use the FID field to specify populations or groupings convenient to analyses, and encourage you to do so as well.

##Using `export2plink.py`

If you call export2plink.py, you should get a usage message like this:

`usage: export2plink.py [-h] -a FILE -g FILE [-s FILE] [-f FILE] [-o PREFIX]`

And typing `export2plink.py -h` will give you a help message with more descriptions for the options. 

An example, outputting genotypes from the wild sample data would look something like this:

`export2plink.py -a resources/CsvAnnotationFile -g /path/to/AxiomGT1.calls.txt -s resources/evansetal2015_snps.txt -f resources/evansetal2015.fam -o reference_dataset`

If successful, it should generate a `reference_dataset.ped` and `reference_dataset.fam` file in your current directory. Hooray!
