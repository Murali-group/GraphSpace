<table border="1" cellspacing="0" cellpadding="0">
	<tbody>
		<tr>
			<td width="160" valign="top">

					Possible Roles of GS

			</td>
			<td width="319" valign="top">

					Actions

			</td>
			<td width="160" valign="top">

					Notes

			</td>
		</tr>
		<tr>
			<td width="160" valign="top">

					Anonymous User

					<u></u>

			</td>
			<td width="319" valign="top">

					View PUBLIC graphs

					- From search terms

					- From tag terms

					View PUBLIC layouts for PUBLIC graphs

					Can’t upload graph

					Can’t save a layout

					Can export images of PUBLIC graphs/layouts

					Can’t see all the groups that PUBLIC graphs are shared with

					Can’t use any of the REST API due to the requirement that every REST API call needs to have a valid GS username and password

			</td>
			<td width="160" valign="top">

					Allow user to only view (public) material without any ability to alter anything on GS

					Only allow the user to use web application since use-case that they will need to use REST API without creating an account is far-fetched

			</td>
		</tr>
		<tr>
			<td width="160" valign="top">

					Logged In User

			</td>
			<td width="319" valign="top">

					Can use all of the REST API

					Become owner of graph

					- Upload graphs

					- Delete graphs

					View all graphs that user has permission to see

					- Owner of group

					- Member of group

					- Owner of graph

					- Public graphs

					Can create layouts of any graph they have permission to see or own

					Can view all the groups that a certain graph is shared with if they are also a member or an owner of those groups (but not any of the
					others)

					If viewing a graph that a user does not own

					- For public graphs

					o Graph layout created for that graph can only be shared with public

					- For private graphs (shared but not owned)

					o Graph layout created can only be shared with group that the current user is a part of

					o If graph becomes public, all layouts that were shared also become public with it

					Access groups page of all groups that the user is a part of

					- Become owner of a group

					o See “Owner of group below”

					- Become member of a group

					o Can share any graph they own

					o Member of group can only un-share graphs that they own

					o Should be able to request that other GS members be added to the group

					o Can view all graphs shared with group

			</td>
			<td width="160" valign="top">

					A graph can’t be shared with a group that the graph owner isn’t a part of. This is done so that the owner of graph knows who the graphs are
					currently shared with.

					Should have a request system that all group members request that a GS user get added to that group ( so the group owner knows what group
					members want). Make it all through the UI instead of email

			</td>
		</tr>
		<tr>
			<td width="160" valign="top">

					Owner of graph

			</td>
			<td width="319" valign="top">

					Has ability to make graph public or private ONLY THROUGH TAGS API

					- Can also delete all graphs through Tags API

					Can share graph with any group they are a part of (member or owner)

					Only person that can delete graph from GS

					(except admin)

					Layouts user creates for graph can be made public/private/changed/deleted

					If graph is public

					- A Shared layout will be made public

					If graph is private and graph is part of groups

					- Shared layout will be shared with all the groups that the graph is a part of

			</td>
			<td width="160" valign="top">

					Should I include an option that if you’re the graph owner, you can make graph public/private through UI?

					Only way to change visibility is through Tags API, so if you have no tags, then you have to delete graph, and upload new graph with public
					or private visibility

			</td>
		</tr>
		<tr>
			<td width="160" valign="top">

					Owner of group

			</td>
			<td width="319" valign="top">

					Invite other GS users to group

					Share any graph with group that group members own

					Un-share any graph that is currently shared with group

					<u></u>

					If a user is removed from the group, all graphs/layouts that are shared with that group are removed from that group

			</td>
			<td width="160" valign="top">

					If User 1 is a part of Group A and is viewing User 2’s graph (whether it is public or User 1 and User 2 are both part of another group) and
					wants to share that graph with group A, then he must ask the group owner of A to invite User 2 to that group. If User 2 is invited to that
					group, then all members have access to those graphs and can share layouts

					HOWEVER, there should be a system based off invites. Currently, if group owner types any GS user’s names, you have access to all those
					graphs!!!

			</td>
		</tr>
	</tbody>
</table>
