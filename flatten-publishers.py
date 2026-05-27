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

ENTITY = 'publishers'

csv_files = {
    'publishers': {
        'publishers': {
            'name': os.path.join(CSV_DIR, ENTITY, 'publishers.csv.gz'),
            'columns': [
                'id', 'display_name', 'country_codes',
                'hierarchy_level', 'parent_publisher_id',
                'works_count', 'cited_by_count', 'updated_date'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY,'publishers_counts_by_year.csv.gz'),
            'columns': ['publisher_id', 'year', 'works_count', 'cited_by_count',
                        'oa_works_count']
        },
        'funder_roles': {
            'name': os.path.join(CSV_DIR, ENTITY,'publishers_funder_roles.csv.gz'),
            'columns': ['publisher_id', 'funder_id']
        },
    },
}



def flatten_publishers():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['publishers']['name'], 'wt', encoding='utf-8') as publishers_csv, \
		gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv, \
		gzip.open(file_spec['funder_roles']['name'], 'wt', encoding='utf-8') as roles_csv:

		publishers_writer = init_dict_writer(publishers_csv, file_spec['publishers'],lineterminator='\n')
		counts_by_year_writer = init_dict_writer(counts_by_year_csv, file_spec['counts_by_year'],lineterminator='\n')
		roles_writer = init_dict_writer(roles_csv, file_spec['funder_roles'],lineterminator='\n')
		
		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as publishers_jsonl:
				for publisher_json in publishers_jsonl:
					
					if not publisher_json.strip():
						continue
						
					publisher = json.loads(publisher_json)
					
					if not (publisher_id := publisher.get('id')):
						continue
					
					publisher_id = publisher_id[21:]
					publisher['id'] = publisher_id
					
					if parent := publisher.get('parent_publisher'):
						if parent.get('id'):
							publisher['parent_publisher_id'] = parent.get('id')[21:]
							
					if countries := publisher.get('country_codes'):
						publisher['country_codes'] = '|'.join(countries)
					else:
						publisher['country_codes'] = None
						
					publishers_writer.writerow(publisher)
										
						
					if counts_by_year := publisher.get('counts_by_year'):
						for count_by_year in counts_by_year:
							count_by_year['publisher_id'] = publisher_id
							counts_by_year_writer.writerow(count_by_year)

					if roles := publisher.get('roles'):
						for role in roles:
							if role.get('id') and role.get('role')=='funder':
								role['publisher_id'] = publisher_id
								role['funder_id'] = role.get('id')[21:]
								roles_writer.writerow(role)
							


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
	flatten_publishers()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
