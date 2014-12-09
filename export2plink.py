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


def translate(annot, gt_row):
    t_gts = []
    # annot is [chrom, bp, alleleA, alleleB]
    a = annot[2]
    b = annot[3]
    trans = {'0' : a + ' ' + a, '1' : a + ' ' + b, '2' : b + ' ' + b, '-1'    : '0 0',
             'AA': a + ' ' + a, 'AB': a + ' ' + b, 'BB': b + ' ' + b, 'NoCall': '0 0'}
    for gt in gt_row:
        t_gts.append(trans[gt])
    return t_gts


def make_ped_file(snp_list, annot_file, pop_file, gt_file, out_pre):
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

    The MAP file describes a single marker and must contain exactly 4 columns:
         chromosome (1-22, X, Y or 0 if unplaced)
         rs# or snp identifier
         Genetic distance (morgans)
         Base-pair position (bp units)
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

    pops = od()
    for l in pop_file:
        tmp = l.rstrip().split('\t')
        pops[tmp[0]] = tmp[1]

    kept_samples = []
    sample_names = []
    gts = {}
    gt_reader = csv.reader(gt_file, delimiter="\t")
    for row in gt_reader:
        if not row[0].startswith('#'):
            if row[0] == "Probe Set ID" or row[0] == 'probeset_id':
                for i, ind_tmp in enumerate(row[1:]):
                    ind = re.sub('(\.AxiomGT1\.chp Call Codes)|(\.CEL)', '', ind_tmp)
                    if ind in pops:
                        kept_samples.append(i+1)
                        sample_names.append(ind)
            else:
                if row[0] in annots:
                    gts[row[0]] = translate(annots[row[0]], [row[x] for x in kept_samples])

    with open('{}.ped'.format(out_pre), 'w') as ped_file, open('{}.map'.format(out_pre), 'w') as map_file:
        ped_dict = dict(zip(sample_names, [[pops[x].replace(' ', '_'), x, '0', '0', '0', '0'] for x in sample_names]))

        for snp_id in annots:
            chrom = annots[snp_id][0]
            bp = annots[snp_id][1]
            map_file.write('\t'.join(['SC1.{}'.format(chrom), snp_id, '0', bp]) + '\n')

            # transpose genotype matrix
            for ind, gt in zip(sample_names, gts[snp_id]):
                ped_dict[ind].append(gt)

        for ind in sample_names:
            ped_file.write('\t'.join(ped_dict[ind]) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Convert Affy genotype exports into ped/map files for plink.")
    parser.add_argument("-a", "--annot",
                        help="Annotation file name.", required=True,
                        type=lambda x: is_valid_file(parser, x),
                        dest='annot_fh', metavar="FILE")

    parser.add_argument("-g", "--geno",
                        help="Genotypes export file name.", required=True,
                        type=lambda x: is_valid_file(parser, x),
                        dest='geno_fh', metavar="FILE")

    parser.add_argument("-s", "--snplist",
                        help="SNP list file name. (one snp ID per line)",
                        type=lambda x: is_valid_file(parser, x),
                        dest='snp_list_fh', metavar="FILE")

    parser.add_argument('-p', "--popfile",
                        help="Populations file name.",
                        type=lambda x: is_valid_file(parser, x),
                        dest='pop_fh', metavar="FILE")

    parser.add_argument('-o', "--outname",
                        help="Prefix used for map and ped files. (default: out)",
                        type=str, dest='out_prefix', metavar="PREFIX", default='out')
    args = parser.parse_args()

    make_ped_file(args.snp_list_fh, args.annot_fh, args.pop_fh, args.geno_fh, args.out_prefix)


if __name__ == '__main__':
    main()