#!/usr/bin/python
#
# Create a bank hierarchy for CLIx, adding to existing children nodes
#
import json
import getopt
import sys

from utilities import AssessmentRequests

#-----------------------------------------------------------------------------


class QBankHierarchy(object):
    def __init__(self, hostname='ec2-dev', children_labels=None, node_id=''):
        if children_labels is None:
            raise TypeError('need to provide children labels')
        if node_id is None:
            raise TypeError('need to provide the node id to add children to')

        self.qbank = AssessmentRequests(username='clix-app-dev@mit.edu', host=hostname)
        self.url = '/api/v1/assessment'
        self.node_id = node_id
        self.children_labels = children_labels

        self.load()

    def _create_node(self, node_name, parent_id=None):
        # first, create the assessment bank
        banks_url = '{0}/banks'.format(self.url)
        payload = {
            'name': node_name,
        }
        node = self.qbank.post(banks_url, payload)
        node_id = node['id']
        print "Created node {0}".format(node_name)

        return node_id

    def _append_nodes_to_hierarchy(self, children_node_ids, parent_id):
        # GET the parent's current children nodes
        parent_url = '{0}/hierarchies/nodes/{1}/children'.format(self.url,
                                                                 parent_id)

        current_children = self.qbank.get(parent_url)
        children_ids = [c['id'] for c in current_children]
        children_ids += children_node_ids

        # next, add to parent in hierarchies
        node_children_url = '{0}/hierarchies/nodes/{1}/children'.format(self.url, parent_id)
        payload = {
            'ids': children_ids
        }

        self.qbank.post(node_children_url, data=payload)
        print "Linked children to {0}".format(parent_id)

    def load(self):
        """        """
        if self.children_labels is not None and self.node_id is not None:
            children_ids = []
            for label in self.children_labels:
                new_node_id = self._create_node(label)
                children_ids.append(new_node_id)
            self._append_nodes_to_hierarchy(children_ids, self.node_id)
        print "all done!"

#-----------------------------------------------------------------------------

if __name__=='__main__':
    try:
        sargs = sys.argv[1:]
        opts, args = getopt.getopt(sargs, "nch:", ["node=", "children=", "host="])
        all_opts = {}
        for o in opts:
            all_opts[o[0]] = o[1]

        hostname = 'ec2-dev'
        children_labels = None
        node_id = ''

        if '-h' in all_opts.keys():
            hostname = all_opts['-h']
        elif '--host' in all_opts:
            hostname = all_opts['--host']

        if not any(node_key in all_opts.keys() for node_key in ['-n', '--node']):
            raise TypeError('need to supply a nodeId')

        if not any(children_label in all_opts.keys() for children_label in ['-c', '--children']):
            raise TypeError('must include at least one child node label')

        if hostname not in ['ec2-dev', 'ec2-staging', 'ec2', 'localhost']:
            raise TypeError('invalid hostname')

        if '-c' in all_opts.keys():
            children_labels = all_opts['-c']
        elif '--children' in all_opts.keys():
            children_labels = json.loads(all_opts['--children'])

        if '-n' in all_opts.keys():
            node_id = all_opts['-n']
        elif '--node' in all_opts.keys():
            node_id = all_opts['--node']

        app = QBankHierarchy(hostname=hostname, children_labels=children_labels, node_id=node_id)
    except:
        # http://stackoverflow.com/questions/1000900/how-to-keep-a-python-script-output-window-open#1000968
        import sys, traceback
        print sys.exc_info()[0]
        print traceback.format_exc()
    finally:
        print "Done! Press Enter to continue ..."
        raw_input()
