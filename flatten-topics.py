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

ENTITY = 'topics'

csv_files = {
    'topics': {
        'topics': {
            'name': os.path.join(CSV_DIR, ENTITY, 'topics.csv.gz'),
            'columns': ['id', 'display_name', 'subfield_id',
                        'subfield_display_name', 'field_id',
                        'field_display_name',
                        'domain_id', 'domain_display_name',
                        'works_count', 'cited_by_count', 'updated_date']
        }
    },
}


def flatten_topics():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['topics']['name'], 'wt', encoding='utf-8') as topics_csv:
		topics_writer = init_dict_writer(topics_csv, file_spec['topics'],lineterminator='\n')
		
		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as topics_jsonl:
				for line in topics_jsonl:
					if not line.strip():
						continue
					
					topic = json.loads(line)
					
					if not (topic_id := topic.get('id')):
						continue

					topic_id = topic_id[21:]
					topic['id'] = topic_id
					
					for key in ('subfield', 'field', 'domain'):
						topic[f'{key}_id'] = topic[key]['id'].rsplit('/',1)[1]
						topic[f'{key}_display_name'] = topic[key]['display_name']
						del topic[key]
						
					topics_writer.writerow(topic)
					


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
	flatten_topics()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
