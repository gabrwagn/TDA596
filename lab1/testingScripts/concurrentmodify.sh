max=10
for i in `seq 2 $max`
do
    curl --data "entry=hello" http://10.1.0.1/board
    curl --data "entry=hello modified by 2&delete=0" http://10.1.0.2/board/0 & curl --data "entry=hello modified by 3&delete=0" http://10.1.0.3/board/0 & curl --data "entry=hello modified by 3&delete=0" http://10.1.0.3/board/0
done
