import csv
import glob
import gzip
import json
import os
import time
import argparse

SNAPSHOT_DIR = '../openalex-snapshot'
CSV_DIR = '../openalex_csv'

if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)

ENTITY = 'works'
SEP = ', '

PARTDIR = [
	"updated_date=201*/*.gz",
	"updated_date=202[0-4]-*/*.gz",
	"updated_date=2025-0*/*.gz",
	"updated_date=2025-10-0*/*.gz",
	"updated_date=2025-10-10/part_00*.gz",
	"updated_date=2025-10-10/part_01*.gz",
	"updated_date=2025-10-1[1-9]/*.gz",
	"updated_date=2025-10-[2-3]*/*.gz",
	"updated_date=2025-11-0[1-5]/*.gz",
	"updated_date=2025-11-06/part_00*.gz",
	"updated_date=2025-11-06/part_01.gz",
	"updated_date=2025-11-06/part_02*.gz",
	"updated_date=2025-11-06/part_03*.gz",
	"updated_date=2025-11-06/part_04*.gz",
	"updated_date=2025-11-06/part_05*.gz",
	"updated_date=2025-11-06/part_06*.gz",
	"updated_date=2025-11-06/part_07*.gz",
	"updated_date=2025-11-06/part_08*.gz",
	"updated_date=2025-11-06/part_09*.gz",
	"updated_date=2025-11-06/part_1*.gz",
	"updated_date=2025-11-0[7-9]/*.gz",
	"updated_date=2025-11-[1-3]*/*.gz",
	"updated_date=2025-12-*/*.gz",
	"updated_date=2026-01-0*/*.gz",
	"updated_date=2026-01-1[0-1]/*.gz",
	"updated_date=2026-01-13/part_00[0-2]*.gz",
	"updated_date=2026-01-13/part_00[3-4]*.gz",
	"updated_date=2026-01-1[4-9]/*.gz",
	"updated_date=2026-01-[2-3]*/*.gz",
	"updated_date=2026-02-0[1-8]/*.gz",
	"updated_date=2026-02-09/part_00*.gz",
	"updated_date=2026-02-09/part_01*.gz",
	"updated_date=2026-02-10/*.gz",
	"updated_date=2026-02-1[1-9]/*.gz",
	"updated_date=2026-02-2*/*.gz",
	"updated_date=2026-03-[0-1]*/*.gz",
	"updated_date=2026-03-2[0-4]/*.gz",
	"updated_date=2026-03-2[5-6]/*.gz",
	"updated_date=2026-03-2[7-9]/*.gz",
	"updated_date=2026-03-30/*.gz"
]

csv_files = {
    'works': {
        'works': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works.csv.gz'),
            'columns': [
                'id', 'doi', 'title', 'publication_year',
                'publication_date', 'type', 'cited_by_count',
                'is_retracted', 'is_paratext', 'is_xpac', 'language', 'fwci',
                'citation_normalized_percentile', 'source_name', 'source_id',
                'volume', 'issue', 'first_page', 'last_page', 'is_oa', 'oa_status',
                'updated_date'
            ]
        },
        'locations': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_locations.csv.gz'),
            'columns': [
                'work_id', 'source_id', 'landing_page_url', 'pdf_url', 'is_oa',
                'version', 'license', 'is_primary', 'is_best_oa'
            ]
        },
        'authorships': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_authorships.csv.gz'),
            'columns': [
                'work_id', 'author_position', 'author_id', 'institution_id',
                'is_corresponding', 'raw_affiliation_strings'
            ]
        },
        'topics': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_topics.csv.gz'),
            'columns': [
                'work_id', 'topic_id', 'score'
            ]
        },
        'mesh': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_mesh.csv.gz'),
            'columns': [
                'work_id', 'descriptor_ui', 'descriptor_name', 'qualifier_ui',
                'qualifier_name', 'is_major_topic'
            ]
        },
        'referenced_works': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_referenced_works.csv.gz'),
            'columns': [
                'work_id', 'referenced_work_id'
            ]
        },
        'related_works': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_related_works.csv.gz'),
            'columns': [
                'work_id', 'related_work_id'
            ]
        },
        'abstracts': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_abstracts.csv.gz'),
            'columns': [
                'work_id', 'abstract_inverted_index'
            ]
        },
        'apcs': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_apcs.csv.gz'),
            'columns': [
                'work_id', 'list_value', 'list_currency', 'list_value_usd',
                'paid_value', 'paid_currency', 'paid_value_usd'
            ]
        },
        'awards': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_awards.csv.gz'),
            'columns': [
                'work_id', 'award_id'
            ]
        },
        'funders': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_funders.csv.gz'),
            'columns': [
                'work_id', 'funder_id'
            ]
        },
        'sdgs': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_sdgs.csv.gz'),
            'columns': [
                'work_id', 'sdg_id', 'score'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, ENTITY, 'works_counts_by_year.csv.gz'),
            'columns': [
                'work_id', 'year', 'cited_by_count'
            ]
        },
    },
}



