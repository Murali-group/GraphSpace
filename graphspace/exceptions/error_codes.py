class ErrorCodes(object):
    """
            A set of constants representing errors.  Error messages can change, but the codes will not.
            See the source for a list of all errors codes.
            Codes can be used to check for specific errors.
    """
    class Validation(object):
        UserAlreadyExists = (1000, "User with `{0}` email id already exists!")

        MethodNotAllowed = (1001, "Incoming request is not allowed")
        BadRequest = (1002, "Bad Request")
        UserPasswordMisMatch = (1003, "User/Password not recognized")
        UserNotAuthorized = (
            1004, "You are not authorized to access this resource, create an account and contact resource's owner for permission to access this resource.")
        UserNotAuthenticated = (1005, "User authentication failed")

        # Graphs API
        IsPublicNotSet = (
            1006, "`is_public` is required to be set to True when `owner_email` and `member_email` are not provided.")
        NotAllowedGraphAccess = (
            1007, "User is not authorized to access private graphs created by {0}.")
        CannotCreateGraphForOtherUser = (
            1008, "Cannot create graph with owner email = `{0}`.")
        GraphIDMissing = (1009, "Graph ID is missing.")

        # Groups API
        NotAllowedGroupAccess = (
            1010, "User is not authorized to access groups they aren't part of. Set `owner_email` or `member_email` to {0}.")
        CannotCreateGroupForOtherUser = (
            1011, "Cannot create group with owner email = `{0}`.")

        # Layouts API
        NotAllowedLayoutAccess = (
            1012, "User is not authorized to access layouts which are not shared. Set `owner_email` to {0} or `is_shared` to 1.")
        CannotCreateLayoutForOtherUser = (
            1013, "Cannot create layout with owner email = `{0}`.")
        LayoutNameAlreadyExists = (
            1014, "Layout with name `{0}` already exists.")
        GraphNameSize = (
            1015, "Graph Name cannot be more than 256 characters long.")
