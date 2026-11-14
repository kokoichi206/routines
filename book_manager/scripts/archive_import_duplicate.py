import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from config.setup import load_notion_config
from api.impl.notion_manager import NotionManager

config=load_notion_config()
notion=NotionManager(config.api_key,config.database_id)
original_id='4186a2934a1e817e8b8ae1299ec48380'
duplicate_id='4186a2934a1e81649c79d3769d353e2b'
expected_url='https://drive.google.com/file/d/1HRrT_N6fMab8Q8y82YA3py1OZI8WIM0c/view?usp=sharing'
pages=[]
for page_id in [original_id,duplicate_id]:
    response=notion._session.get(f'https://api.notion.com/v1/pages/{page_id}',headers=notion.headers,timeout=30)
    response.raise_for_status();page=response.json();pages.append(page)
    assert page['properties']['url']['url']==expected_url
    assert ''.join(t['plain_text'] for t in page['properties']['title']['title'])=='software_design_2025_06.pdf'
    assert page['parent']['database_id'].replace('-','')==config.database_id.replace('-','')
    assert not page['archived']
assert pages[1]['created_time']=='2026-11-14T18:05:00.000Z'
assert pages[1]['last_edited_time']==pages[1]['created_time']
response=notion._session.get(f'https://api.notion.com/v1/blocks/{duplicate_id}/children',headers=notion.headers,timeout=30)
response.raise_for_status()
assert response.json()['results']==[]
response=notion._session.patch(f'https://api.notion.com/v1/pages/{duplicate_id}',headers=notion.headers,json={'archived':True},timeout=30)
response.raise_for_status()
assert response.json()['archived']
print('Archived the one duplicate created by this import:',pages[1]['url'])
print('Kept the original page:',pages[0]['url'])
