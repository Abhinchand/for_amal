from Bio import Entrez
from Bio import SeqIO
from urllib.error import HTTPError


# used by biopython for NCBI access
Entrez.email = "admin@bpprc.org"


def _ncbi_domain_extract(accession):
    """
    extract ncbi domain details for individual proteins


    """
    Endotoxin_N, Endotoxin_N_start, Endotoxin_N_end, Endotoxin_M, Endotoxin_M_start, Endotoxin_M_end, Endotoxin_C, Endotoxin_C_start, Endotoxin_C_end = [
        ""] * 9
    no_ncbi = True
    try:
        with Entrez.efetch(db="protein", rettype="gb", retmode="text", id=accession) as handle:
            for seq_record in SeqIO.parse(handle, "gb"):
                try:
                    Endotoxin_N = seq_record.features[1].qualifiers['region_name'][0]
                    print(type(seq_record.features[1].location.start))
                    Endotoxin_N_start = seq_record.features[1].location.start
                    Endotoxin_N_end = seq_record.features[1].location.end
                except:
                    pass

                try:
                    Endotoxin_M = seq_record.features[2].qualifiers['region_name'][0]
                    Endotoxin_M_start = seq_record.features[2].location.start
                    Endotoxin_M_end = seq_record.features[2].location.end
                except:
                    pass

                try:
                    Endotoxin_C = seq_record.features[3].qualifiers['region_name'][0]
                    Endotoxin_C_start = seq_record.features[3].location.start
                    Endotoxin_C_end = seq_record.features[3].location.end
                except:
                    pass
    except HTTPError as err:
        try:
            if err.code == 404:
                no_ncbi = False
            else:
                raise
        except HTTPError as err:
            print(err.code)

    if no_ncbi:
        return Endotoxin_N, Endotoxin_N_start, Endotoxin_N_end, Endotoxin_M, Endotoxin_M_start, Endotoxin_M_end, Endotoxin_C, Endotoxin_C_start, Endotoxin_C_end
    else:
        return None
