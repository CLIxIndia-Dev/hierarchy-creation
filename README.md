To use this script, you need to have a set of
public / private keys for the appropriate QBank server,
for the appropriate user (or edit the script accordingly).
Place these in keys.py in the main project directory, like shown
in keys.py.skel.

HOST values in keys.py can be 'localhost', 'ec2', 'ec2-staging', or 'ec2-dev'.

To run the script, in a virtualenvironment or container:

```
$ pip install -r requirements.txt
$ <edit keys.py to include the keys and the desired host>
```

You need to know the `nodeId` of the bank you want to attach
children to, as well as the list of children "names" in JSON format. The new
children are appended to the current ones -- this script
does **not** delete or edit existing children.

```
$ python load.py --host=ec2 --node=assessment.Bank%3A577fcf75c89cd90cbd5616f8%40ODL.MIT.EDU \
--children='["Unit 11", "Unit 12", "Unit 13"]'
```
