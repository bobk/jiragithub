# jiragithub

This example code set uses the PyGitHub and jira-python libraries to perform various bits of useful interoperability between Jira and GitHub.
Individual scripts and the functions they perform are listed below:

### jiragithub-update_comments.py: 
    
- based on Jira issuekeys found in GitHub commit messages, adds GitHub commit information (repo, branch, message, SHA, author, stats) as comments to the associated Jira issues
- based on "transition(\<transition name>)" in the GitHub commit message, moves the Jira issue found in the commit message through the specified transition
- based on "assign(\<assignee name>)" in the GitHub commit message, assigns the Jira issue to the specified assignee

#### general notes

1) intended for low-volume environments that just want a simple mechanism to update Jira issues with info on related GitHub commits
1) for environments that are making large numbers of commits against small numbers of Jira issues, this code may not be the best answer
1) this code requires:
   * a GitHub personal access token (PAT) that includes at least 'repo:' scope (no writes are made to GitHub, only reads)
   * Jira project(s) containing issues referenced in GitHub commits
   * write access (e.g. Developer role, but not Administrator role) to those Jira projects
1) this code does not require a Jira plug-in, Jira custom fields or any other Jira changes requiring elevated Jira access
1) areas for code enhancement:
   * store commit info in a custom field
   * add commit stats per file
   * add code to remove older comments (comments added by this code)

#### configuration file

   * general
      * jira_server - the Jira server URL to connect to
      * jira_projects - list of projects to scan for in GitHub commit messages
      * jira_comment_footprint - (for future use) key phrase in comments so we know that they were made by this code
      * jira_comment_removeissuekey - do we want to remove the Jira issuekey from the comment's commit message line (not from the commit message itself in GitHub)
      * github_org - GitHub organization or user ID that all repos in github_repos section are under
      * github_baseurl - for future use
   * github_repos
      * \<repo_name>
         * jira_comment_format - sample comment format using Jira markup language, using \<bracketed variable names> that the code will replace with actual values at runtime

#### execution

1) set the GITHUB_PASSWORD env var to your GitHub PAT
1) set the JIRA_USERNAME and JIRA_PASSWORD env vars to the correct values 
   * (note that for Jira Server, you use a user name and password, for Jira Cloud, you use the user email and API token)
1) edit the config file to include your Jira server, Jira project(s), GitHub org and repos
1) run the script (note that since the script does not require any separate authentication, you can run it as a scheduled task in the background using your scheduler of choice based on your OS. Of course if you include the above env vars in your scheduled task, take precautions to protect them)
1) the script should pick up all commits that contain a Jira issue in your project(s), add comment(s) to that Jira issue for those commits, and optionally move the issue through the specified transition or change the assignee
1) the script will write the last execution time to jiragithub-runtimedata.json - delete this file to force a re-run
