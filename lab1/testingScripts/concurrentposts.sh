max=10
for i in `seq 2 $max`
do
    curl --data "entry=hello $i" http://10.1.0.1/board & curl --data "entry=bye" http://10.1.0.2/board & curl --data "entry=logging on from board 10" http://10.1.0.10/board
done
