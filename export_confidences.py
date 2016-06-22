#!/usr/bin/env python
import csv
import re
from collections import OrderedDict as od
import argparse


def is_valid_file(parser, arg):
    try:
        return open(arg, 'r')
    except OSError as e:
        parser.error("Cannot open {}. Does it exist and is it readable?".format(arg))

def make_ped_file(snp_list, annot_file, fam_file, conf_file, out_pre):
    """
    The PED file is a white-space (space or tab) delimited file.
    the first six columns are mandatory:
         Family ID
         Individual ID
         Paternal ID
         Maternal ID
         Sex (1=male; 2=female; other=unknown)
         Phenotype
    Genotypes (column 7 onwards) should also be white-space delimited;
    they can be any character (e.g. 1,2,3,4 or A,C,G,T or anything else)
    except 0 which is, by default, the missing genotype character.
    All markers should be biallelic.

    """

    good_snps = set([x.rstrip() for x in snp_list])
    annots = od()
    annot_reader = csv.reader(annot_file, delimiter=",", quotechar='"')
    for row in annot_reader:
        if row[0].startswith('AX-') and row[0] in good_snps:
            # Probe Set ID: [Chromosome,Physical Position,Allele A,Allele B]
            kept_annots = [row[x] for x in [3, 4, 9, 10]]
            kept_annots[0] = kept_annots[0].split('.')[1]
            annots[row[0]] = kept_annots

    fam_dict = od()
    for l in fam_file:
        tmp = l.rstrip().split()
        fam_dict[tmp[1]] = tmp

    kept_samples = []
    sample_names = []
    gts = {}
    gt_reader = csv.reader(conf_file, delimiter="\t")
    for row in gt_reader:
        if not row[0].startswith('#'):
            if row[0] == "Probe Set ID" or row[0] == 'probeset_id':
                for i, ind_tmp in enumerate(row[1:]):
                    ind = re.sub('(\.AxiomGT1\.chp Call Codes)|(\.CEL)', '', ind_tmp)
                    if ind in fam_dict:
                        kept_samples.append(i+1)
                        sample_names.append(ind)
            else:
                if row[0] in annots:
                    gts[row[0]] = [row[x] for x in kept_samples]

    with open('{}.conf'.format(out_pre), 'w') as ped_file:

        for snp_id in annots:
            # transpose genotype matrix
            for ind, gt in zip(sample_names, gts[snp_id]):
                fam_dict[ind].append(gt)

        for ind in fam_dict:
            ped_file.write('\t'.join(fam_dict[ind]) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Convert Affy genotype exports into ped/map files for plink.")
    parser.add_argument("-a", "--annot",
                        help="Annotation file name.", required=True,
                        type=lambda x: is_valid_file(parser, x),
                        dest='annot_fh', metavar="FILE")

    parser.add_argument("-c", "--conf",
                        help="Genotypes confidences file name.", required=True,
                        type=lambda x: is_valid_file(parser, x),
                        dest='conf_fh', metavar="FILE")

    parser.add_argument("-s", "--snplist",
                        help="SNP list file name. (one snp ID per line)",
                        type=lambda x: is_valid_file(parser, x),
                        dest='snp_list_fh', metavar="FILE")

    parser.add_argument('-f', "--famfile",
                        help="PED family file, indicating the invidividuals desired for output.",
                        type=lambda x: is_valid_file(parser, x),
                        dest='fam_fh', metavar="FILE")

    parser.add_argument('-o', "--outname",
                        help="Prefix used for map and ped files. (default: out)",
                        type=str, dest='out_prefix', metavar="PREFIX", default='out')
    args = parser.parse_args()

    make_ped_file(args.snp_list_fh, args.annot_fh, args.fam_fh, args.conf_fh, args.out_prefix)


if __name__ == '__main__':
    main()
