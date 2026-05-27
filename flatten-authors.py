import csv
import glob
import gzip
import json
import os
import time

SNAPSHOT_DIR = '../openalex_snapshot'
CSV_DIR = '../openalex_csv'

if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

ENTITY = 'authors'

csv_files = {
    'authors': {
        'authors': {
            'name': os.path.join(CSV_DIR, ENTITY, 'authors.csv.gz'),
            'columns': [
                'id', 'orcid', 'display_name', 'works_count', 'cited_by_count',
                'updated_date'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY, 'authors_counts_by_year.csv.gz'),
            'columns': [
                'author_id', 'year', 'works_count', 'cited_by_count',
                'oa_works_count'
            ]
        },
        'alternative_names': {
            'name': os.path.join(CSV_DIR, ENTITY, 'authors_alternative_names.csv.gz'),
            'columns': [
                'author_id', 'alternative_name'
            ]
        },
        'last_known_institutions': {
            'name': os.path.join(CSV_DIR, ENTITY, 'authors_last_known_institutions.csv.gz'),
            'columns': [
                'author_id', 'institution_id'
            ]
        },
    },
}


def flatten_authors():
    file_spec = csv_files[ENTITY]

    with gzip.open(file_spec['authors']['name'], 'wt',
                   encoding='utf-8') as authors_csv, \
            gzip.open(file_spec['counts_by_year']['name'], 'wt',
                      encoding='utf-8') as counts_by_year_csv, \
            gzip.open(file_spec['alternative_names']['name'], 'wt',
                      encoding='utf-8') as alternative_names_csv, \
            gzip.open(file_spec['last_known_institutions']['name'], 'wt',
                      encoding='utf-8') as last_known_institutions_csv:

        authors_writer = init_dict_writer(authors_csv, file_spec['authors'], lineterminator='\n')
        counts_by_year_writer = init_dict_writer(counts_by_year_csv,
                                              file_spec['counts_by_year'],lineterminator='\n')
        alternative_names_writer = init_dict_writer(alternative_names_csv,
                                              file_spec['alternative_names'],lineterminator='\n')
        last_known_institutions_writer = init_dict_writer(last_known_institutions_csv,
                                              file_spec['last_known_institutions'],lineterminator='\n')

        for jsonl_file_name in glob.glob(
                os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as authors_jsonl:
                for author_json in authors_jsonl:
                    if not author_json.strip():
                        continue

                    author = json.loads(author_json)

                    if not (author_id := author.get('id')):
                        continue
                    
                    author_id = author_id[21:]
                    author['id'] = author_id

                    ##### authors

                    authors_writer.writerow(author)


                    ############ alternative_names
                    for alt_name in author.get('display_name_alternatives'):
                        if alt_name:
                            alternative_names_writer.writerow({
                                'author_id': author_id,
                                'alternative_name': alt_name
                            })
					
					############ last_known_institutions
                    for inst in author.get('last_known_institutions'):
                        if inst_id := inst.get('id'):
                            last_known_institutions_writer.writerow({
                                'author_id': author_id,
                                'institution_id': inst_id[21:],
                            })

					
                    ##### counts_by_year
                    if counts_by_year := author.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['author_id'] = author_id
                            counts_by_year_writer.writerow(count_by_year)


def init_dict_writer(csv_file, file_spec, **kwargs):
    writer = csv.DictWriter(
        csv_file, fieldnames=file_spec['columns'], extrasaction='ignore', **kwargs
    )
    writer.writeheader()
    return writer


if __name__ == '__main__':

	if not os.path.exists(os.path.join(CSV_DIR, ENTITY)):
		os.mkdir(os.path.join(CSV_DIR, ENTITY))

	start = time.time()
	flatten_authors()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
    
