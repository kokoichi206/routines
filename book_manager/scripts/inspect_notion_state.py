import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from config.setup import load_notion_config
from api.impl.notion_manager import NotionManager

config=load_notion_config()
notion=NotionManager(config.api_key,config.database_id)
page_ids=['4186a2934a1e817e8b8ae1299ec48380','4186a2934a1e81649c79d3769d353e2b','4186a2934a1e81a29679ce5c00cc27f8']
urls=[]
for page_id in page_ids:
    r=notion._session.get(f'https://api.notion.com/v1/pages/{page_id}',headers=notion.headers,timeout=30)
    r.raise_for_status();page=r.json()
    props=page['properties']
    url=props['url']['url']
    urls.append(url)
    print(json.dumps({'kind':'direct_page','id':page_id,'page_url':page['url'],'archived':page['archived'],'in_trash':page.get('in_trash'),'created_time':page['created_time'],'last_edited_time':page['last_edited_time'],'title_parts':props['title']['title'],'drive_url':url,'parent_matches':page['parent']['database_id'].replace('-','')==config.database_id.replace('-','')},ensure_ascii=False))
for url in set(urls):
    r=notion._session.post(f'https://api.notion.com/v1/databases/{config.database_id}/query',headers=notion.headers,json={'filter':{'property':'url','url':{'equals':url}}},timeout=30)
    r.raise_for_status();pages=r.json()['results']
    print(json.dumps({'kind':'filtered_query','drive_url':url,'pages':[{'id':p['id'],'url':p['url'],'title_parts':p['properties']['title']['title']} for p in pages]},ensure_ascii=False))
books=notion.fetch()
print(json.dumps({'kind':'unfiltered_query','total':len(books),'matching':[{'title':b.title,'drive_url':b.url} for b in books if b.url in urls]},ensure_ascii=False))
for mode,query,version in [
    ('raw_unfiltered',{},'2021-05-13'),
    ('raw_url_filter',{'filter':{'property':'url','url':{'is_not_empty':True}}},'2021-05-13'),
    ('raw_created_sort',{'sorts':[{'timestamp':'created_time','direction':'ascending'}]},'2021-05-13'),
    ('raw_2022',{},'2022-06-28'),
]:
    raw=[];body=query.copy();page_sizes=[]
    while True:
        headers={**notion.headers,'Notion-Version':version}
        response=notion._session.post(f'https://api.notion.com/v1/databases/{config.database_id}/query',headers=headers,json=body,timeout=30)
        response.raise_for_status();result=response.json();raw.extend(result['results']);page_sizes.append(len(result['results']))
        if not result['has_more']:break
        body={**query,'start_cursor':result['next_cursor']}
    target_rows=[{'id':p['id'],'title_parts':p['properties']['title']['title'],'drive_url':p['properties']['url']['url']} for p in raw if p['id'].replace('-','') in page_ids]
    print(json.dumps({'kind':mode,'raw_count':len(raw),'parsed_count':len(notion._extract_book_data(raw)),'unique_ids':len({p['id'] for p in raw}),'page_sizes':page_sizes,'target_rows':target_rows},ensure_ascii=False))
