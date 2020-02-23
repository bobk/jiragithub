# jiragithub

This example code set uses the PyGitHub and jira-python libraries to perform various bits of useful interoperability between Jira and GitHub

### jiragithub-update_comments.py: 
    
- based on Jira issuekeys found in GitHub commit messages, adds GitHub commit information as comments to the associated Jira issues
- based on "transition(<transitionname>)" in the GitHub commit message, move the Jira issue found in the commit message through the specified transition

#### general notes

1) intended for low-volume environments that just want a simple mechanism to update Jira issues with info on related GitHub commits
1) for environments that are making large numbers of commits against small numbers of Jira issues, this code may not be the best answer
1) does not require a Jira plug-in, custom fields or any changes requiring elevated Jira access
1) requires:
   * a GitHub personal access token (PAT) that includes at least 'repo:' scope (no writes are made to GitHub, only reads)
   * Jira project(s) containing issues referenced in GitHub commits
   * write access (e.g. Developer role, but not Administrator role) to those Jira projects
1) areas for code enhancement:
   * store commit info in a custom field
   * add commit stats (files, lines)
   * add code to remove older comments (comments added by this code)

#### configuration file

   * general
      * jira_server - the Jira server URL to connect to
      * jira_projects - list of projects to scan for in GitHub commit messages
      * jira_comment_footprint - (for future use) key phrase in comments so we know that they were made by this code
      * github_org - GitHub organization or user ID that all repos in github_repos section are under
   * github_repos
      * <repo_name>
         * repo_lastscan_timestamp - timestamp of last run for this script for this repo (this is updated by the code itself)
         * jira_comment_format - sample comment format, using <bracketed variable names>

#### execution

1) set the GITHUB_PASSWORD env var to your GitHub PAT
1) set the JIRA_USERNAME and JIRA_PASSWORD env vars to the correct values 
   * (note that for Jira Server, you use a user name and password, for Jira Cloud, you use the user email and API token)
1) edit the config file to include your Jira server, Jira project(s), GitHub org and repos
1) run the script
1) the script should pick up all commits that contain a Jira issue in your project(s), update the comment for those issues, and optionally move the issue through the specified transition
