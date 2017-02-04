1. Start your MongoDB server
2. Run flask based REST server:
    - python setup.py install
    - python MongodbEndpoint.py -p 27000 -m csvmapping.ttl
3. Run test:
    - python test_rest.py