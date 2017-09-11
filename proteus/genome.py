"""This class wraps the indexed FASTA file for an organism's genomic sequence.
It supports retrieving parts of the sequence and converting these parts
into their one hot encodings.
"""
import numpy as np
from pyfaidx import Fasta


class Genome(object):

    BASES = np.array(['A', 'C', 'G', 'T'])

    def __init__(self, fa_file):
        """Wrapper class around the pyfaix.Fasta class.

        Parameters
        ----------
        fa_file : str
            Path to an indexed FASTA file, that is, a *.fasta file with a
            corresponding *.fai file in the same directory.
            File should contain the target organism's genome sequence.

        Attributes
        ----------
        genome : Fasta
        chrs : list[str]
        len_chrs : dict
            The length of each chromosome sequence in the file.
        """
        self.genome = Fasta(fa_file)
        self.chrs = sorted(self.genome.keys())
        self.len_chrs = self._get_len_chrs()

    def _get_len_chrs(self):
        """Gets the length of each chromosome sequence in the file.
        `self.len_chrs` is used for quick lookup of this information
        during sampling.
        """
        len_chrs = {}
        for chrom in self.chrs:
            len_chrs[chrom] = len(self.genome[chrom])
        return len_chrs

    def get_sequence_from_coords(self, chrom, start, end, strand='+'):
        """Gets the genomic sequence given the chromosome, sequence start,
        sequence end, and strand side.

        Parameters
        ----------
        chrom : str
            e.g. "chr1".
        start : int
        end : int
        strand : {'+', '-'}, optional
            Default is '+'.

        Returns
        -------
        str
            The genomic sequence.

        Raises
        ------
        ValueError
            If the input char to `strand` is not one of the specified choices.
        """
        if start >= len(self.genome[chrom]) or end >= len(self.genome[chrom]) \
                or start < 0:
            return ""

        if strand == '+':
            return self.genome[chrom][start:end].seq
        elif strand == '-':
            return self.genome[chrom][start:end].reverse.complement.seq
        else:
            raise ValueError(
                "Strand must be one of '+' or '-'. Input was {0}".format(
                    strand))

    def get_encoding_from_coords(self, chrom, start, end, strand='+'):
        """Gets the genomic sequence given the chromosome, sequence start,
        sequence end, and strand side; and return its one hot encoding.

        Parameters
        ----------
        chrom : str
            e.g. "chr1".
        start : int
        end : int
        strand : {'+', '-'}, optional
            Default is '+'.

        Returns
        -------
        numpy.ndarray, dtype=bool
            The N-by-4 encoding of the sequence.

        Raises
        ------
        ValueError
            If the input char to `strand` is not one of the specified choices.
            (Raised in the call to `self.get_sequence_from_coords`)
        """
        sequence = self.get_sequence_from_coords(chrom, start, end, strand)
        return self.sequence_encoding(sequence)

    def sequence_encoding(self, sequence):
        """Converts an input sequence to its one hot encoding.

        Parameters
        ----------
        sequence : str
            The input sequence of length N.

        Returns
        -------
        numpy.ndarray, dtype=bool
            The N-by-4 encoding of the sequence.
        """
        encoding = np.zeros((len(sequence), 4), np.bool_)
        for base, index in zip(sequence, range(len(sequence))):
            encoding[index, :] = self.BASES == base
        return encoding
