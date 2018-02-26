# Terminology
This section describes GraphSpace concepts and terms that are used throughout the documentation.

## Anonymous vs. Registered user
An **anonymous** user is anyone that is using GraphSpace without being logged in. An anonymous user does not have access to the REST API and may not be a member of a group. Such a user may upload graphs anonymously via a web interface. We will delete graphs that are uploaded after 30 days.

A **registered** user is anyone that is logged into GraphSpace. By logging into GraphSpace, a user has full access to the REST API and is allowed to be a member of groups. Graphs uploaded by a registered user will remain in that user's account unless explicitly deleted by the user.

## Graph visibility: Private, Shared, or Public
The visibility of a graph uploaded by a registered user can have one of three states: private, shared, or public. The visibility of a graph controls who can view the graph and interact with it upon visiting the URL associated with that graph.

### Private
When a registered user uploads a graph to GraphSpace either through the REST API or through the web interface, its visibility is **private**, i.e., only the graph owner (the user who uploaded it) can view it.
### Shared
A graph owner may share a graph with one or more groups. At this point, the graph's visibility is **shared**, i.e., all members of these groups may view the graph.
### Public
A graph owner may make the graph public through the REST API.

When an anonymous user uploads a graph, it is by default a public graph, i.e., it is accessible to any user who visits GraphSpace and knows the URL of the graph.

## Groups
A group is a collection of GraphSpace users. For example, if there are multiple researchers who are collaborating a project, a group may be created containing all of them. Another use case for a group is for all students registered in a network biology course. Once a GraphSpace user becomes a member of a group, the user may share any graph that he/she owns or a layout of such a graph with the group. Only members of that group will be able to access the graph. A user may share a graph will multiple graphs. Conversely, a user may be a member of multiple groups but share a graph only with some of these groups.

A **group owner** is the creator of the group. Any GraphSpace user can create a group by visiting the Groups page and clicking the "Create group" button. The group owner may
- Invite any GraphSpace user that has an account to be a member of their group.
- Remove any member from the group.
- Unshare any graph that has already been shared by the members of the group

A **group member** is a user who is a part of a group. (A group owner is trivially a member of the group.) A group member may
- Share a graph owned by him or her with a group.
- Unshare a previously shared graph.
- Share a layout for a previously shared graph.
- Unshare a previously shared layout.

The Groups page provides access to all the groups owned by the user (by clicking the link "Owner of") as well as the groups of which the user is a member (via the link "Member of"). The user will have the option to delete a group (if the user wowns it) or to unfollow a group (if the user is a member).

Clicking on the name of a group will open a new page that lists all the graphs in that group. This page will also contain a panels to search for nodes and edges in graphs belonging to that group and a panel to search for graphs in that group that match specific tags. If the user owns the group, there will be an interface to add or delete members. If the user is a member of group, the user can only see who are the other members of the group. Notes:
- Users must have GraphSpace accounts and be logged in in order to access group functions.
- By design, groups are private, i.e., a GraphSpace user does not have access to the names of groups of which the user is not a member.
- GraphSpace does not have a mechanism wherein a user may request to become a member of a group. All memberships must be managed by private communication.
