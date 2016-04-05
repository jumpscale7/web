[actor] @dbtype:fs
	"""
	"""
    method:userregister
        """
        register a user (can be done by user itself, no existing key or login/passwd is needed)
        """
        var:name str,,name of user
        var:passwd str,,chosen passwd (will be stored hashed in DB)
        var:emails str,,comma separated list of email addresses
        var:reference str,'',reference as used in other application using this API (optional)
        var:remarks str,'',free to be used field by client
        var:config str,,free to be used field to store config information e.g. in json or xml format
        result:bool    #True if successful, False otherwise

    method:userget
        """
        get a user
        """
        var:name str,,name of user
        result:dict 

    method:getuserwithid
        """
        get a user with id
        """
        var:id str,,id of user
        result:dict

    method:getgroup
        """
        get a group with id
        """
        var:id str,,id of group
        result:dict

    method:listusers
        """
        list all users 
        """
        result:list


    method:editUser
        """
        set Groups for a user
        """
        var:username str,,name of user
        var:groups list,,name of groups @optional
        var:password str,,password for user @optional
		var:emails str,,comma seperated list of emails or list @optional
		var:domain str,,Domain of user @optional

	method:delete
		"""
		Delete a user
		"""
		var:username str,, name of the user

    method:create
		"""
		create a user
		"""
        var:username str,,name of user
		var:password str,,passwd
		var:groups str,,comma separated list of groups this user belongs to @optional
		var:emails str,,comma separated list of email addresses
		var:domain str,,domain of user
        result:bool    #True if successful, False otherwise

    method:authenticate @noauth
		"""
        authenticate and return False if not successfull
        otherwise return secret for api
		"""
        var:name str,,name
		var:secret str,,md5 or passwd
        #var:refresh bool,False,if True will recreate a new key otherwise will use last key created @optional
        result:str #is key to be used to e.g use the rest interface

    method:userexists
		"""
		"""
        var:name str,,name
        result:bool


    method:createGroup
		"""
		create a group
		"""
        var:name str,,name of group
        var:domain str,,domain of group
        var:description str,,description of group
        result:bool    #True if successful, False otherwise

    method:editGroup
		"""
		edit a group
		"""
        var:name str,,name of group
        var:domain str,,domain of group
        var:description str,,description of group
        var:users str,,list or comma seperate string of users @optional
        result:bool    #True if successful, False otherwise

    method:deleteGroup
		"""
		delete a group
		"""
        var:id str,,id of group
        result:bool    #True if successful, False otherwise

	method:usergroupsget
		"""
		return list of groups in which user is member of
		"""
		var:user str,,name of user
        result:list(str)

	method:whoami @noauth
		"""
		return username
		"""
        result:str
