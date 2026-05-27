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

ENTITY = 'institutions'

csv_files = {
    'institutions': {
        'institutions': {
            'name': os.path.join(CSV_DIR, ENTITY, 'institutions.csv.gz'),
            'columns': [
                'id', 'ror', 'display_name', 'country_code', 'city', 'region',
                'geonames_city_id', 'latitude', 'longitude',
                'type', 'works_count', 'cited_by_count', 'updated_date'
            ]
        },
        'associated_institutions': {
            'name': os.path.join(CSV_DIR, ENTITY,
                                 'institutions_associated_institutions.csv.gz'),
            'columns': [
                'institution_id', 'associated_institution_id', 'relationship'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY, 'institutions_counts_by_year.csv.gz'),
            'columns': [
                'institution_id', 'year', 'works_count', 'cited_by_count',
                'oa_works_count'
            ]
        },
        'publisher_roles': {
            'name': os.path.join(CSV_DIR, ENTITY, 'institutions_publisher_roles.csv.gz'),
            'columns': [
                'institution_id', 'publisher_id'
            ]
        },
        'funder_roles': {
            'name': os.path.join(CSV_DIR, ENTITY, 'institutions_funder_roles.csv.gz'),
            'columns': [
                'institution_id', 'funder_id'
            ]
        }
    },
}



def flatten_institutions():
	file_spec = csv_files[ENTITY]
	
	with gzip.open(file_spec['institutions']['name'], 'wt',
                   encoding='utf-8') as institutions_csv, \
            gzip.open(file_spec['associated_institutions']['name'], 'wt',
                      encoding='utf-8') as associated_institutions_csv, \
            gzip.open(file_spec['counts_by_year']['name'], 'wt',
                      encoding='utf-8') as counts_by_year_csv, \
            gzip.open(file_spec['publisher_roles']['name'], 'wt',
                      encoding='utf-8') as publisher_roles_csv, \
            gzip.open(file_spec['funder_roles']['name'], 'wt',
                      encoding='utf-8') as funder_roles_csv:
                      
		institutions_writer = init_dict_writer(institutions_csv, file_spec['institutions'],lineterminator='\n')
		associated_institutions_writer = init_dict_writer(associated_institutions_csv, file_spec['associated_institutions'],lineterminator='\n')
		counts_by_year_writer = init_dict_writer(counts_by_year_csv,
			file_spec['counts_by_year'],lineterminator='\n')
		publisher_roles_writer = init_dict_writer(publisher_roles_csv,
			file_spec['publisher_roles'],lineterminator='\n')
		funder_roles_writer = init_dict_writer(funder_roles_csv,
			file_spec['funder_roles'],lineterminator='\n')

       

		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, '*', '*.gz')):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as institutions_jsonl:
				for institution_json in institutions_jsonl:
					if not institution_json.strip():
						continue

					institution = json.loads(institution_json)
                    
					if not (institution_id := institution.get('id')):
						continue

                    ############ institutions
					institution_id = institution_id[21:]
					institution['id'] = institution_id
                    
					if institution_geo := institution.get('geo'):
						institution['city'] = institution_geo.get('city')
						institution['region'] = institution_geo.get('region')
						institution['geonames_city_id'] = institution_geo.get('geonames_city_id')
						institution['longitude'] = institution_geo.get('longitude')
						institution['latitude'] = institution_geo.get('latitude')
                   
					institutions_writer.writerow(institution)


                    # associated_institutions
					if associated_institutions := institution.get('associated_institutions'):
						for associated_institution in associated_institutions:
							if associated_institution_id := associated_institution.get('id'):
								associated_institutions_writer.writerow({
                                    'institution_id': institution_id,
                                    'associated_institution_id': associated_institution_id[21:],
                                    'relationship': associated_institution.get('relationship')
                                })

                    # counts_by_year
					if counts_by_year := institution.get('counts_by_year'):
						for count_by_year in counts_by_year:
							count_by_year['institution_id'] = institution_id
							counts_by_year_writer.writerow(count_by_year)
                            
					if roles := institution.get('roles'):
						for role in roles:
							role['institution_id'] = institution_id
							if role.get('role') == 'publisher':
								role['publisher_id'] = role.get('id')[21:]
								publisher_roles_writer.writerow(role)
							elif role.get('role') == 'funder':
								role['funder_id'] = role.get('id')[21:]
								funder_roles_writer.writerow(role)							



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
	flatten_institutions()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
