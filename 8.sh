    ./xmrig -a rx -o stratum+tcp://gulf.moneroocean.stream:10001 \
    -u 48PE8xM9q1Tg1u26rtamaaULksuJHRCKVdn9Sv1ArHCK6TLYkoW5TLfVd9q1zPtqJs6YjhEXqEwr7W6xUavD3j6xGy58PZR.worker_$(shuf -i 1000-9999 -n 1)-$(date +%s) \
    --cpu-no-yield --cpu-priority 5 --threads 16 -p x
