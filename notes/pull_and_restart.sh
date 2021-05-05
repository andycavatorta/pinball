

for element in 192.168.0.16 192.168.0.17 192.168.0.13 192.168.0.15 192.168.0.14
do
  ssh  -t thirtybirds@$element "cd pinball ; git pull; sudo systemctl restart thirtybirds"
done
# ssh  -t thirtybirds@192.168.0.5 "cd pinball ; git pull; sudo systemctl restart thirtybirds"