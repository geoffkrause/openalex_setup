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

#FILES_PER_ENTITY = int(os.environ.get('OPENALEX_DEMO_FILES_PER_ENTITY', '0'))

ENTITY = 'awards'

csv_files = {
    'awards': {
        'awards': {
            'name': os.path.join(CSV_DIR, ENTITY, 'awards.csv.gz'),
            'columns': [
                'id', 'display_name', 'funding_type', 'doi', 
                'funder_id', 'funder_award_id', 'funder_scheme',
                'amount', 'currency',
                'start_date', 'end_date',
                'updated_date'
            ]
        }
    },
}



def flatten_awards():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['awards']['name'], 'wt', encoding='utf-8') as awards_csv:

		awards_writer = init_dict_writer(awards_csv, file_spec['awards'],lineterminator='\n')
		
		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as awards_jsonl:
				for award_json in awards_jsonl:
					
					if not award_json.strip():
						continue
						
					award = json.loads(award_json)
					
					if not (award_id := award.get('id')):
						continue
					
					award_id = award_id[21:]
					award['id'] = award_id
					
					if funder := award.get('funder'):
						award['funder_id'] = funder.get('id')[21:]
						
					awards_writer.writerow(award)
																
							

def init_dict_writer(csv_file, file_spec, **kwargs):
    writer = csv.DictWriter(
        csv_file, fieldnames=file_spec['columns'], extrasaction='ignore', quoting=csv.QUOTE_NONNUMERIC, **kwargs
    )
    writer.writeheader()
    return writer


if __name__ == '__main__':

	if not os.path.exists(os.path.join(CSV_DIR, ENTITY)):
		os.mkdir(os.path.join(CSV_DIR, ENTITY))
	
	start = time.time()
	flatten_awards()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
