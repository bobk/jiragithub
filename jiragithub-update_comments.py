
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

def get_branches_commit(repo_html_url, commit_sha):

    api_html_url = repo_html_url.strip("/") + "/branch_commits/" + commit_sha
    github_tree = html.fromstring(requests.get(api_html_url).content)
    
    branches = github_tree.xpath('//ul[@class="branches-list"]/li[@class="branch"]/a')
    
    retval = [branch.text for branch in branches]
    return retval

def main():

    githubkey = os.environ['GITHUB_PASSWORD']
    githubconn = Github(githubkey)

    with open('jiragithub-config.json', 'r') as config_file:
        config = json.load(config_file)

    config['general']['foo'] = "fff"
    with open('jiragithub-config.json', 'w') as config_file:
        json.dump(config, config_file, indent=8)

    jira_server = config['general']['jira_server']
    jira_username = os.environ['JIRA_USERNAME']
    jira_password = os.environ['JIRA_PASSWORD']
    options = { "server" : jira_server }
    jira = JIRA(options, basic_auth=(jira_username, jira_password))

    jira_projects = config['general']['jira_projects']

    for repo_name in config['github_repos']:
        repo_url = config['github_repos'][repo_name]['repo_url']
        repo_lastscan_time = datetime.fromisoformat(config['github_repos'][repo_name]['repo_lastscan_time'])
        jira_comment_format = config['github_repos'][repo_name]['jira_comment_format']
        jira_comment_maxnum = int(config['github_repos'][repo_name]['jira_comment_maxnum'])

        repo = githubconn.get_repo('bobk/' + repo_name)
        print(repo)
        commits = repo.get_commits(since=repo_lastscan_time)
        for commit in commits:
            #print(dir(commit))
            #print(dir(commit.commit))
            message = commit.commit.message
            for jira_project in jira_projects:
                pattern = re.compile(r'(' + jira_project + '-[0-9]+)')
                match = pattern.match(message)
                if (match):
                    jira_issue = jira.issue(match.group(1))
                    if (jira_issue):
                        jira_comment = jira_comment_format
                        jira_comment = jira_comment.replace('<repo_name>', repo_name)
                        jira_comment = jira_comment.replace('<repo_url>', repo.html_url)
                        branch_name = get_branches_commit(repo.html_url, commit.commit.sha)[0]
                        jira_comment = jira_comment.replace('<branch_name>', branch_name)
                        branch_url = repo.html_url + "/tree" + branch_name
                        jira_comment = jira_comment.replace('<branch_url>', branch_url)
                        jira_comment = jira_comment.replace('<commit_message>', commit.commit.message)
                        jira_comment = jira_comment.replace('<commit_url>', commit.commit.html_url)
                        jira_comment = jira_comment.replace('<commit_abbrev>', commit.commit.sha[:7])
                        jira_comment = jira_comment.replace('<commit_author>', commit.commit.author.name)
                        #jira_comment = jira_comment.replace('<branch_name>', commit.)
                        #print(jira_comment)
                        jira.add_comment(jira_issue, jira_comment)
                        #print(get_branches_commit(repo.html_url, commit.commit.sha))

                        if (jira_comment_maxnum >= 1):
                            jira_allcomments = jira.comments(jira_issue)
                            jira_allcomments.sort(key=lambda r: datetime.fromisoformat(r.created[:-5]))
                            print(jira_allcomments)
                            jira_comment_num = 0
                            for comment in jira_allcomments:
                                comment.delete()
                                jira_comment_num = jira_comment_num + 1
                                


            
            # print("   " + str(commit.commit.author.date) + "  " + commit.sha + "  " + commit.commit.message)
            # for comment in commit.get_comments():
            #     a=1
            #     print(comment)
            # for file in commit.files:
            #     print("      " + file.filename + "   " + str(commit.stats.total))
            #     a=1






    # for repo in githubconn.get_user().get_repos():
    #     print(repo.name)
    #     if (repo.name == "jiracharts"):
    #         commits = repo.get_commits()
    #         for commit in commits:
    #             print("   " + str(commit.commit.author.date) + "  " + commit.sha)
    #             for comment in commit.get_comments():
    #                 a=1
    #                 print(comment)
    #             for file in commit.files:
    #                 print("      " + file.filename + "   " + str(commit.stats.total))
    #                 a=1

    print(githubconn.rate_limiting)
    print(datetime.fromtimestamp(githubconn.rate_limiting_resettime))

if __name__== "__main__" :
    main()
