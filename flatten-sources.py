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

ENTITY = 'sources'

csv_files = {
    'sources': {
        'sources': {
            'name': os.path.join(CSV_DIR, ENTITY, 'sources.csv.gz'),
            'columns': [
                'id', 'issn_l', 'display_name', 'type', 'host_organization', 'country_code',
                'is_oa', 'is_in_doaj', 'is_in_scielo', 'is_ojs',
                'first_publication_year', 'last_publication_year', 'oa_flip_year',
                'works_count', 'cited_by_count', 'updated_date'
            ]
        },
        'issns': {
            'name': os.path.join(CSV_DIR, ENTITY, 'sources_issns.csv.gz'),
            'columns': ['source_id', 'issn']
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY, 'sources_counts_by_year.csv.gz'),
            'columns': ['source_id', 'year', 'works_count', 'cited_by_count',
                        'oa_works_count']
        },
    },
}



def flatten_sources():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['sources']['name'], 'wt', encoding='utf-8') as sources_csv, \
		gzip.open(file_spec['issns']['name'], 'wt', encoding='utf-8') as issns_csv, \
		gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv:

		sources_writer = init_dict_writer(sources_csv, file_spec['sources'],lineterminator='\n')
		issns_writer = init_dict_writer(issns_csv, file_spec['issns'],lineterminator='\n')
		counts_by_year_writer = init_dict_writer(counts_by_year_csv, file_spec['counts_by_year'],lineterminator='\n')
		
		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as sources_jsonl:
				for source_json in sources_jsonl:
					
					if not source_json.strip():
						continue
						
					source = json.loads(source_json)
					
					if not (source_id := source.get('id')):
						continue
					
					source_id = source_id[21:]
					source['id'] = source_id
					
					if host_organization := source.get('host_organization'):
						source['host_organization'] = host_organization[21:]
						
					#source['issn'] = json.dumps(source.get('issn'))
					sources_writer.writerow(source)
					
					if issns := source.get('issn'):
						for issn in issns:
							issns_writer.writerow(
								{'source_id':source_id, 'issn':issn}
							)
					
					#if source_ids := source.get('ids'):
					#	source_ids['source_id'] = source_id
					#	source_ids['issn'] = json.dumps(source_ids.get('issn'))
					#	ids_writer.writerow(source_ids)
						
					if counts_by_year := source.get('counts_by_year'):
						for count_by_year in counts_by_year:
							count_by_year['source_id'] = source_id
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
	flatten_sources()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
