Udacity Project - Item Catalog

This app consists of displaying items corresponding to catalogs. Addition, Updation and Deletion can be performed on Items but Catolog list is fixed. Item description is also available
Currently no validations are added on Items,Catalogs and user email addresses.

Storage:
For storing items and catalogs sqlite database is used

Operation available:
Note: User needs to be logged in, also the user who created the item is allowed to edit/delete
New Item: /catalog/new
Edit Item: /catalog/<itemname>/edit
Delete Item: /catalog/<itemname>/delete

Authentication:
Two modes are available for user to login: Using GplusId or Register with email
Note: Currently a single user is registered with email, on running database_populater.py(discussed later)
	email: admin
	password: admin

How to Run?
To run on local machine, Vagrant machine is need
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. To download visit, https://www.vagrantup.com/downloads.
Once it is up and running follow the steps:
	1. run 'python database/database_setup.py'
		Database/database_setup.py contains basic database schema
	2. run 'python database/database_populator.py'
		Database/database_populator.py contains sample database entries.
	3. run 'python app.py'
		Server is UP on localhost:5000
	Open url 'http://localhost:5000'
	And APP is UP and Running
