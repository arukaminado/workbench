
''' view_memory worker '''
import os
import hashlib
import pprint

class ViewMemory(object):
    ''' ViewMemory: Generates a view for meta data on the sample '''
    dependencies = ['mem_connscan', 'mem_meta', 'mem_procdump', 'mem_pslist']

    def execute(self, input_data):
        ''' Execute the ViewMemory worker '''

        # Aggregate the output from all the memory workers, clearly this could be kewler
        output = {'tables': {}}
        for data in [input_data[key] for key in ViewMemory.dependencies]:
            for name,table in data['tables'].iteritems():
                output['tables'].update({name: table})
        return output

# Unit test: Create the class, the proper input and run the execute() method for a test
def test():
    ''' view_memory.py: Unit test'''
    
    # This worker test requires a local server running
    import zerorpc
    workbench = zerorpc.Client(timeout=300, heartbeat=60)
    workbench.connect("tcp://127.0.0.1:4242")

    # Store the sample
    data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/memory_images/exemplar4.vmem')
    with open(data_path, 'rb') as mem_file:
        raw_bytes = mem_file.read()
        md5 = hashlib.md5(raw_bytes).hexdigest()
        if not workbench.has_sample(md5):
            md5 = workbench.store_sample(open(data_path, 'rb').read(), 'exemplar4.vmem', 'mem')

    # Grab the input data
    input_data = workbench.work_request('mem_connscan', md5)
    input_data.update(workbench.work_request('mem_meta', md5))
    input_data.update(workbench.work_request('mem_procdump', md5))
    input_data.update(workbench.work_request('mem_pslist', md5))

    # Execute the worker (unit test)
    worker = ViewMemory()
    output = worker.execute(input_data)
    print '\n<<< Unit Test >>>'
    pprint.pprint(output)
    assert 'Error' not in output

    # Execute the worker (server test)
    output = workbench.work_request('view_memory', md5)
    print '\n<<< Server Test >>>'
    pprint.pprint(output)

if __name__ == "__main__":
    test()
