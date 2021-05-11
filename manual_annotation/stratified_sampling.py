import sqlite3
import pandas as pd
import numpy as np
import argparse

def main():

    parser = argparse.ArgumentParser('')
    parser.add_argument("db", help = 'name of database')
    parser.add_argument("num", help='number of samples')
    parser.add_argument("sampling", help='sampling by references or papers')

    db = parser.parse_args().db
    N = int(parser.parse_args().num)
    sampling = parser.parse_args().sampling

    conn = sqlite3.connect(db)

    if sampling == 'papers':
        sample_papers(conn, N)
        print("Success! Your file's name is samples.csv")
    elif sampling == 'refs':
        sample_references(conn, N)
        print("Success! Your file's name is samples.csv")
    else:
        print("Please enter one of the following sampling : papers or refs.")



def sample_papers(conn, N):

    df = pd.read_sql_query("SELECT * from arxivmetadata", conn)
    df['month_year'] = df.date.apply(lambda x: x[:7])

    samples = stratified_sampling(df, N)
    refs = samples.arxiv_id.to_numpy()

    query = f"SELECT * FROM bibitem WHERE citing_arxiv_id in ({','.join(['?']*len(refs))})"
    df_ref = pd.read_sql_query(query, conn, params = refs)
    conn.close()

    refs_result = pd.merge(df_ref, samples, how = 'inner', left_on = 'citing_arxiv_id', right_on = 'arxiv_id').drop(columns='arxiv_id')
    refs_result.to_csv('samples.csv', index=False)

def sample_references(conn, N):
    papers = pd.read_sql_query("SELECT * from arxivmetadata", conn)
    papers['month_year'] = papers.date.apply(lambda x: x[:7])

    query = f"SELECT * FROM bibitem"
    refs = pd.read_sql_query(query, conn)
    conn.close()
    papers_refs = pd.merge(papers, refs, how = 'right',left_on='arxiv_id', right_on='citing_arxiv_id').drop(columns='arxiv_id')
    samples = stratified_sampling(papers_refs, N)
    samples.to_csv('samples.csv', index=False)



def stratified_sampling(df, N):

    strata = ['discipline', 'month_year']

    group1 = df.groupby(strata,group_keys=False).count().reset_index()

    first = df.groupby(strata, group_keys=False).apply(lambda x: x.sample(int(np.rint(N*len(x)/len(df))))).sample(frac=1).reset_index(drop=True)
    rest = N - len(first)

    group2 = first.groupby(strata, group_keys=False).count().reset_index()

    df3 = pd.merge(group1,group2, how='left', on = strata, indicator='Exist')
    df3 = df3[df3['Exist'] != 'both'].sort_values(by='date_x', ascending=False)[strata][:rest]
    mrgd = pd.merge(df, df3, how='inner')

    second = mrgd.groupby(strata, group_keys=False).apply(lambda x: x.sample(1)).sample(frac=1).reset_index(drop=True)

    result = pd.concat([first,second], ignore_index=True).drop(columns = ['month_year'])

    return result

if __name__ == "__main__":
    main()
