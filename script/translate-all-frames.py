# Copyright (c) 2016. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse


import varlens
import varlens.reads_util
import skbio
from pysam import AlignmentFile

from isovar import gather_variant_reads, sequence_counts

parser = argparse.ArgumentParser()

parser.add_argument(
    "--vcf",
    default="/Users/iskander/code/varlens/test/data/CELSR1/vcfs/vcf_1.vcf")

parser.add_argument(
    "--bam",
    default="/Users/iskander/code/varlens/test/data/CELSR1/bams/bam_1.bam")

parser.add_argument(
    "--genome",
    default="hg19")

parser.add_argument(
    "--min-weight", type=float, default=3.0)

if __name__ == "__main__":
    args = parser.parse_args()
    variants_df = varlens.variants_util.load_as_dataframe(
        args.vcf,
        genome=args.genome)
    print(variants_df)

    samfile = AlignmentFile(args.bam)

    variant_to_locus_dict = {}
    for variant in variants_df["variant"]:
        print(variant)
        variant_reads = gather_variant_reads(
            samfile=samfile,
            chromosome="chr" + variant.contig,
            base1_location=variant.start,
            ref=variant.ref,
            alt=variant.alt)
        if len(variant_reads) == 0:
            continue
        result = sequence_counts(variant_reads)
        for ((prefix, suffix), weight) in sorted(
                result.sequence_weights.items(),
                key=lambda x: -x[1]):
            if weight < args.min_weight:
                continue

            variant = result.variant_nucleotides
            print("\t%s|%s|%s: %f" % (
                prefix,
                variant,
                suffix,
                weight))

            # translate in three reading frames:
            seq = "%s%s%s" % (prefix, variant, suffix)
            for offset in range(3):
                dna = skbio.DNA(seq[offset:])
                print("\t\tframe=%d: %s" % (offset, dna.translate()))
