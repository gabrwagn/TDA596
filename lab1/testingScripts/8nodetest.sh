for i in `seq 1 40`; do
    curl -d 'entry=node1:'${i} -X 'POST' 'http://10.1.0.1/board'
    curl -d 'entry=node2:'${i} -X 'POST' 'http://10.1.0.2/board'
    curl -d 'entry=node3:'${i} -X 'POST' 'http://10.1.0.3/board'
    curl -d 'entry=node4:'${i} -X 'POST' 'http://10.1.0.4/board'
    curl -d 'entry=node5:'${i} -X 'POST' 'http://10.1.0.5/board'
    curl -d 'entry=node6:'${i} -X 'POST' 'http://10.1.0.6/board'
    curl -d 'entry=node7:'${i} -X 'POST' 'http://10.1.0.7/board'
    curl -d 'entry=node8:'${i} -X 'POST' 'http://10.1.0.8/board'
done

