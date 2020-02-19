
# http://github.com/bobk/jiragithub
#
#   jiragithub-update_comments.py
#   based on Jira issuekeys found in GitHub commit messages, this code adds 
#   the GitHub commit information as comments to the associated Jira issues
#
#   see documentation on operation and configuration before using
#

from github import Github
from jira import JIRA
import os
import datetime
import json
import re
import requests
from datetime import datetime
from lxml import html

#   this is an undocumented and unsupported GitHub HTML API for getting the branch(es) containing a commit
#   since it is just HTML we have to parse it with lxml and xpath
def get_branches_commit(repo_html_url, commit_sha):

    api_html_url = repo_html_url.strip("/") + "/branch_commits/" + commit_sha
    github_tree = html.fromstring(requests.get(api_html_url).content)
    
    branches = github_tree.xpath('//ul[@class="branches-list"]/li[@class="branch"]/a')
    
    retval = [branch.text for branch in branches]
    return retval

def main():

#   read in all of our config file values - see docs for explanation of each
    with open('jiragithub-config.json', 'r') as config_file:
        config = json.load(config_file)
        config_file.close
    jira_projects = config['general']['jira_projects']
    jira_comment_footprint = config['general']['jira_comment_footprint']

#   get GitHub PAT from env var and connect to GitHub
    githubkey = os.environ['GITHUB_PASSWORD']
    github_base_url = config['general']['github_base_url']
    if (github_base_url != ''):
        githubconn = Github(login_or_token=githubkey, base_url=github_base_url)
    else:
        githubconn = Github(login_or_token=githubkey)
    github_org = config['general']['github_org']

#   connect to Jira also
    jira_server = config['general']['jira_server']
    jira_username = os.environ['JIRA_USERNAME']
    jira_password = os.environ['JIRA_PASSWORD']
    options = { "server" : jira_server }
    jira = JIRA(options, basic_auth=(jira_username, jira_password))

#   go through each GitHub repo in the config file, look for commits since the last scan time with(for that repo)
#   that have a commit message that contains a Jira issuekey that is in our project list
    for repo_name in config['github_repos']:
        repo_lastscan_timestamp_text = config['github_repos'][repo_name]['repo_lastscan_timestamp']
        if not (repo_lastscan_timestamp_text == ''):
            repo_lastscan_timestamp = datetime.fromisoformat(repo_lastscan_timestamp_text)
        else:
            repo_lastscan_timestamp = datetime.min
        jira_comment_format = config['github_repos'][repo_name]['jira_comment_format']

#   connect to the repo and get all the commits since the last scan time
        repo = githubconn.get_repo(github_org + '/' + repo_name)
        commits = repo.get_commits(since=repo_lastscan_timestamp)
        for commit in commits:
            message = commit.commit.message
#   for each commit, look in all the projects to see if there is a match
            for jira_project in jira_projects:
                pattern = re.compile(r'(' + jira_project + '-[0-9]+)')
                match = pattern.match(message)
#   if there is a match, write a new comment to the Jira issue
                if (match):
                    jira_issue = jira.issue(match.group(1))
                    if (jira_issue):

#   construct the new comment
                        jira_comment = jira_comment_format
                        jira_comment = jira_comment.replace('<repo_name>', repo_name)
                        jira_comment = jira_comment.replace('<repo_url>', repo.html_url)
                        branch_name = get_branches_commit(repo.html_url, commit.commit.sha)[0]
                        jira_comment = jira_comment.replace('<branch_name>', branch_name)
                        branch_url = repo.html_url + "/tree/" + branch_name
                        jira_comment = jira_comment.replace('<branch_url>', branch_url)
                        jira_comment = jira_comment.replace('<commit_message>', commit.commit.message)
                        jira_comment = jira_comment.replace('<commit_url>', commit.commit.html_url)
                        jira_comment = jira_comment.replace('<commit_abbrev>', commit.commit.sha[:7])
                        jira_comment = jira_comment.replace('<commit_author>', commit.commit.author.name)

#   add the new comment
                        jira.add_comment(jira_issue, jira_comment)

#   update our config file with the new timestamp, so that we do not process the same commits again
        config['github_repos'][repo_name]['repo_lastscan_timestamp'] = str(datetime.today())
        with open('jiragithub-config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

if __name__== "__main__" :
    main()
