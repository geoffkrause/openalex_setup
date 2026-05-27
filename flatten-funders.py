import csv
import glob
import gzip
import json
import os
import time

SNAPSHOT_DIR = '../openalex-snapshot'
CSV_DIR = '../openalex_csv'

if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

ENTITY = 'funders'

csv_files = {
    'funders': {
        'funders': {
            'name': os.path.join(CSV_DIR, ENTITY, 'funders.csv.gz'),
            'columns': [
                'id', 'display_name', 'country_code',
                'ror', 'crossref', 'doi',
                'works_count', 'cited_by_count', 'updated_date'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY, 'funders_counts_by_year.csv.gz'),
            'columns': ['funder_id', 'year', 'works_count', 'cited_by_count',
                        'oa_works_count']
        },
    },
}



def flatten_funders():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['funders']['name'], 'wt', encoding='utf-8') as funders_csv, \
		gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv:

		funders_writer = init_dict_writer(funders_csv, file_spec['funders'],lineterminator='\n')
		counts_by_year_writer = init_dict_writer(counts_by_year_csv, file_spec['counts_by_year'],lineterminator='\n')
		
		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as funders_jsonl:
				for funder_json in funders_jsonl:
					
					if not funder_json.strip():
						continue
						
					funder = json.loads(funder_json)
					
					if not (funder_id := funder.get('id')):
						continue
					
					funder_id = funder_id[21:]
					funder['id'] = funder_id
					
					if ids := funder.get('ids'):
						funder['ror'] = ids.get('ror')
						funder['crossref'] = ids.get('crossref')
						funder['doi'] = ids.get('doi')
						
					funders_writer.writerow(funder)
										
						
					if counts_by_year := funder.get('counts_by_year'):
						for count_by_year in counts_by_year:
							count_by_year['funder_id'] = funder_id
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
	flatten_funders()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
