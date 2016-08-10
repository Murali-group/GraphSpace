Contributing to the Project
=========================

All contributions to the project should follow the following procedure:

1. Create an issue. See the [guidelines for issues](#create-an-issue) given below for more information.
2. Create a pull request. See the [guidelines for pull request](#create-pull-request) given below for more information.

*Note:* Only the administrators of project are allowed to make changes without a pull request.

Create an Issue
---------------

If you find a bug in a project you’re using, have trouble following the documentation or have a question about the project – create an issue! 

For more information on how issues work, check out our [Issues guide](http://guides.github.com/features/issues).

#### Guidelines for Issues


 - Before creating an issue, check existing issues to see if it already
   exists. Try to avoid duplication of issues.
   
 - Be clear about what your problem is: what was the expected outcome,
   what happened instead? Detail how someone else can recreate the
   problem. Link to demos recreating the problem on things like JSFiddle
   or CodePen. Include system details like what the browser, library or
   operating system you’re using and its version.
   
 - Paste error output or logs in your issue or in a Gist. If pasting
   them in the issue, wrap it in three backticks: " ``` "  so that it
   renders nicely.
 
- Tag the issues with a proper label. 
	- feature: If you are requesting for a new feature.
	- bug: If the issue reports a bug in the current functionality.
	- question: If you have a doubt/question regarding the project.
	- enhancement: If you are requesting for an enhancement in an existing feature.
	- duplicate: If you find that your issue is duplicate of an existing issue.
	

Create Pull Request
------------

If you’re able to patch a bug or add a feature, make a pull request with the code! Once you’ve submitted a pull request the maintainer(s) can compare your branch to the existing one and decide whether or not to incorporate (pull in) your changes.

Once you’ve opened a pull request a discussion will start around your proposed changes. Other contributors and users may comment on the pull request, but ultimately the decision is made by the maintainer(s). You may be asked to make some changes to your pull request, if so, add more commits to your branch and push them – they’ll automatically go into the existing pull request.

#### Guidelines for Pull Request

- **[Fork](http://guides.github.com/activities/forking/)** the repository and clone it locally. 
- Connect your local to the original ‘upstream’ repository by adding it as a remote. 
- **Pull in changes** from ‘upstream’ often so that you stay up to date so that when you submit your pull request, merge conflicts will be less likely. See more [detailed instructions here](https://help.github.com/articles/syncing-a-fork).
- **Create a branch** for your edits. See [guidelines for naming branches](#create-a-branch) for naming conventions.
- **[Create a pull request](https://help.github.com/articles/creating-a-pull-request/)** to `develop` branch in the original 'upstream' repository i.e. `https://github.com/Murali-group/GraphSpace/`.
- Add `fixes #<issue_number>` phrase in the pull request description to add a reference to the corresponding issue. See [information here](https://github.com/blog/957-introducing-issue-mentions) for referencing issues in the pull request.
- Explain in your pull request what steps you have taken to ensure that the code change doesnt break the existing project's functionality.
- **Include screenshots** of the before and after if your changes include differences in HTML/CSS. Drag and drop the images into the body of your pull request.
- **Add comments in code** to help the maintainer to merge/understand the code change.

Create a branch
-----------------

**Use short branch names.**  

This is important, because branch names show up in the merge commits that result from accepting pull requests and should be as expressive and concise as possible.

#### Naming Conventions

- Branches used when submitting pull requests should preferably be named according to GitHub issues, e.g. 'b#1234' or 'f#1234'.
  - If the branch resolves an issue with a `bug` label then name the branch as `b#<issue_number>` e.g.: 'b#123'
  - If the branch resolves an issue with a `feature` label then name the branch as `f#<issue_number>` e.g.: 'f#123'
  - If the branch resolves an issue with a `enhancement` label then name the branch as `e#<issue_number>` e.g.: 'e#123'
  
- Otherwise, use succinct, lower-case, dash (-) delimited names, such as 'fix-warnings', 'fix-typo', etc. 