def flatten_works():
	file_spec = csv_files[ENTITY]
	
#	with gzip.open(file_spec['works']['name'], 'wt',
#                   encoding='utf-8') as works_csv, \
#            gzip.open(file_spec['locations']['name'], 'wt',
#                      encoding='utf-8') as locations, \
#            gzip.open(file_spec['authorships']['name'], 'wt',
#                      encoding='utf-8') as authorships_csv, \
#            gzip.open(file_spec['topics']['name'], 'wt',
#                      encoding='utf-8') as topics_csv, \
#            gzip.open(file_spec['mesh']['name'], 'wt',
#                      encoding='utf-8') as mesh_csv, \
#            gzip.open(file_spec['referenced_works']['name'], 'wt',
#                      encoding='utf-8') as referenced_works_csv, \
#            gzip.open(file_spec['related_works']['name'], 'wt',
#                      encoding='utf-8') as related_works_csv, \
#            gzip.open(file_spec['abstracts']['name'], 'wt',
#                      encoding='utf-8') as abstracts_csv, \
#            gzip.open(file_spec['apcs']['name'], 'wt',
#                      encoding='utf-8') as apcs_csv, \
#            gzip.open(file_spec['awards']['name'], 'wt',
#                      encoding='utf-8') as awards_csv, \
#            gzip.open(file_spec['funders']['name'], 'wt',
#                      encoding='utf-8') as funders_csv, \
#            gzip.open(file_spec['sdgs']['name'], 'wt',
#                      encoding='utf-8') as sdgs_csv, \
#            gzip.open(file_spec['counts_by_year']['name'], 'wt',
#                      encoding='utf-8') as counts_by_year_csv:

	with gzip.open(f"{CSV_DIR}/{ENTITY}/works-{PARTNUM}.csv.gz", 'wt',
                   encoding='utf-8') as works_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_locations-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as locations, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_authorships-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as authorships_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_topics-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as topics_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_mesh-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as mesh_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_referenced_works-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as referenced_works_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_related_works-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as related_works_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_abstracts-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as abstracts_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_apcs-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as apcs_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_awards-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as awards_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_funders-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as funders_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_sdgs-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as sdgs_csv, \
            gzip.open(f"{CSV_DIR}/{ENTITY}/works_counts_by_year-{PARTNUM}.csv.gz", 'wt',
                      encoding='utf-8') as counts_by_year_csv:
                      
		works_writer = init_dict_writer(works_csv, file_spec['works'], lineterminator='\n')
		locations_writer = init_dict_writer(locations, file_spec['locations'],lineterminator='\n')
		authorships_writer = init_dict_writer(authorships_csv,
                                              file_spec['authorships'],lineterminator='\n')
		topics_writer = init_dict_writer(topics_csv, file_spec['topics'],lineterminator='\n')
		mesh_writer = init_dict_writer(mesh_csv, file_spec['mesh'],lineterminator='\n')
		referenced_works_writer = init_dict_writer(referenced_works_csv,
                                                   file_spec[
                                                       'referenced_works'],lineterminator='\n')
		related_works_writer = init_dict_writer(related_works_csv,
                                                file_spec['related_works'],lineterminator='\n')
		abstracts_writer = init_dict_writer(abstracts_csv,
                                                file_spec['abstracts'],lineterminator='\n')
		apcs_writer = init_dict_writer(apcs_csv, file_spec['apcs'],lineterminator='\n')
		awards_writer = init_dict_writer(awards_csv, file_spec['awards'],lineterminator='\n')
		funders_writer = init_dict_writer(funders_csv, file_spec['funders'],lineterminator='\n')
		sdgs_writer = init_dict_writer(sdgs_csv, file_spec['sdgs'],lineterminator='\n')
		counts_by_year_writer = init_dict_writer(counts_by_year_csv, 
        										file_spec['counts_by_year'],lineterminator='\n')

		for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', ENTITY, PARTDIR[PARTNUM])):
			print(jsonl_file_name)
			with gzip.open(jsonl_file_name, 'r') as works_jsonl:
				for work_json in works_jsonl:
					if not work_json.strip():
						continue

					work = json.loads(work_json)

					if not (work_id := work.get('id')):
						continue
					
					############ works
					work_id = work_id[21:]
					work['id'] = work_id
					
					if work.get('citation_normalized_percentile'):
						work['citation_normalized_percentile'] = work.get(
                    		'citation_normalized_percentile').get('value')
					else:
						work['citation_normalized_percentile'] = None

					if primary_location := work.get('primary_location'):
						if source := primary_location.get('source'):
							work['source_name'] = source.get('display_name')
							if source.get('id'):
								work['source_id'] = source.get('id')[21:]
					
					if biblio := work.get('biblio'):
						work['volume'] = biblio.get('volume')
						work['issue'] = biblio.get('issue')
						work['first_page'] = biblio.get('first_page')
						work['last_page'] = biblio.get('last_page')
                    
					if open_access := work.get('open_access'):
						work['is_oa'] = open_access.get('is_oa')
						work['oa_status'] = open_access.get('oa_status')
                    
					works_writer.writerow(work)
					
					############ abstracts
					if (abstract := work.get('abstract_inverted_index')) is not None:
						abstracts_writer.writerow({
                    		'work_id': work_id,
                    		'abstract_inverted_index': json.dumps(abstract,
                                                                     ensure_ascii=False)
                    	})
                                            
                    # best_oa_locations - for use with values below
					oa_src = None
					if best_oa_location := work.get('best_oa_location'):
						if best_oa_location.get('source') and best_oa_location.get('source').get('id'):
							oa_src = best_oa_location.get('source').get('id')[21:]
                                        
                    
                    ############ locations
					if locations := work.get('locations'):
						for location in locations:
							if location.get('source') and location.get('source').get('id'):
								locations_writer.writerow({
                                    'work_id': work_id,
                                    'source_id': location['source']['id'][21:],
                                    'landing_page_url': location.get(
                                        'landing_page_url'),
                                    'pdf_url': location.get('pdf_url'),
                                    'is_oa': location.get('is_oa'),
                                    'version': location.get('version'),
                                    'license': location.get('license'),
                                    'is_primary': True if location['source']['id'][21:] == work.get('source_id') else False,
                                    'is_best_oa': True if location['source']['id'][21:] == oa_src else False,                                    
                                })


                    ############ authorships
					if authorships := work.get('authorships'):
						for authorship in authorships:
							if author_id := authorship.get('author', {}).get('id'):
								institutions = authorship.get('institutions')
								institution_ids = [i.get('id') for i in institutions]
								institution_ids = [i for i in institution_ids if i]
								institution_ids = institution_ids or [None]
								
								for institution_id in institution_ids:
									authorships_writer.writerow({
                                        'work_id': work_id,
                                        'author_position': authorship.get(
                                            'author_position'),
                                        'author_id': author_id[21:],
                                        'institution_id': institution_id[21:] if institution_id is not None else None,
                                        'is_corresponding': authorship.get('is_corresponding'),
                                        'raw_affiliation_strings': SEP.join(authorship.get(
                                            'raw_affiliation_strings')),
                                    })

                    ############ topics
					for topic in work.get('topics', []):
						if topic_id := topic.get('id'):
							topics_writer.writerow({
                                'work_id': work_id,
                                'topic_id': topic_id[21:],
                                'score': topic.get('score')
                            })

                    ############ mesh
					for mesh in work.get('mesh'):
						mesh['work_id'] = work_id
						mesh_writer.writerow(mesh)

                    ############ referenced_works
					for referenced_work in work.get('referenced_works'):
						if referenced_work:
							referenced_works_writer.writerow({
                                'work_id': work_id,
                                'referenced_work_id': referenced_work[21:]
                            })

                    ############ related_works
					for related_work in work.get('related_works'):
						if related_work:
							related_works_writer.writerow({
                                'work_id': work_id,
                                'related_work_id': related_work[21:]
                            })

                    ############ apcs
					if work.get('apc_list') or work.get('apc_paid'):
						apcs = {'work_id': work_id}
						if apc_list := work.get('apc_list'):
							apcs |= {f"list_{key}": val for key,val in apc_list.items()}
						if apc_paid := work.get('apc_paid'):
							apcs |= {f"paid_{key}": val for key,val in apc_paid.items()}
						apcs_writer.writerow(apcs)

                    ############ awards
					for award in work.get('awards'):
						if award:
							awards_writer.writerow({
                                'work_id': work_id,
                                'award_id': award.get('id')[21:]
                            })

                    ############ funders
					for funder in work.get('funders'):
						if funder:
							funders_writer.writerow({
                                'work_id': work_id,
                                'funder_id': funder.get('id')[21:]
                            })

                    ############ sdgs
					for sdg in work.get('sustainable_development_goals'):
						if sdg:
							sdgs_writer.writerow({
                                'work_id': work_id,
                                'sdg_id': sdg.get('id').rsplit('/',1)[1],
                                'score': sdg.get('score')
                            })

                    ############ counts_by_year
					for cby in work.get('counts_by_year'):
						cby['work_id'] = work_id
						counts_by_year_writer.writerow(cby)



def init_dict_writer(csv_file, file_spec, **kwargs):
    writer = csv.DictWriter(
        csv_file, fieldnames=file_spec['columns'], extrasaction='ignore', **kwargs
    )
    writer.writeheader()
    return writer


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process the works directory in chunks')
	parser.add_argument('chunk', type=int)
	args = parser.parse_args()
	
	PARTNUM = args.chunk
	
	if not os.path.exists(os.path.join(CSV_DIR, ENTITY)):
		os.mkdir(os.path.join(CSV_DIR, ENTITY))

	start = time.time()
	flatten_works()
	end = time.time()
	print(f"Time taken: {(end - start) / 60}  minutes")
