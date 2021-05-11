""" Script to filter MAG's PaperAuthorAffiliations.txt to contain only entries
    concerning papers we want to determine the author's affiliations (i.e. the
    MAG IDs in citing_in_lang_mids_for_filtering.txt."""

target_mids = []
with open('citing_in_lang_mids_for_filtering.txt') as f:
    for line in f:
        target_mids.append(int(line.strip()))

with open('../PaperAuthorAffiliations_filtered.txt', 'w') as fo:
    with open('../PaperAuthorAffiliations.txt') as fi:
        for i, line in enumerate(fi):
            if i%100000 == 0:
                print('{}'.format(i/677802679))
            vals = line.split('\t')
            mid = int(vals[0])
            if mid in target_mids:
                fo.write(line)
