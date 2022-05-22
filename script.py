import os
import re
from urllib.parse import urlparse
import pandas as pd
from tqdm import tqdm

from github import GitHubApi

BASE_URL = 'https://api.github.com'

F_SYNONYMS = open('words/features.txt').read().split('\n')
I_SYNONYMS = open('words/improvements.txt').read().split('\n')
BF_SYNONYMS = open('words/bug_fixes.txt').read().split('\n')
DR_SYNONYMS = open('words/deprecations_removals.txt').read().split('\n')
ALL_SYNONYMS = F_SYNONYMS + I_SYNONYMS + BF_SYNONYMS + DR_SYNONYMS

def get_release_id(releases, tag):
    for release in releases:
        if release['tag_name'] == tag:
            return release['id']
    return None

def get_commit_messages(commits_url):
    res = api.get_commits(urlparse(commits_url).path, token)
    return [commit['commit']['message'] for commit in res['commits']]

def get_release_note(repo, version):
    releases = api.get_releases(repo, token)
    release_id = get_release_id(releases, version)
    release = api.get_release(repo, str(release_id), token)
    lines = release['body'].splitlines()
    note = {}
    current_category = None
    list_flag = False
    sub_list_flag = False
    ignore_categoery = True
    text = ''

    for i, l in enumerate(lines):
        n_word_flag = False
        if len(l) <= 20:
            for n_word in ['none', 'nothing', 'n/a']:
                if n_word in l.lower():
                    n_word_flag = True
        if n_word_flag:
            continue

        category_l = l
        for e in ['💅', '👍', '🚨', '👻', '📝', '📦', '🏠', '🐛', '🐞', '🚀', '🔨', '🔥', '✨', '🔒', '📖', '🎉', '🔩', '💥', '⚡', '⚠️',
                  ':bug:', ':lock:', ':tada:', ':book:', ':boom:', ':nut_and_bolt:', ':mag:', ':construction_worker:', ':nail_care:', ':house:', ':rocket:', '*', '#', ':']:
            category_l = category_l.replace(e, '')
        category_l = category_l.strip().lower()

        prev_category = None
        if category_l in ALL_SYNONYMS:
            ignore_categoery = False
            prev_category = current_category
            current_category = category_l
            note[current_category] = []
        elif l[:2] == '##' or (l[:2] == '**' and l[-3:] == ':**'):
            ignore_categoery = True
    
        if note and not ignore_categoery:
            if prev_category and text:
                if sub_list_flag:
                    sub_list_flag = False
                else:
                    note[prev_category].append(text)
                list_flag = False
                text = None
            elif list_flag and note and (l[:3] == '  -' or l[:3] == '  *') and \
                 (lines[i-1][:2] == ' -' or lines[i-1][:2] == ' *' or lines[i-1][:2] == '* '): # サブリストの検出
                text_with_sublist = text + ' ' + l[4:]
                note[current_category].append(text_with_sublist)
                sub_list_flag = True
            elif list_flag and note and (l[:4] == '   -' or l[:4] == '   *') \
                 and (lines[i-1][:3] == '  -' or lines[i-1][:3] == '  *'):
                text_with_sublist = text + ' ' + l[5:]
                note[current_category].append(text_with_sublist)
                sub_list_flag = True
            elif re.search(r'^[-*] .*', l.strip()):
                if sub_list_flag:
                    sub_list_flag = False
                elif (list_flag and note and text or 
                     list_flag and note and text and text not in note[current_category]):
                    note[current_category].append(text)
                list_flag = True
                text = l[2:].strip()
                if len(lines) == i + 1 and note:
                    note[current_category].append(text)
            elif list_flag and l.strip():
                text += ' ' + l.strip()
                if len(lines) == i + 1 and note:
                    note[current_category].append(text)
            elif list_flag and note and l.strip() == '':
                if i + 1 != len(lines) and ('-' in lines[i+1][:4] or '*' in lines[i+1][:4]):
                    continue
                elif sub_list_flag:
                    sub_list_flag = False
                else:
                    note[current_category].append(text)
                list_flag = False
                text = None

    release_note = {}
    category_flag = [0, 0, 0, 0]
    for category, v in note.items():
        if not v:
            continue

        if category in F_SYNONYMS:
            category_flag[0] = 1
            if 'Features' in release_note:
                release_note['Features'].extend(v)
            else:
                release_note['Features'] = v
        elif category in I_SYNONYMS:
            category_flag[1] = 1
            if 'Improvements' in release_note:
                release_note['Improvements'].extend(v)
            else:
                release_note['Improvements'] = v
        elif category in BF_SYNONYMS:
            category_flag[2] = 1
            if 'Bug Fixes' in release_note:
                release_note['Bug Fixes'].extend(v)
            else:
                release_note['Bug Fixes'] = v
        elif category in DR_SYNONYMS:
            category_flag[3] = 1
            if 'Deprecations and Removals' in release_note:
                release_note['Deprecations and Removals'].extend(v)
            else:
                release_note['Deprecations and Removals'] = v

    return release_note

api = GitHubApi()
token = os.getenv('GITHUB_TOKEN')

data = []
df = pd.read_json('rnsum.jsonl', orient='records', lines=True)
for _, row in tqdm(df.iterrows(), total=df.shape[0]):
    try:
        row['commit_messages'] = get_commit_messages(row['commits_url'])
        version = row['note_url'].split('/')[-1]
        row['release_note'] = get_release_note(row['repo'], version)
        data.append(row)
    except Exception as e:
        print(e)

pd.DataFrame(data).to_json('rnsum_with_text.jsonl', orient='records', lines=True)
